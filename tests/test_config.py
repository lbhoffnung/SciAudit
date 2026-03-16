import unittest
import os
import tempfile
from sciaudit.core.config import load_config, Config

class TestConfig(unittest.TestCase):
    def test_default_config(self):
        config = Config()
        self.assertEqual(config.rules, {})
        self.assertEqual(config.ignore_paths, [])
        self.assertFalse(config.should_ignore("src/main.py"))

    def test_load_basic_config(self):
        yaml_content = """
rules:
  SCI-002: warning
  SCI-008: off
paths:
  ignore:
    - "venv/"
    - ".git"
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, ".sciaudit.yml")
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(yaml_content)
            
            config = load_config(tmpdir)
            
            self.assertEqual(config.rules["SCI-002"], "warning")
            self.assertEqual(config.rules["SCI-008"], "off")
            self.assertTrue(config.should_ignore("venv/lib/site-packages"))
            self.assertTrue(config.should_ignore(".git/config"))
            self.assertFalse(config.should_ignore("src/main.py"))

    def test_profiles(self):
        # Strict profile
        config_strict = load_config(profile="strict")
        self.assertEqual(config_strict.rules["SCI-002"], "error")
        self.assertEqual(config_strict.rules["SCI-013"], "error")

        # Relaxed profile
        config_relaxed = load_config(profile="relaxed")
        self.assertEqual(config_relaxed.rules["SCI-002"], "info")
        self.assertEqual(config_relaxed.rules["SCI-013"], "off")

    def test_baseline_logic(self):
        config = Config()
        config.baseline = [
            {"rule_id": "SCI-001", "file": "src/bad.py", "line": 10}
        ]
        
        # Should be in baseline
        self.assertTrue(config.is_in_baseline({"rule_id": "SCI-001", "file": "src/bad.py", "line": 10}))
        
        # Different line
        self.assertFalse(config.is_in_baseline({"rule_id": "SCI-001", "file": "src/bad.py", "line": 11}))
        
        # Different rule
        self.assertFalse(config.is_in_baseline({"rule_id": "SCI-002", "file": "src/bad.py", "line": 10}))

if __name__ == "__main__":
    unittest.main()
