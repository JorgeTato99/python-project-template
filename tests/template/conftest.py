"""Carga herramientas independientes sin modificar sys.path."""

import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def bootstrap():
    spec = importlib.util.spec_from_file_location(
        "template_bootstrap", ROOT / "scripts/bootstrap.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def sample_project(tmp_path, bootstrap):
    source = tmp_path / "src" / bootstrap.TEMPLATE_PACKAGE
    source.mkdir(parents=True)
    (source / "__init__.py").write_text(
        f'from importlib.metadata import version\n\ndef get_version() -> str:\n    return version("{bootstrap.TEMPLATE_NAME}")\n',
        encoding="utf-8",
    )
    shutil.copyfile(ROOT / "README.md", tmp_path / "README.md")
    shutil.copyfile(ROOT / "CHANGELOG.md", tmp_path / "CHANGELOG.md")
    (tmp_path / "pyproject.toml").write_text(
        f'[project]\nname = "{bootstrap.TEMPLATE_NAME}"\nversion = "0.1.0"\ndescription = "Example"\n\n[project.scripts]\n{bootstrap.TEMPLATE_NAME} = "{bootstrap.TEMPLATE_PACKAGE}.__main__:main"\n',
        encoding="utf-8",
    )
    manifest = ROOT / "docs/template/manifest.json"
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    for name in [*payload["files"], "docs/template/manifest.json"]:
        destination = tmp_path / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
    return tmp_path


@pytest.fixture
def finalizer():
    spec = importlib.util.spec_from_file_location(
        "template_finalizer", ROOT / "scripts/finalize_template.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def adopted_project(bootstrap, sample_project):
    bootstrap.personalize(sample_project, "example-service", "Proyecto de prueba")
    return sample_project
