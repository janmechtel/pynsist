import unittest
import os
import platform
import subprocess
import glob

from testpath.tempdir import TemporaryDirectory
from testpath import assert_isfile
from nsist.pypi import fetch_pypi_wheels

class TestLocalWheels(unittest.TestCase):
    def test_matching_one_pattern(self):
        with TemporaryDirectory() as td1:
            subprocess.call(['pip', 'wheel', 'astsearch==0.1.2', '-w', td1])

            with TemporaryDirectory() as td2:
                fetch_pypi_wheels([], [os.path.join(td1, '*.whl')], td2, platform.python_version(), 64)

                assert_isfile(os.path.join(td2, 'astsearch.py'))
                assert_isfile(os.path.join(td2, 'astsearch-0.1.2.dist-info', 'METADATA'))

                assert_isfile(os.path.join(td2, 'astcheck.py'))
                self.assertTrue(glob.glob(os.path.join(td2, '*.dist-info')))

    def test_duplicate_wheel_files_raise(self):
        with TemporaryDirectory() as td1:
            subprocess.call(['pip', 'wheel', 'astsearch==0.1.2', '-w', td1])

            with TemporaryDirectory() as td2:
                with self.assertRaisesRegex(ValueError, 'wheel distribution astsearch already included'):
                    fetch_pypi_wheels(['astsearch==0.1.2'], [os.path.join(td1, '*.whl')], td2, platform.python_version(), 64)

    def test_invalid_wheel_file_raise(self):
        with TemporaryDirectory() as td1:
            open(os.path.join(td1, 'notawheel.txt'), 'w+')

            with TemporaryDirectory() as td2:
                with self.assertRaisesRegex(ValueError, 'Invalid wheel file name: notawheel.txt'):
                    fetch_pypi_wheels([], [os.path.join(td1, '*')], td2, platform.python_version(), 64)

    def test_incompatible_plateform_wheel_file_raise(self):
        with TemporaryDirectory() as td1:
            open(os.path.join(td1, 'incompatiblewheel-1.0.0-py2.py3-none-linux_x86_64.whl'), 'w+')

            with TemporaryDirectory() as td2:
                with self.assertRaisesRegex(ValueError, '{0} does not support Windows platform'
                .format('incompatiblewheel-1.0.0-py2.py3-none-linux_x86_64.whl')):
                    fetch_pypi_wheels([], [os.path.join(td1, '*.whl')], td2, platform.python_version(), 64)

    def test_incompatible_python_wheel_file_raise(self):
        with TemporaryDirectory() as td1:
            open(os.path.join(td1, 'incompatiblewheel-1.0.0-py26-none-any.whl'), 'w+')

            with TemporaryDirectory() as td2:
                with self.assertRaisesRegex(ValueError, '{0} does not support Python {1}'
                .format('incompatiblewheel-1.0.0-py26-none-any.whl', platform.python_version())):
                    fetch_pypi_wheels([], [os.path.join(td1, '*.whl')], td2, platform.python_version(), 64)
