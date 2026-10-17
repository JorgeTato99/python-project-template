"""Comprueba nombres portables, preservación y personalización consistente."""

import hashlib
import tomllib

import pytest


@pytest.mark.parametrize(
    "name",
    [
        "../escape",
        "hello_world",
        "Upper",
        "3d",
        "-x",
        "x-",
        "x--y",
        "class",
        "con",
        "com1",
        "nul",
        "",
        "json",
        "argparse",
        "tomllib",
        "typing",
        "scripts",
        "tests",
    ],
)
def test_invalid_names_preserve_project(bootstrap, sample_project, name):
    original = (sample_project / "pyproject.toml").read_bytes()
    with pytest.raises(ValueError):
        bootstrap.personalize(sample_project, name)
    assert (sample_project / "pyproject.toml").read_bytes() == original
    assert (sample_project / "src" / bootstrap.TEMPLATE_PACKAGE).is_dir()


def test_dry_run_preserves_all_bytes(bootstrap, sample_project):
    def hashes():
        return {
            path: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sample_project.rglob("*")
            if path.is_file()
        }

    before = hashes()
    affected = bootstrap.personalize(sample_project, "example-service", dry_run=True)
    assert affected
    assert hashes() == before


def test_renames_namespace_metadata_and_entrypoint(bootstrap, sample_project):
    bootstrap.personalize(
        sample_project, "example-service", 'Descripción "con comillas"\ny acentos.'
    )
    project = tomllib.loads(
        (sample_project / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    assert project["name"] == "example-service"
    assert project["description"] == 'Descripción "con comillas"\ny acentos.'
    assert project["scripts"] == {"example-service": "example_service.__main__:main"}
    assert (sample_project / "src/example_service/__init__.py").is_file()
    assert not (sample_project / "src" / bootstrap.TEMPLATE_PACKAGE).exists()
    assert 'version("example-service")' in (
        sample_project / "src/example_service/__init__.py"
    ).read_text(encoding="utf-8")


def test_existing_destination_preserves_project(bootstrap, sample_project):
    (sample_project / "src/example_service").mkdir()
    with pytest.raises(ValueError, match="destino"):
        bootstrap.personalize(sample_project, "example-service")
    assert (sample_project / "src" / bootstrap.TEMPLATE_PACKAGE).is_dir()


def test_does_not_rewrite_lock_or_local_evidence(bootstrap, sample_project):
    (sample_project / "temp").mkdir()
    evidence = sample_project / "temp/source.md"
    evidence.write_text(bootstrap.TEMPLATE_NAME, encoding="utf-8")
    lock = sample_project / "uv.lock"
    lock.write_text(bootstrap.TEMPLATE_NAME, encoding="utf-8")
    bootstrap.personalize(sample_project, "example-service")
    assert evidence.read_text(encoding="utf-8") == bootstrap.TEMPLATE_NAME
    assert lock.read_text(encoding="utf-8") == bootstrap.TEMPLATE_NAME


def test_rejects_second_rename_without_corrupting_text(bootstrap, sample_project):
    bootstrap.personalize(sample_project, "a")
    original = (sample_project / "pyproject.toml").read_bytes()
    with pytest.raises(ValueError, match="ya se personalizó"):
        bootstrap.personalize(sample_project, "another-service")
    assert (sample_project / "src/a").is_dir()
    assert (sample_project / "pyproject.toml").read_bytes() == original


@pytest.mark.parametrize(
    "name", ["example-service", "python-project-template-api", "a"]
)
def test_same_personalized_name_is_idempotent(bootstrap, sample_project, name):
    bootstrap.personalize(sample_project, name)
    original = (sample_project / "pyproject.toml").read_bytes()
    assert bootstrap.personalize(sample_project, name) == []
    assert (sample_project / "pyproject.toml").read_bytes() == original


def test_same_name_can_update_description(bootstrap, sample_project):
    bootstrap.personalize(sample_project, bootstrap.TEMPLATE_NAME, "Nueva descripción")
    project = tomllib.loads(
        (sample_project / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    assert project["description"] == "Nueva descripción"


def test_rejects_empty_description(bootstrap, sample_project):
    with pytest.raises(ValueError, match="descripción"):
        bootstrap.personalize(sample_project, "example-service", " ")


def test_generates_project_readme_without_template_links(bootstrap, sample_project):
    bootstrap.personalize(sample_project, "example-service", "Mi aplicación")
    readme = (sample_project / "README.md").read_text(encoding="utf-8")
    assert "# example-service" in readme
    assert "Mi aplicación" in readme
    assert "docs/development/" in readme
    assert "docs/template/" not in readme


def test_custom_readme_requires_explicit_preservation(bootstrap, sample_project):
    path = sample_project / "README.md"
    path.write_text("Trabajo propio", encoding="utf-8")
    with pytest.raises(ValueError, match="keep-readme"):
        bootstrap.personalize(sample_project, "example-service")
    assert path.read_text(encoding="utf-8") == "Trabajo propio"
    bootstrap.personalize(sample_project, "example-service", keep_readme=True)
    assert path.read_text(encoding="utf-8") == "Trabajo propio"


def test_can_record_template_repository_url(bootstrap, sample_project):
    bootstrap.personalize(
        sample_project,
        "example-service",
        template_url="https://github.com/example/python-project-template",
    )
    assert "https://github.com/example/python-project-template" in (
        sample_project / "README.md"
    ).read_text(encoding="utf-8")


def test_changelog_starts_without_template_history(bootstrap, sample_project):
    bootstrap.personalize(sample_project, "example-service")
    changelog = (sample_project / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "example-service" in changelog
    assert "## [Unreleased]" in changelog
    assert "## [0.1.0]" not in changelog
    assert "Historial de la plantilla" not in changelog
    assert "docs/template/" not in changelog
    assert "Keep a Changelog" in changelog


def test_custom_changelog_requires_explicit_preservation(bootstrap, sample_project):
    path = sample_project / "CHANGELOG.md"
    original = b"# Mi historial\r\n\r\nCambios de python-project-template\r\n"
    path.write_bytes(original)
    before = (sample_project / "pyproject.toml").read_bytes()
    with pytest.raises(ValueError, match="keep-changelog"):
        bootstrap.personalize(sample_project, "example-service")
    assert path.read_bytes() == original
    assert (sample_project / "pyproject.toml").read_bytes() == before
    assert not (sample_project / "docs/template/state.json").exists()
    bootstrap.personalize(sample_project, "example-service", keep_changelog=True)
    assert path.read_bytes() == original


def test_repeated_bootstrap_preserves_new_project_history(bootstrap, sample_project):
    bootstrap.personalize(sample_project, "example-service")
    path = sample_project / "CHANGELOG.md"
    path.write_text("Historial propio\n", encoding="utf-8")
    assert bootstrap.personalize(sample_project, "example-service") == []
    assert path.read_text(encoding="utf-8") == "Historial propio\n"
