"""Actualiza el inventario del material retirable al mantener la plantilla original."""

import argparse
import hashlib
import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_NAME = "python-project-template"


def safe_file(path: Path) -> Path:
    """Comprueba destino y ancestros antes de leer o normalizar archivos."""
    if not path.resolve().is_relative_to(ROOT):
        raise ValueError(f"La ruta sale del proyecto: {path}")
    current = ROOT
    for part in path.relative_to(ROOT).parts:
        current /= part
        if current.is_symlink() or current.is_junction():
            raise ValueError(f"No se operará sobre enlaces o junctions: {path}")
    return path


def main() -> None:
    """Registra hashes de autor; nunca se ejecuta para limpiar una copia derivada."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-url",
        help="URL HTTPS de la plantilla una vez publicado el repositorio.",
    )
    args = parser.parse_args()
    project = tomllib.loads(
        safe_file(ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    state = safe_file(ROOT / "docs/template/state.json")
    if project["name"] != TEMPLATE_NAME or state.exists():
        raise ValueError("El inventario sólo se mantiene en la plantilla original.")
    files = [
        ROOT / "scripts" / name
        for name in (
            "bootstrap.py",
            "finalize_template.py",
            "update_template_manifest.py",
        )
    ]
    for folder in ("docs/template", "tests/template"):
        files.extend(
            path
            for path in (ROOT / folder).rglob("*")
            if path.is_file()
            and path.suffix in {".md", ".json", ".py", ".in"}
            and path.name not in {"manifest.json", "state.json"}
        )
    for path in files:
        safe_file(path)
    target = safe_file(ROOT / "docs/template/manifest.json")
    readme = safe_file(ROOT / "README.md")
    changelog = safe_file(ROOT / "CHANGELOG.md")
    previous = json.loads(target.read_text(encoding="utf-8")) if target.exists() else {}
    for path in [*files, readme, changelog]:
        path.write_text(
            path.read_text(encoding="utf-8"), encoding="utf-8", newline="\n"
        )
    payload = {
        "schema": 1,
        "template": TEMPLATE_NAME,
        "source_url": args.source_url or previous.get("source_url"),
        "template_readme_sha256": hashlib.sha256(
            (ROOT / "README.md").read_bytes()
        ).hexdigest(),
        "template_changelog_sha256": hashlib.sha256(changelog.read_bytes()).hexdigest(),
        "files": {
            path.relative_to(ROOT).as_posix(): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in sorted(files)
        },
    }
    target.write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"Inventario actualizado: {len(files)} archivos.")


if __name__ == "__main__":
    main()
