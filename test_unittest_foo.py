# python -m unittest

import unittest
from unittest.mock import MagicMock, patch
import foo

class MyTest(unittest.TestCase):
    def test_db_name(self):
        assert foo.DB_NAME == "users.db"

    # [Q1] Please complete the test that gets the response from the Flask API.
    @patch("foo.send_audit_log")
    def test_get_user_not_exists(self, mock_send_audit_log):
        # Arrange
        id = 999
        
        # Act
        # HINT: How do I create a test client for the foo service?
        #     : https://tedboy.github.io/flask/generated/generated/flask.Flask.test_client.html#flask-flask-test-client
        client = foo.app.test_client()
        actual_response = "FIXME"

        # Assert
        assert actual_response.status_code == 404
        assert actual_response.json == {"message": "User not found"}
        # HINT: What is assert_not_called()
        #     : https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_not_called
        mock_send_audit_log.assert_not_called()

    # [Q2] Please complete the test to get the response from the Flask API, 
    # and assert what you think is most important.
    @patch("foo.sqlite3.connect")
    @patch("foo.send_audit_log")
    def test_get_user_exists(self, mock_send_audit_log, mock_sqlite3):
        # Arrange
        expected_id = 99
        expected_name = "Alice"
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [expected_id, expected_name]

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_sqlite3.return_value = mock_conn

        # Act
        client = foo.app.test_client()
        
        # Assert

    # [Q3] Break down the test scenarios you consider important.
    # You don't need to implement the test content.

    # [Bonus] Can you verify the request body as well?
    @patch("foo.datetime")
    @patch("foo.requests.post")
    def test_check_request(self, mock_post, mock_datetime):
        action = "foo"
        detail = "bar"

        foo.send_audit_log(action, detail)