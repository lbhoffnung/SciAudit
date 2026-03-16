import unittest
import subprocess
import json
import os
import tempfile

class TestCLI(unittest.TestCase):
    def run_sciaudit(self, args, expected_code=0):
        cmd = ["python", "-m", "sciaudit"] + args
        env = {**os.environ, "PYTHONPATH": ".", "PYTHONIOENCODING": "utf-8"}
        res = subprocess.run(cmd, capture_output=True, text=True, env=env, encoding="utf-8")
        if res.returncode != expected_code:
            print(f"\nCMD: {' '.join(cmd)}")
            print(f"STDOUT: {res.stdout}")
            print(f"STDERR: {res.stderr}")
        return res

    def test_json_output(self):
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write("print('hello')\n")
            fpath = f.name
        
        try:
            res = self.run_sciaudit([fpath, "--format", "json"], expected_code=0)
            self.assertEqual(res.returncode, 0)
            data = json.loads(res.stdout)
            self.assertIn("summary", data)
            self.assertEqual(data["summary"]["files_audited"], 1)
        finally:
            os.remove(fpath)

    def test_exit_codes(self):
        # Create a file with an ERROR violation (SCI-001)
        code = "scaler.fit(X); train_test_split(X, y)"
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            fpath = f.name
        
        try:
            # Default (any-error) should fail (1)
            res = self.run_sciaudit([fpath], expected_code=1)
            self.assertEqual(res.returncode, 1)

            # always-zero should pass (0)
            res = self.run_sciaudit([fpath, "--exit-code-strategy", "always-zero"], expected_code=0)
            self.assertEqual(res.returncode, 0)
        finally:
            os.remove(fpath)

    def test_baseline_filtering(self):
        code = "scaler.fit(X); train_test_split(X, y)\n"
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            fpath = f.name
        
        baseline_path = "test_baseline.json"
        try:
            # Create baseline (fails 1 but we create it anyway)
            self.run_sciaudit([fpath, "--create-baseline", baseline_path], expected_code=1)
            self.assertTrue(os.path.exists(baseline_path))

            # Run with baseline, should pass (0) because error is ignored
            res = self.run_sciaudit([fpath, "--baseline", baseline_path], expected_code=0)
            self.assertEqual(res.returncode, 0)
            
            # Verify summary shows 0 errors
            stdout = self.run_sciaudit([fpath, "--baseline", baseline_path, "--format", "json"], expected_code=0).stdout
            data = json.loads(stdout)
            self.assertEqual(data["summary"]["errors"], 0)
        finally:
            os.remove(fpath)
            if os.path.exists(baseline_path): os.remove(baseline_path)

if __name__ == "__main__":
    unittest.main()
