import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from publication.models import Publication
from users.models import User


class RelationshipArchitectureTest(unittest.TestCase):
    def test_user_and_publication_are_linked(self):
        self.assertTrue(hasattr(User, "publications"))
        self.assertTrue(hasattr(Publication, "author"))
        self.assertIn("user_id", Publication.__table__.columns.keys())


if __name__ == "__main__":
    unittest.main()
