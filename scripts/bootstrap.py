"""Personaliza el nombre de distribución, paquete, comandos y documentación."""

import argparse
import hashlib
import json
import keyword
import re
import sys
import tomllib
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_NAME = "python-project-template"
TEMPLATE_PACKAGE = "python_project_template"
TEMPLATE_SCRIPTS = {
    "bootstrap.py",
    "finalize_template.py",
    "update_template_manifest.py",
}
RESERVED = {"con", "prn", "aux", "nul"} | {
    f"{prefix}{number}" for prefix in ("com", "lpt") for number in range(1, 10)
}


def validate_name(name: str) -> str:
    """Restringe el nombre a un slug portable y un identificador Python válido."""
    package = name.replace("-", "_")
    if not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", name):
        raise ValueError(
            "Usa letras minúsculas, números y guiones; empieza por una letra."
        )
    if keyword.iskeyword(package) or package in RESERVED | sys.stdlib_module_names | {
        "scripts",
        "tests",
    }:
        raise ValueError("El nombre está reservado por Python, Windows o la plantilla.")
    return package


def _text_files(root: Path) -> list[Path]:
    """Selecciona fuentes de la plantilla; excluye entornos y evidencia local."""
    paths = [
        root / name
        for name in (
            "pyproject.toml",
            "README.md",
            "CONTRIBUTING.md",
            "CHANGELOG.md",
            "LICENSE",
        )
    ]
    for folder in ("src", "scripts", "tests", "docs", ".github"):
        paths.extend(
            path
            for path in (root / folder).rglob("*")
            if path.is_file()
            and path.suffix in {".py", ".md", ".toml", ".yml", ".yaml", ".txt"}
        )
    selected = sorted(
        {
            path
            for path in paths
            if path.is_file()
            and not path.relative_to(root)
            .as_posix()
            .startswith(("docs/template/", "tests/template/"))
            and not (path.parent == root / "scripts" and path.name in TEMPLATE_SCRIPTS)
        }
    )
    if any(
        path.is_symlink() or not path.resolve().is_relative_to(root.resolve())
        for path in selected
    ):
        raise ValueError(
            "La personalización requiere archivos locales dentro del proyecto."
        )
    return selected


def local_path(root: Path, relative: str) -> Path:
    """Comprueba también ancestros antes de escribir o leer activos de generación."""
    path = root / relative
    if not path.resolve().is_relative_to(root):
        raise ValueError(f"La ruta sale del proyecto: {relative}")
    current = root
    for part in Path(relative).parts:
        current /= part
        if current.is_symlink() or current.is_junction():
            raise ValueError(f"No se operará sobre enlaces o junctions: {relative}")
    return path


