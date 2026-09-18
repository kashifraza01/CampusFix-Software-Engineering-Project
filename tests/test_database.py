import os
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

import database  # noqa: E402


class CampusFixDatabaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_path = database.DB_PATH
        cls.temp_dir = tempfile.TemporaryDirectory()
        database.DB_PATH = Path(cls.temp_dir.name) / "test_campusfix.db"
        database.initialize_database()

    @classmethod
    def tearDownClass(cls):
        database.DB_PATH = cls.original_path
        cls.temp_dir.cleanup()

    def test_demo_login(self):
        user = database.authenticate("student@campusfix.local", "student123")
        self.assertIsNotNone(user)
        self.assertEqual(user["role"], "User")

    def test_register_and_submit_complaint(self):
        ok, _ = database.register_user("Test User", "test@example.com", "secret1")
        self.assertTrue(ok)
        user = database.authenticate("test@example.com", "secret1")
        complaint_id = database.add_complaint(
            user["id"], "Projector not working", "Classroom Equipment", "2nd Floor", "High", "The projector does not power on during class."
        )
        self.assertGreater(complaint_id, 0)
        rows = database.get_user_complaints(user["id"])
        self.assertEqual(rows[0]["status"], "Submitted")

    def test_admin_update(self):
        user = database.authenticate("student@campusfix.local", "student123")
        cid = database.add_complaint(user["id"], "WiFi issue", "IT / Network", "Library", "Medium", "WiFi disconnects every few minutes in the reading area.")
        database.update_complaint(cid, "In Progress", "Network Support", "Router access point will be checked.")
        item = database.get_complaint(cid)
        self.assertEqual(item["status"], "In Progress")
        self.assertEqual(item["assigned_to"], "Network Support")


if __name__ == "__main__":
    unittest.main()
