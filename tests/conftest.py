"""Fixtures for pytest."""

from pathlib import Path

import pytest


# main dirs
# -------------------------------------------------------------------------------------
@pytest.fixture()
def root_dir(request):
    path = request.config.rootdir
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    return Path(path)


@pytest.fixture()
def data_dir(root_dir):
    path = root_dir / "tests" / "data"
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    return path


@pytest.fixture()
def input_dir(data_dir):
    path = data_dir / "input"
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    return path


@pytest.fixture()
def output_dir(data_dir):
    path = data_dir / "output"
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    return path


@pytest.fixture()
def conf_dir(data_dir):
    path = data_dir / "conf"
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    return path


@pytest.fixture()
def tmp_dir(data_dir):
    path = data_dir / "tmp"
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    return path


# instruments dir
# -------------------------------------------------------------------------------------
@pytest.fixture()
def instr_dir_hatpro(input_dir):
    return input_dir / "rpg_hatpro"
