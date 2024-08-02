import pytest


@pytest.fixture()
def vaisala_cl_input_dir(input_dir):
    return input_dir / "vaisala_cl"


@pytest.fixture()
def vaisala_cl_conf_dir(vaisala_cl_input_dir):
    return vaisala_cl_input_dir / "conf"


@pytest.fixture()
def vaisala_cl_output_dir(output_dir):
    path = output_dir / "lufft_chm15k"
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    return path
