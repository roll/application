import unittest
import tempfile
from pathlib import Path

from ode.paths import Paths


class TestPaths(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_no_conflict(self):
        test_file = self.temp_path / "tempfile.txt"
        result = Paths.get_unique_destination_filepath(test_file, self.temp_path)
        self.assertEqual(result, test_file)

    def test_single_conflict(self):
        # Create same temp file to generate a conflict
        (self.temp_path / "tempfile.txt").touch()
        result = Paths.get_unique_destination_filepath(self.temp_path / "tempfile.txt", self.temp_path)

        self.assertEqual(result, self.temp_path / "tempfile(1).txt")

    def test_multiple_conflicts(self):
        # Create two temp files to see if increased to the next one
        (self.temp_path / "tempfile.txt").touch()
        (self.temp_path / "tempfile(1).txt").touch()
        result = Paths.get_unique_destination_filepath(self.temp_path / "tempfile.txt", self.temp_path)
        self.assertEqual(result, self.temp_path / "tempfile(2).txt")
