from raw2l1.raw2l1 import raw2l1


def test_conversion(chm15k_conf_dir, chm15k_input_dir, chm15k_output_dir, tmp_path):
    """Test reader for UKMO Nimbus ceilometer data."""
    date = "20160514"
    conf_file = (chm15k_conf_dir / "conf_lufft_chm15k-ukmo_eprofile.ini").open()
    input_file = str(
        chm15k_input_dir
        / "metoffice-jenoptick-chm15k-nimbus-ceilometer_aldergrove_201605140000.nc"
    )
    output_file = str(chm15k_output_dir / "chm15k_ukmo.nc")
    log_file = str(tmp_path / "raw2l1.log")

    ret_code = raw2l1(
        date, conf_file, [input_file], output_file, verbose="debug", log_file=log_file
    )

    assert ret_code == 0, "chm15k ukmo"
