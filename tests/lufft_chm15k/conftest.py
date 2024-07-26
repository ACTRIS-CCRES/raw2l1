import pytest


@pytest.fixture()
def chm15k_input_dir(input_dir):
    return input_dir / "lufft_chm15k"


@pytest.fixture()
def chm15k_conf_dir(chm15k_input_dir):
    return chm15k_input_dir / "conf"


@pytest.fixture()
def chm15k_output_dir(output_dir):
    path = output_dir / "lufft_chm15k"
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    return path
