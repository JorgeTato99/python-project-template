"""Retira material de la plantilla de una copia personalizada y conserva respaldo."""

import argparse
import hashlib
import json
import re
import sys
import tomllib
import uuid
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_NAME = "python-project-template"
MANIFEST = "docs/template/manifest.json"
STATE = "docs/template/state.json"
SCOPES = ("docs/template/", "tests/template/")
SCRIPTS = {
    "scripts/bootstrap.py",
    "scripts/finalize_template.py",
    "scripts/update_template_manifest.py",
}


@dataclass(frozen=True)
class Plan:
    """Archivos comprobados y conflictos que impiden aplicar el cierre."""

    root: Path
    files: dict[str, str]
    conflicts: tuple[str, ...]


def digest(path: Path) -> str:
    """Calcula la huella de los bytes, sin normalizar saltos de línea."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_path(root: Path, relative: str) -> Path:
    """Rechaza escapes, enlaces y junctions antes de operar sobre una ruta."""
    parts = PurePosixPath(relative).parts
    if (
        not parts
        or ".." in parts
        or "\\" in relative
        or ":" in relative
        or relative.startswith("/")
    ):
        raise ValueError(f"Ruta no permitida: {relative}")
    candidate = root.joinpath(*parts)
    if not candidate.resolve().is_relative_to(root):
        raise ValueError(f"La ruta sale del proyecto: {relative}")
    current = root
    for part in parts:
        current /= part
        if current.is_symlink() or current.is_junction():
            raise ValueError(f"No se operará sobre enlaces o junctions: {relative}")
    return candidate


def load_manifest(root: Path) -> dict[str, str]:
    """Valida la lista curada; nunca acepta código o documentación de aplicación."""
    data = json.loads(safe_path(root, MANIFEST).read_text(encoding="utf-8"))
    if (
        not isinstance(data, dict)
        or data.get("schema") != 1
        or not isinstance(data.get("files"), dict)
    ):
        raise ValueError("El manifiesto no tiene un formato compatible.")
    files: dict[str, str] = data["files"]
    for name, value in files.items():
        if name in {MANIFEST, STATE} or not (
            name in SCRIPTS or name.startswith(SCOPES)
        ):
            raise ValueError(f"El manifiesto propone una ruta ajena: {name}")
        safe_path(root, name)
        if not isinstance(value, str) or not re.fullmatch(r"[a-f0-9]{64}", value):
            raise ValueError(f"Huella inválida: {name}")
    return files


def _references(root: Path, removed: set[str]) -> list[str]:
    """Detecta referencias persistentes a material que se retiraría."""
    tokens = (
        *SCOPES,
        *SCRIPTS,
        "scripts.bootstrap",
        "scripts.finalize_template",
        "scripts.update_template_manifest",
    )
    files = [*root.glob("*.md"), root / "pyproject.toml", root / "Makefile"]
    for folder in ("src", "scripts", "tests", "docs", ".github"):
        files.extend(
            path
            for path in (root / folder).rglob("*")
            if path.is_file()
            and path.suffix in {".py", ".md", ".toml", ".yml", ".yaml", ".txt"}
        )
    conflicts = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        if relative in removed:
            continue
        safe_path(root, relative)
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if any(token in text for token in tokens):
            conflicts.append(f"Referencia pendiente en {relative}")
    return conflicts


def plan_finalization(root: Path) -> Plan:
    """Previsualiza sin escribir; los cambios de usuario bloquean todo el cierre."""
    root = root.resolve()
    manifest = safe_path(root, MANIFEST)
    state_path = safe_path(root, STATE)
    if not manifest.is_file() or not state_path.is_file():
        raise ValueError("Ejecuta primero el bootstrap en una copia de la plantilla.")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]
    if project["name"] == TEMPLATE_NAME:
        raise ValueError(
            "La plantilla original conserva su documentación; personaliza una copia."
        )
    if (
        not isinstance(state, dict)
        or state.get("schema") != 1
        or state.get("project") != project["name"]
    ):
        raise ValueError("El estado no corresponde a este proyecto.")
    if state.get("manifest_sha256") != digest(manifest):
        raise ValueError("El manifiesto cambió después de personalizar la copia.")
    expected = load_manifest(root)
    files = {MANIFEST: digest(manifest), STATE: digest(state_path)}
    conflicts = []
    for name, value in expected.items():
        path = safe_path(root, name)
        if not path.exists():
            continue
        if not path.is_file():
            conflicts.append(f"Se esperaba un archivo: {name}")
        elif digest(path) != value:
            conflicts.append(
                f"Archivo editado; conservar o reubicar antes del cierre: {name}"
            )
        else:
            files[name] = value
    allowed_dirs = {
        str(PurePosixPath(name).parent) for name in {*expected, MANIFEST, STATE}
    }
    allowed_dirs |= {
        str(parent)
        for name in {*expected, MANIFEST, STATE}
        for parent in PurePosixPath(name).parents
    }
    for scope in SCOPES:
        folder = safe_path(root, scope.rstrip("/"))
        for path in folder.rglob("*"):
            name = path.relative_to(root).as_posix()
            safe_path(root, name)
            if path.is_dir():
                if name not in allowed_dirs and "__pycache__" not in path.parts:
                    conflicts.append(
                        f"Carpeta nueva dentro del material de plantilla: {name}"
                    )
            elif name not in expected and name not in {MANIFEST, STATE}:
                if "__pycache__" in path.parts and path.suffix in {".pyc", ".pyo"}:
                    files[name] = digest(path)
                else:
                    conflicts.append(
                        f"Archivo nuevo dentro del material de plantilla: {name}"
                    )
    conflicts.extend(_references(root, set(expected) | {MANIFEST, STATE}))
    return Plan(root, dict(sorted(files.items())), tuple(sorted(set(conflicts))))


def apply_finalization(root: Path) -> Path:
    """Mueve archivos comprobados al respaldo y restaura si falla la operación."""
    plan = plan_finalization(root)
    if plan.conflicts:
        raise ValueError("\n".join(plan.conflicts))
    backup_name = f"temp/finalization-{uuid.uuid4().hex}"
    backup = safe_path(plan.root, backup_name)
    backup.mkdir(parents=True)
    receipt = {"schema": 1, "status": "prepared", "files": plan.files}
    receipt_path = backup / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    moved: list[str] = []
    try:
        for name, expected in plan.files.items():
            source = safe_path(plan.root, name)
            if digest(source) != expected:
                raise ValueError(f"El archivo cambió durante el cierre: {name}")
            destination = backup / "files" / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            source.replace(destination)
            moved.append(name)
        receipt["status"] = "complete"
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError) as error:
        failures = []
        for name in reversed(moved):
            source = plan.root / name
            try:
                if source.exists():
                    raise FileExistsError(name)
                source.parent.mkdir(parents=True, exist_ok=True)
                (backup / "files" / name).replace(source)
            except OSError:
                failures.append(name)
        if failures:
            raise RuntimeError(
                f"Recuperación incompleta de {failures}; conserva el respaldo {backup}"
            ) from error
        raise RuntimeError(
            f"Se restauraron los archivos tras un fallo; recibo en {backup}"
        ) from error
    directories = {
        parent
        for name in moved
        for parent in (plan.root / name).parents
        if parent != plan.root and parent.is_relative_to(plan.root)
    }
    for folder in sorted(directories, key=lambda path: len(path.parts), reverse=True):
        try:
            folder.rmdir()
        except OSError:
            # Un directorio con contenido ajeno permanece intacto.
            continue
    return backup


def main() -> int:
    """Exige escoger previsualización o aplicación; no solicita confirmación interactiva."""
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--dry-run", action="store_true")
    action.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        plan = plan_finalization(ROOT)
        for name in plan.files:
            print(f"Retirar: {name}")
        if plan.conflicts:
            print("\n".join(plan.conflicts), file=sys.stderr)
            return 1
        if args.apply:
            backup = apply_finalization(ROOT)
            print(f"Cierre terminado. Respaldo local: {backup}")
            print("Verifica el proyecto con uv run --locked python scripts/check.py")
    except (OSError, ValueError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
