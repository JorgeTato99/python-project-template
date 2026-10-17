"""Verifica la API pública y la instalación fuera del directorio fuente."""

import subprocess
import sys
from importlib.metadata import version

from python_project_template import get_version
from python_project_template.__main__ import main


def test_reports_installed_distribution_version():
    assert get_version() == version("python-project-template")


def test_default_command_displays_help(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["python-project-template"])
    main()
    assert "--version" in capsys.readouterr().out


def test_module_runs_outside_repository(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "python_project_template", "--version"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == get_version()
