# python -m unittest

import unittest
from unittest.mock import MagicMock, patch
import foo
from datetime import datetime


class MyTest(unittest.TestCase):
    def test_db_name(self):
        assert foo.DB_NAME == "users.db"