def personalize(
    root: Path,
    name: str,
    description: str | None = None,
    *,
    dry_run: bool = False,
    keep_readme: bool = False,
    keep_changelog: bool = False,
    template_url: str | None = None,
) -> list[Path]:
    """Actualiza una copia de la plantilla y devuelve sus rutas afectadas."""
    package = validate_name(name)
    root = root.resolve()
    manifest = root / "pyproject.toml"
    project = tomllib.loads(manifest.read_text(encoding="utf-8"))["project"]
    previous_name = project["name"]
    if previous_name != TEMPLATE_NAME and name != previous_name:
        raise ValueError(
            "La copia ya se personalizó. Para otro proyecto parte de una copia nueva."
        )
    previous_package = validate_name(previous_name)
    old_folder = local_path(root, f"src/{previous_package}")
    new_folder = local_path(root, f"src/{package}")
    if not old_folder.is_dir() or old_folder.is_symlink():
        raise ValueError("No se encontró el paquete fuente esperado.")
    if old_folder != new_folder and new_folder.exists():
        raise ValueError("El paquete destino ya existe.")
    if description is not None and not description.strip():
        raise ValueError("La descripción no puede estar vacía.")

    template_manifest = local_path(root, "docs/template/manifest.json")
    manifest_bytes = template_manifest.read_bytes()
    template = json.loads(manifest_bytes)
    source_url = template_url or template.get("source_url")
    if source_url is not None:
        parsed = urlsplit(source_url)
        if (
            parsed.scheme != "https"
            or not parsed.netloc
            or any(
                character.isspace() or character in "[]()" for character in source_url
            )
        ):
            raise ValueError("El enlace de origen debe ser una URL HTTPS sin espacios.")
    state_path = local_path(root, "docs/template/state.json")
    first_adoption = previous_name == TEMPLATE_NAME and name != TEMPLATE_NAME
    readme = local_path(root, "README.md")
    changelog = local_path(root, "CHANGELOG.md")
    project_readme = None
    project_changelog = None
    if first_adoption:
        if state_path.exists():
            raise ValueError(
                "La copia ya tiene estado de adopción; revisa su procedencia."
            )
        if not keep_readme:
            if (
                readme.exists()
                and hashlib.sha256(readme.read_bytes()).hexdigest()
                != template["template_readme_sha256"]
            ):
                raise ValueError(
                    "README.md tiene cambios. Usa --keep-readme para conservarlo."
                )
            project_readme = local_path(
                root, "docs/template/readme-project.md.in"
            ).read_text(encoding="utf-8")
            project_readme = (
                project_readme.replace("{{ project_name }}", name)
                .replace("{{ package_name }}", package)
                .replace(
                    "{{ description }}",
                    description
                    if description is not None
                    else project.get("description", "Proyecto Python."),
                )
            )
            provenance = (
                f"Base de origen: [plantilla Python]({source_url})."
                if source_url
                else "Base inicial: plantilla reutilizable para proyectos Python."
            )
            project_readme = project_readme.replace("{{ provenance }}", provenance)
        if not keep_changelog:
            if (
                changelog.exists()
                and hashlib.sha256(changelog.read_bytes()).hexdigest()
                != template["template_changelog_sha256"]
            ):
                raise ValueError(
                    "CHANGELOG.md tiene cambios. Usa --keep-changelog para conservarlo."
                )
            project_changelog = (
                local_path(root, "docs/template/changelog-project.md.in")
                .read_text(encoding="utf-8")
                .replace("{{ project_name }}", name)
            )

    original_bytes = {path: path.read_bytes() for path in _text_files(root)}
    originals = {
        path: value.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
        for path, value in original_bytes.items()
    }
    for path in originals:
        local_path(root, path.relative_to(root).as_posix())
    changes = {}
    for path, original in originals.items():
        if path == readme and (keep_readme or not first_adoption):
            continue
        if path == changelog and (keep_changelog or not first_adoption):
            continue
        updated = original
        if previous_name == TEMPLATE_NAME and name != TEMPLATE_NAME:
            updated = original.replace(TEMPLATE_NAME, name).replace(
                TEMPLATE_PACKAGE, package
            )
        if path == manifest and description is not None:
            updated, count = re.subn(
                r"(?m)^description = .*?$",
                lambda _: (
                    "description = " + json.dumps(description, ensure_ascii=False)
                ),
                updated,
                count=1,
            )
            if count != 1:
                raise ValueError("Revisa manualmente la descripción del manifiesto.")
        if updated != original:
            changes[path] = updated
    if project_readme is not None:
        changes[readme] = project_readme
    if project_changelog is not None:
        changes[changelog] = project_changelog
    if first_adoption:
        changes[state_path] = (
            json.dumps(
                {
                    "schema": 1,
                    "project": name,
                    "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                },
                indent=2,
            )
            + "\n"
        )
    # La validación ocurre antes de escribir, también para comillas y saltos de línea.
    tomllib.loads(changes.get(manifest, originals[manifest]))
    affected = list(changes)
    if old_folder != new_folder:
        affected.append(old_folder)
    if dry_run:
        return affected

    written = []
    try:
        for path, content in changes.items():
            written.append(path)
            path.write_text(content, encoding="utf-8", newline="\n")
        if old_folder != new_folder:
            old_folder.rename(new_folder)
    except OSError:
        for path in written:
            if path in originals:
                path.write_bytes(original_bytes[path])
            else:
                path.unlink(missing_ok=True)
        raise
    return affected


def main() -> None:
    """Presenta el cambio o personaliza la copia en la que reside el script."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True)
    parser.add_argument("--description")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--keep-readme",
        action="store_true",
        help="Conservar un README propio en lugar de generar la portada inicial.",
    )
    parser.add_argument(
        "--keep-changelog",
        action="store_true",
        help="Conservar un historial propio en lugar de generar uno vacío.",
    )
    parser.add_argument(
        "--template-url",
        help="URL HTTPS del repositorio de origen, cuando esté publicado.",
    )
    args = parser.parse_args()
    try:
        affected = personalize(
            ROOT,
            args.name,
            args.description,
            dry_run=args.dry_run,
            keep_readme=args.keep_readme,
            keep_changelog=args.keep_changelog,
            template_url=args.template_url,
        )
    except (OSError, ValueError) as error:
        parser.error(str(error))
    for path in affected:
        print(path.relative_to(ROOT))
    if not args.dry_run:
        print(
            "Personalización terminada. Ejecuta uv lock, uv sync --locked y uv run --locked ruff format src scripts tests."
        )
        print(
            "Cuando termines la adopción: python scripts/finalize_template.py --dry-run y después --apply."
        )


if __name__ == "__main__":
    main()
