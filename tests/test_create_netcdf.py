import datetime as dt
import logging
import os
import unittest
from unittest import mock

import raw2l1.tools.create_netcdf as cnc


class DummyConf:
    def __init__(self, values):
        self._values = values

    def get(self, section, option):
        return self._values[(section, option)]


class DummyNcDataset:
    def close(self):
        return None


class DummyXrDataset:
    def __init__(self):
        self.output = None

    def sel(self, time):
        return self

    def to_netcdf(self, output_file):
        self.output = output_file

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None


class DummyTempDir:
    def __init__(self, path):
        self.path = path
        self.entered = False
        self.exited = False

    def __enter__(self):
        self.entered = True
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exited = True
        return None


class TestCreateNetcdfTempCleanup(unittest.TestCase):
    def setUp(self):
        self.conf = DummyConf(
            {
                ("conf", "filter_day"): True,
                ("conf", "date"): dt.datetime(2026, 3, 5),
                ("conf", "output"): "/tmp/final-output.nc",
                ("conf", "netcdf_format"): "NETCDF4",
            }
        )
        self.logger = logging.getLogger("raw2l1-test-create-netcdf")

    def test_remove_temp_file_after_filtering(self):
        tmp_dir = "/tmp/raw2l1-temp-test-dir"
        expected_tmp_file = os.path.join(tmp_dir, "raw2l1_filter_day.nc")
        temp_dir_cm = DummyTempDir(tmp_dir)
        xr_dataset = DummyXrDataset()

        with (
            mock.patch.object(cnc, "create_netcdf_global"),
            mock.patch.object(cnc, "create_netcdf_dim"),
            mock.patch.object(cnc, "create_netcdf_variables"),
            mock.patch(
                "raw2l1.tools.create_netcdf.tempfile.TemporaryDirectory",
                return_value=temp_dir_cm,
            ),
            mock.patch(
                "raw2l1.tools.create_netcdf.nc.Dataset",
                return_value=DummyNcDataset(),
            ) as dataset_mock,
            mock.patch(
                "raw2l1.tools.create_netcdf.xr.open_dataset", return_value=xr_dataset
            ),
        ):
            status = cnc.create_netcdf(self.conf, {}, self.logger)

        self.assertEqual(status, 0)
        self.assertTrue(temp_dir_cm.entered)
        self.assertTrue(temp_dir_cm.exited)
        dataset_mock.assert_called_once_with(
            expected_tmp_file,
            "w",
            format="NETCDF4",
        )
        self.assertEqual(xr_dataset.output, "/tmp/final-output.nc")

    def test_remove_temp_file_if_creation_fails(self):
        tmp_dir = "/tmp/raw2l1-temp-test-dir"
        temp_dir_cm = DummyTempDir(tmp_dir)

        with (
            mock.patch.object(cnc, "create_netcdf_global"),
            mock.patch.object(cnc, "create_netcdf_dim"),
            mock.patch.object(cnc, "create_netcdf_variables"),
            mock.patch(
                "raw2l1.tools.create_netcdf.tempfile.TemporaryDirectory",
                return_value=temp_dir_cm,
            ),
            mock.patch(
                "raw2l1.tools.create_netcdf.nc.Dataset",
                side_effect=OSError("boom"),
            ),
        ):
            with self.assertRaises(SystemExit):
                cnc.create_netcdf(self.conf, {}, self.logger)

        self.assertTrue(temp_dir_cm.entered)
        self.assertTrue(temp_dir_cm.exited)

    def test_remove_temp_file_if_variable_creation_fails(self):
        tmp_dir = "/tmp/raw2l1-temp-test-dir"
        temp_dir_cm = DummyTempDir(tmp_dir)

        with (
            mock.patch.object(cnc, "create_netcdf_global"),
            mock.patch.object(cnc, "create_netcdf_dim"),
            mock.patch.object(
                cnc,
                "create_netcdf_variables",
                side_effect=RuntimeError("broken variable step"),
            ),
            mock.patch(
                "raw2l1.tools.create_netcdf.tempfile.TemporaryDirectory",
                return_value=temp_dir_cm,
            ),
            mock.patch(
                "raw2l1.tools.create_netcdf.nc.Dataset",
                return_value=DummyNcDataset(),
            ),
        ):
            with self.assertRaises(RuntimeError):
                cnc.create_netcdf(self.conf, {}, self.logger)

        self.assertTrue(temp_dir_cm.entered)
        self.assertTrue(temp_dir_cm.exited)


if __name__ == "__main__":
    unittest.main()
