# python -m unittest

import unittest
from unittest.mock import MagicMock, patch
import foo
from datetime import datetime


class MyTest(unittest.TestCase):
    def test_db_name(self):
        assert foo.DB_NAME == "users.db"

    @patch("foo.datetime")
    @patch("foo.requests.post")
    def test_check_request(self, mock_post, mock_datetime):
        # Arrange
        expected_url = "https://example.com/audit"
        expected_action = "foo"
        expected_detail = "bar"
        expected_time = datetime(2000, 1, 2, 3, 4, 5)
        mock_datetime.now.return_value = expected_time

        # Act
        foo.send_audit_log(expected_action, expected_detail)

        # Assert
        mock_post.assert_called_once_with(
            expected_url, json={"action": expected_action,
                                "detail": expected_detail,
                                "timestamp": "2000-01-02T03:04:05"}
        )
        mock_datetime.now.assert_called_once()

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
        actual_response = client.get(f"/user/{expected_id}")

        # Assert
        assert actual_response.status_code == 200
        assert actual_response.json == {
            "id": expected_id, "name": expected_name}
        mock_send_audit_log.assert_called_once_with(
            "GET_USER", {"id": expected_id, "name": expected_name}
        )
        mock_sqlite3.assert_called_once_with("users.db")
        mock_cursor.execute.assert_called_once_with(
            "SELECT id, name FROM users WHERE id = ?", (expected_id,)
        )
        mock_cursor.fetchone.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("foo.sqlite3.connect")
    @patch("foo.send_audit_log")
    def test_get_user_not_exists(self, mock_send_audit_log, mock_sqlite3):
        # Arrange
        id = 99
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_sqlite3.return_value = mock_conn

        # Act
        client = foo.app.test_client()
        actual_response = client.get(f"/user/{id}")

        # Assert
        assert actual_response.status_code == 404
        assert actual_response.json == {"message": "User not found"}
        mock_sqlite3.assert_called_once_with("users.db")
        mock_send_audit_log.assert_not_called()
        mock_cursor.execute.assert_called_once_with(
            "SELECT id, name FROM users WHERE id = ?", (id,)
        )
        mock_cursor.fetchone.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("foo.sqlite3.connect")
    @patch("foo.send_audit_log")
    def test_create_user_invalid_body(self, mock_send_audit_log, mock_sqlite3):
        # Arrange
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_sqlite3.return_value = mock_conn

        # Act
        client = foo.app.test_client()
        actual_response = client.post(f"/user", json={
            "country": "taiwan",
        })

        # Assert
        assert actual_response.status_code == 400
        assert actual_response.json == {"message": "Invalid input"}
        mock_sqlite3.assert_not_called()
        mock_send_audit_log.assert_not_called()
        mock_cursor.execute.assert_not_called()
        mock_cursor.fetchone.assert_not_called()
        mock_conn.close.assert_not_called()

    @patch("foo.sqlite3.connect")
    @patch("foo.send_audit_log")
    def test_create_user_valid_body(self, mock_send_audit_log, mock_sqlite3):
        # Arrange
        expected_id = 5566
        expected_name = "grrr"

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_cursor.lastrowid = expected_id

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_sqlite3.return_value = mock_conn

        # Act
        client = foo.app.test_client()
        actual_response = client.post(f"/user", json={
            "name": "grrr",
        })

        # Assert
        assert actual_response.status_code == 201
        assert actual_response.json == {
            "id": expected_id, "name": expected_name}
        mock_send_audit_log.assert_called_once_with(
            "CREATE_USER", {"id": expected_id, "name": expected_name}
        )
        mock_sqlite3.assert_called_once_with("users.db")
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO users (name) VALUES (?)", (expected_name,)
        )
        mock_conn.close.assert_called_once()
