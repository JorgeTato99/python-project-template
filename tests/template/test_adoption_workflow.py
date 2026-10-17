"""Ejecuta la adopción y el cierre de una copia real con las herramientas elegidas."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.integration
def test_generated_project_passes_checks_after_finalization(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    for folder in ("src", "scripts", "tests", "docs", ".github"):
        shutil.copytree(
            ROOT / folder,
            project / folder,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    for name in (
        "pyproject.toml",
        "uv.lock",
        ".python-version",
        "README.md",
        "LICENSE",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "CHANGELOG.md",
        "CODE_OF_CONDUCT.md",
        "Makefile",
        ".pre-commit-config.yaml",
        ".gitignore",
        ".gitattributes",
        ".editorconfig",
        ".env.example",
    ):
        shutil.copyfile(ROOT / name, project / name)
    environment = dict(os.environ)
    environment.pop("VIRTUAL_ENV", None)
    environment.update(
        {
            "UV_PROJECT_ENVIRONMENT": str(project / ".venv"),
            "UV_PYTHON": sys.executable,
            "UV_LINK_MODE": "copy",
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8",
        }
    )
    commands = [
        [
            sys.executable,
            "scripts/bootstrap.py",
            "--name",
            "adopted-service",
            "--description",
            "Aplicación de prueba",
        ],
        ["uv", "lock"],
        ["uv", "sync", "--locked"],
        ["uv", "run", "--locked", "ruff", "format", "src", "scripts", "tests"],
        [
            "uv",
            "run",
            "--locked",
            "python",
            "scripts/finalize_template.py",
            "--dry-run",
        ],
        ["uv", "run", "--locked", "python", "scripts/finalize_template.py", "--apply"],
        ["uv", "run", "--locked", "python", "scripts/check.py"],
    ]
    own_notes = project / "docs/development/application.md"
    own_notes.write_text("Información propia del proyecto\n", encoding="utf-8")
    for command in commands:
        result = subprocess.run(
            command,
            cwd=project,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            check=False,
        )
        assert result.returncode == 0, (
            " ".join(command) + "\n" + result.stdout + "\n" + result.stderr
        )
    assert own_notes.read_text(encoding="utf-8") == "Información propia del proyecto\n"
    assert not (project / "docs/template").exists()
    assert not (project / "tests/template").exists()
    assert not (project / "scripts/bootstrap.py").exists()
    assert (project / "scripts/check.py").exists()
    assert (project / "docs/development/pruebas.md").exists()
    changelog = (project / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "adopted-service" in changelog
    assert "## [Unreleased]" in changelog
    assert "## [0.1.0]" not in changelog
    assert "docs/template/" not in changelog
