import tempfile
import time
from pathlib import Path
import unittest

from social_store import load_jsonl, write_jsonl, store_revision

class TestSocialStorePerf(unittest.TestCase):
    def test_load_write_jsonl_performance(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "test_perf.jsonl"
            records = [{"id": str(i), "data": "a" * 100} for i in range(100000)]

            t0 = time.time()
            write_jsonl(p, records)
            write_time = time.time() - t0

            t0 = time.time()
            loaded_records = load_jsonl(p)
            read_time = time.time() - t0

            self.assertEqual(len(loaded_records), 100000)

            # Use generous upper bounds for tests running in shared CI/environments
            self.assertLess(write_time, 5.0, "write_jsonl took too long")
            self.assertLess(read_time, 3.0, "load_jsonl took too long")

    def test_store_revision_performance(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            # Create some dummy files corresponding to DATA_FILENAMES
            from social_store import DATA_FILENAMES
            for name in DATA_FILENAMES:
                write_jsonl(p / name, [{"id": str(j), "data": "a" * 10} for j in range(1000)])

            t0 = time.time()
            for _ in range(1000):
                store_revision(p)
            revision_time = time.time() - t0

            self.assertLess(revision_time, 5.0, "store_revision took too long for 1000 iterations")

if __name__ == '__main__':
    unittest.main()
