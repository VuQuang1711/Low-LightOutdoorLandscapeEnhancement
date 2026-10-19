import os
import tempfile
import unittest
from pathlib import Path

from src.config import AppConfig, PROJECT_ROOT


class TestAppConfigPaths(unittest.TestCase):

    def test_relative_config_path_resolves_from_project_root(self):
        original_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                config = AppConfig(Path("config") / "config.yaml")
            finally:
                os.chdir(original_cwd)

        self.assertEqual(
            config.config_path,
            (PROJECT_ROOT / "config" / "config.yaml").resolve()
        )
        self.assertEqual(config.app_version, "1.0.0")
        dataset_dir = config.get_dataset_dir()
        self.assertTrue(
            dataset_dir == PROJECT_ROOT or PROJECT_ROOT in dataset_dir.parents
        )


if __name__ == "__main__":
    unittest.main()
