"""Comprueba que el cierre conserva el trabajo de usuario y puede recuperarse."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def snapshot(root):
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file()
        and "temp" not in path.relative_to(root).parts
        and "__pycache__" not in path.parts
    }


def test_manifest_matches_original_assets(finalizer):
    payload = json.loads((ROOT / finalizer.MANIFEST).read_text(encoding="utf-8"))
    for name, value in payload["files"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == value


def test_preview_preserves_bytes(finalizer, adopted_project):
    before = snapshot(adopted_project)
    plan = finalizer.plan_finalization(adopted_project)
    assert not plan.conflicts
    assert finalizer.MANIFEST in plan.files
    assert snapshot(adopted_project) == before


def test_cli_preview_preserves_bytes(adopted_project):
    before = snapshot(adopted_project)
    result = subprocess.run(
        [
            sys.executable,
            str(adopted_project / "scripts/finalize_template.py"),
            "--dry-run",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Retirar:" in result.stdout
    assert snapshot(adopted_project) == before


def test_apply_keeps_application_code_and_documents(finalizer, adopted_project):
    preserved = {
        "src/example_service/feature.py": "VALUE = 7\n",
        "tests/test_business.py": "def test_business():\n    assert True\n",
        "docs/development/notes.md": "Notas propias\n",
        "SECURITY.md": "Contacto del proyecto\n",
    }
    for name, content in preserved.items():
        path = adopted_project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    before_readme = (adopted_project / "README.md").read_bytes()
    backup = finalizer.apply_finalization(adopted_project)
    assert backup.is_relative_to(adopted_project / "temp")
    assert (backup / "files/docs/template/manifest.json").is_file()
    assert not (adopted_project / "docs/template").exists()
    assert not (adopted_project / "tests/template").exists()
    assert not (adopted_project / "scripts/bootstrap.py").exists()
    assert not (adopted_project / "scripts/finalize_template.py").exists()
    assert (adopted_project / "README.md").read_bytes() == before_readme
    for name, content in preserved.items():
        assert (adopted_project / name).read_text(encoding="utf-8") == content
    with pytest.raises(ValueError):
        finalizer.apply_finalization(adopted_project)


@pytest.mark.parametrize("before_bootstrap", [True, False])
def test_edited_template_asset_blocks_all_mutation(
    finalizer, bootstrap, sample_project, before_bootstrap
):
    path = sample_project / "docs/template/python-project-anti-patterns.md"
    if not before_bootstrap:
        bootstrap.personalize(sample_project, "example-service")
    path.write_text(
        path.read_text(encoding="utf-8") + "\nTrabajo propio\n", encoding="utf-8"
    )
    if before_bootstrap:
        bootstrap.personalize(sample_project, "example-service")
    before = snapshot(sample_project)
    with pytest.raises(ValueError, match="editado"):
        finalizer.apply_finalization(sample_project)
    assert snapshot(sample_project) == before
    assert not (sample_project / "temp").exists()


@pytest.mark.parametrize(
    "name", ["docs/template/own-notes.md", "tests/template/test_custom.py"]
)
def test_unknown_content_blocks_cleanup(finalizer, adopted_project, name):
    path = adopted_project / name
    path.write_text("Trabajo propio\n", encoding="utf-8")
    before = snapshot(adopted_project)
    with pytest.raises(ValueError, match="nuevo"):
        finalizer.apply_finalization(adopted_project)
    assert snapshot(adopted_project) == before


def test_pending_reference_blocks_cleanup(finalizer, adopted_project):
    (adopted_project / "README.md").write_text(
        "[Guía](docs/template/adopcion.md)\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="Referencia pendiente"):
        finalizer.apply_finalization(adopted_project)


def test_changed_manifest_is_rejected(finalizer, adopted_project):
    path = adopted_project / finalizer.MANIFEST
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="manifiesto cambió"):
        finalizer.apply_finalization(adopted_project)


@pytest.mark.parametrize(
    "target", ["src/user.py", "../outside.md", "/outside.md", "C:/outside.md"]
)
def test_manifest_cannot_expand_scope(finalizer, bootstrap, sample_project, target):
    path = sample_project / finalizer.MANIFEST
    data = json.loads(path.read_text(encoding="utf-8"))
    data["files"][target] = "0" * 64
    path.write_text(json.dumps(data), encoding="utf-8")
    bootstrap.personalize(sample_project, "example-service")
    before = snapshot(sample_project)
    with pytest.raises(ValueError):
        finalizer.apply_finalization(sample_project)
    assert snapshot(sample_project) == before


def test_original_template_is_protected(finalizer, sample_project):
    manifest = sample_project / finalizer.MANIFEST
    (sample_project / finalizer.STATE).write_text(
        json.dumps(
            {
                "schema": 1,
                "project": "python-project-template",
                "manifest_sha256": finalizer.digest(manifest),
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="original"):
        finalizer.apply_finalization(sample_project)


def test_failure_rolls_back_without_losing_backup(
    finalizer, adopted_project, monkeypatch
):
    before = snapshot(adopted_project)
    replace = Path.replace
    calls = 0

    def injected(path, target):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("Fallo simulado")
        return replace(path, target)

    monkeypatch.setattr(Path, "replace", injected)
    with pytest.raises(RuntimeError, match="restauraron"):
        finalizer.apply_finalization(adopted_project)
    assert snapshot(adopted_project) == before
    assert list((adopted_project / "temp").glob("finalization-*/receipt.json"))


def test_symlink_is_rejected(finalizer, adopted_project, tmp_path):
    outside = tmp_path / "outside.txt"
    outside.write_text("Conservar", encoding="utf-8")
    link = adopted_project / "docs/template/link.md"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("Este entorno no permite crear enlaces simbólicos.")
    with pytest.raises(ValueError):
        finalizer.apply_finalization(adopted_project)
    assert outside.read_text(encoding="utf-8") == "Conservar"
