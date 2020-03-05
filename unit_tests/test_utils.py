import unittest
from verification_ui.main import app
from verification_ui.utils.content_negotiation_utils import request_wants_json
from verification_ui.utils.lock_check import check_correct_lock_user
from unittest import mock


class TestContentNegotiationUtil(unittest.TestCase):

    def setup_method(self, method):
        self.app = app.test_client()

    def test_content_negotiation_util_returns_false_for_text_html(self):
        with self.app:
            self.app.get('/', headers=[('Accept', 'text/html')])
            assert request_wants_json() is False

    def test_content_negotiation_util_returns_true_for_application_json(self):
        with self.app:
            self.app.get('/', headers=[('Accept', 'application/json')])
            assert request_wants_json() is True


class TestLockCheck(unittest.TestCase):

    def setup_method(self, method):
        self.app = app.test_client()

    @mock.patch('verification_ui.utils.lock_check.VerificationAPI.get_item')
    def test_check_correct_lock_user_returns_true(self, mock_api):
        mock_api.return_value = {'staff_id': 'TestUser'}
        item_id = 666
        with app.app_context():
            result = check_correct_lock_user(item_id, 'TestUser')
            self.assertEqual(result, True)

    @mock.patch('verification_ui.utils.lock_check.VerificationAPI.get_item')
    def test_check_correct_lock_user_returns_false(self, mock_api):
        mock_api.return_value = {'staff_id': 'PinkHaze'}
        item_id = 666
        with app.app_context():
            result = check_correct_lock_user(item_id, 'TestUser')
            self.assertEqual(result, False)
