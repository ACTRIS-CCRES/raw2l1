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
def root_data_dir(root_dir):
    path = root_dir / "tests" / "data"
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    return path


@pytest.fixture()
def root_input_dir(root_data_dir):
    path = root_data_dir / "input"
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    return path


@pytest.fixture()
def root_output_dir(root_data_dir):
    path = root_data_dir / "output"
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    return path


@pytest.fixture()
def tmp_dir(tmp_path):
    return tmp_path


@pytest.fixture()
def root_conf_dir(root_data_dir):
    path = root_data_dir / "conf"
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    return path


# instruments dir
# -------------------------------------------------------------------------------------
@pytest.fixture()
def instr_dir_hatpro(root_input_dir):
    return root_input_dir / "rpg_hatpro"


@pytest.fixture()
def instr_dir_chm15k(root_input_dir):
    return root_input_dir / "lufft_chm15k"


@pytest.fixture()
def instr_dir_vaisala_cl(root_input_dir):
    return root_input_dir / "vaisala_cl"
