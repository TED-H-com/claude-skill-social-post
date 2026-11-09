import tempfile
from pathlib import Path
import unittest
import os
import shutil
from social_store import load_jsonl, write_jsonl, store_revision, exclusive_store_lock, commit_records

class TestSocialStore(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="social-store-test-")
        self.data_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_and_write_jsonl(self):
        path = self.data_dir / "test.jsonl"
        records = [{"a": 1}, {"b": 2}]
        write_jsonl(path, records)
        loaded = load_jsonl(path)
        self.assertEqual(records, loaded)

    def test_load_jsonl_invalid(self):
        path = self.data_dir / "invalid.jsonl"
        path.write_text("invalid json\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            load_jsonl(path)

        path.write_text('"not an object"\n', encoding="utf-8")
        with self.assertRaises(ValueError):
            load_jsonl(path)

    def test_load_jsonl_nonexistent(self):
        path = self.data_dir / "nonexistent.jsonl"
        self.assertEqual(load_jsonl(path), [])

    def test_load_jsonl_empty_lines(self):
        path = self.data_dir / "empty.jsonl"
        path.write_text("\n   \n\n", encoding="utf-8")
        self.assertEqual(load_jsonl(path), [])

    def test_store_revision(self):
        # empty
        rev1 = store_revision(self.data_dir)
        write_jsonl(self.data_dir / "posts.jsonl", [{"post_id": "1"}])
        rev2 = store_revision(self.data_dir)
        self.assertNotEqual(rev1, rev2)

    def test_commit_records(self):
        expected_revision = store_revision(self.data_dir)
        path = self.data_dir / "posts.jsonl"
        records = {path: [{"post_id": "2"}]}

        new_rev = commit_records(records, data_dir=self.data_dir, expected_revision=expected_revision)
        self.assertNotEqual(expected_revision, new_rev)

        # Test stale revision error
        with self.assertRaises(RuntimeError):
            commit_records(records, data_dir=self.data_dir, expected_revision=expected_revision)

    def test_commit_records_rollback(self):
        expected_revision = store_revision(self.data_dir)
        path = self.data_dir / "posts.jsonl"
        write_jsonl(path, [{"post_id": "original"}])
        expected_revision = store_revision(self.data_dir)

        records = {path: [{"post_id": "new"}]}

        original_copyfile = shutil.copyfile
        def fake_copyfile(src, dst):
            raise OSError("fake error")

        shutil.copyfile = fake_copyfile
        try:
            with self.assertRaises(OSError):
                commit_records(records, data_dir=self.data_dir, expected_revision=expected_revision)
        finally:
            shutil.copyfile = original_copyfile

        loaded = load_jsonl(path)
        self.assertEqual(loaded[0]["post_id"], "original")

    def test_commit_records_rollback_missing(self):
        expected_revision = store_revision(self.data_dir)
        path = self.data_dir / "posts.jsonl"

        records = {path: [{"post_id": "new"}]}

        original_copyfile = shutil.copyfile
        def fake_copyfile(src, dst):
            raise OSError("fake error")

        shutil.copyfile = fake_copyfile
        try:
            with self.assertRaises(OSError):
                commit_records(records, data_dir=self.data_dir, expected_revision=expected_revision)
        finally:
            shutil.copyfile = original_copyfile

        self.assertFalse(path.exists())

    def test_exclusive_store_lock(self):
        with exclusive_store_lock(self.data_dir):
            self.assertTrue((self.data_dir / ".write.lock").exists())
        self.assertFalse((self.data_dir / ".write.lock").exists())

    def test_exclusive_store_lock_timeout(self):
        lock_dir = self.data_dir / ".write.lock"
        os.mkdir(lock_dir)

        with self.assertRaises(TimeoutError):
            with exclusive_store_lock(self.data_dir, timeout_seconds=0.1):
                pass

        os.rmdir(lock_dir)

    def test_exclusive_store_lock_rmdir_not_found(self):
        with exclusive_store_lock(self.data_dir):
            os.rmdir(self.data_dir / ".write.lock")

        self.assertFalse((self.data_dir / ".write.lock").exists())

if __name__ == '__main__':
    unittest.main()
