"""Comprueba límites de filesystem y recuperación de la personalización."""

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("kind", ["symlink", "junction"])
def test_bootstrap_rejects_external_source_directory(bootstrap, sample_project, kind):
    source = sample_project / "src"
    outside = sample_project.parent / (sample_project.name + "-external")
    assert outside.resolve().is_relative_to(sample_project.parent.resolve())
    source.rename(outside)
    try:
        if kind == "junction":
            if sys.platform != "win32":
                pytest.skip("Junction es específico de Windows.")
            import _winapi

            _winapi.CreateJunction(str(outside), str(source))
        else:
            source.symlink_to(outside, target_is_directory=True)
    except OSError:
        outside.rename(source)
        pytest.skip("El entorno no permite crear este enlace.")
    with pytest.raises(ValueError):
        bootstrap.personalize(sample_project, "example-service")
    assert (outside / bootstrap.TEMPLATE_PACKAGE).is_dir()
    assert not (outside / "example_service").exists()


def test_bootstrap_rollback_preserves_crlf_bytes(
    bootstrap, sample_project, monkeypatch
):
    manifest = sample_project / "pyproject.toml"
    original = manifest.read_bytes().replace(b"\n", b"\r\n")
    manifest.write_bytes(original)
    rename = Path.rename

    def injected(path, target):
        if path.name == bootstrap.TEMPLATE_PACKAGE:
            raise OSError("Fallo simulado")
        return rename(path, target)

    monkeypatch.setattr(Path, "rename", injected)
    with pytest.raises(OSError, match="simulado"):
        bootstrap.personalize(sample_project, "example-service")
    assert manifest.read_bytes() == original
    assert not (sample_project / "docs/template/state.json").exists()


@pytest.mark.parametrize(
    "name", ["README.md", "CHANGELOG.md", "docs/template/manifest.json"]
)
def test_inventory_update_does_not_write_through_links(
    sample_project, name, monkeypatch
):
    spec = importlib.util.spec_from_file_location(
        "template_inventory", ROOT / "scripts/update_template_manifest.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", sample_project)
    monkeypatch.setattr(sys, "argv", ["update_template_manifest.py"])
    path = sample_project / name
    path.unlink()
    outside = sample_project.parent / (sample_project.name + "-outside.txt")
    outside.write_text("Conservar\r\n", encoding="utf-8", newline="")
    before = outside.read_bytes()
    try:
        path.symlink_to(outside)
    except OSError:
        pytest.skip("El entorno no permite crear enlaces simbólicos.")
    with pytest.raises(ValueError):
        module.main()
    assert outside.read_bytes() == before
