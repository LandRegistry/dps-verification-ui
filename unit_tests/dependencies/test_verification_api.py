import unittest
import requests
import json
from unittest import mock
from unittest.mock import MagicMock
from werkzeug.datastructures import ImmutableMultiDict
from requests.exceptions import HTTPError, ConnectionError, Timeout
from verification_ui.main import app
from verification_ui.dependencies.verification_api import VerificationAPI
from verification_ui.exceptions import ApplicationError


def use_test_request_context(func):
    def run_with_context(*args, **kwargs):
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                return func(*args, **kwargs)

    return run_with_context


class TestVerificationAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.item_id = 1
        self.staff_id = 'cs999jb'
        self.error_msg = 'Test error message'
        self.decline_reason = 'Registration number'
        self.decline_advice = 'Reapply with a new number'
        self.close_requester = 'hmlr'
        self.close_reason = 'This is a test reason'
        self.note_text = 'This is a test note'

    @mock.patch("requests.Session.get")
    @use_test_request_context
    def test_get_worklist(self, mock_get):
        mock_get.return_value.json.return_value = [{'case_id': 1}]
        mock_get.return_value.status_code = 200

        verification_api = VerificationAPI()
        response = verification_api.get_worklist()

        self.assertEqual(response, [{'case_id': 1}])

    @mock.patch("requests.Session.get")
    @use_test_request_context
    def test_get_worklist_http_error(self, mock_get):
        mock_get.side_effect = HTTPError(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.get_worklist()

        self.assertEqual(context.exception.message,
                         'Received the following response from verification_api: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E401')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.get")
    @use_test_request_context
    def test_get_worklist_connection_error(self, mock_get):
        mock_get.side_effect = ConnectionError(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.get_worklist()

        self.assertEqual(context.exception.message,
                         'Encountered an error connecting to verification_api: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E402')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.get")
    @use_test_request_context
    def test_get_worklist_timeout_error(self, mock_get):
        mock_get.side_effect = Timeout(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.get_worklist()

        self.assertEqual(context.exception.message,
                         'Connection to verification_api timed out: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E403')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.get")
    @use_test_request_context
    def test_get_item(self, mock_get):
        mock_get.return_value.json.return_value = [{'case_id': self.item_id}]
        mock_get.return_value.status_code = 200

        verification_api = VerificationAPI()
        response = verification_api.get_item(self.item_id)

        self.assertEqual(response, [{'case_id': self.item_id}])

    @mock.patch("requests.Session.get")
    @use_test_request_context
    def test_get_item_http_error(self, mock_get):
        mock_get.side_effect = HTTPError(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.get_item(self.item_id)

        self.assertEqual(context.exception.message,
                         'Received the following response from verification_api: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E401')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.get")
    @use_test_request_context
    def test_get_item_connection_error(self, mock_get):
        mock_get.side_effect = ConnectionError(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.get_item(self.item_id)

        self.assertEqual(context.exception.message,
                         'Encountered an error connecting to verification_api: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E402')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.get")
    @use_test_request_context
    def test_get_item_timeout_error(self, mock_get):
        mock_get.side_effect = Timeout(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.get_item(self.item_id)

        self.assertEqual(context.exception.message,
                         'Connection to verification_api timed out: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E403')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_approve_worklist_item(self, mock_post):
        mock_post.return_value.json.return_value = {'case_id': self.item_id, 'staff_id': self.staff_id,
                                                    'status_updated': True}
        mock_post.return_value.status_code = 201

        verification_api = VerificationAPI()
        response = verification_api.approve_worklist_item(self.item_id, self.staff_id)

        self.assertEqual(response, {'case_id': self.item_id, 'staff_id': self.staff_id,
                                    'status_updated': True})

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_approve_worklist_item_http_error(self, mock_post):
        mock_post.side_effect = HTTPError(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.approve_worklist_item(self.item_id, self.staff_id)

        self.assertEqual(context.exception.message,
                         'Received the following response from verification_api: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E401')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_approve_worklist_item_connection_error(self, mock_post):
        mock_post.side_effect = ConnectionError(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.approve_worklist_item(self.item_id, self.staff_id)

        self.assertEqual(context.exception.message,
                         'Encountered an error connecting to verification_api: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E402')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_approve_worklist_item_timeout_error(self, mock_post):
        mock_post.side_effect = Timeout(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.approve_worklist_item(self.item_id, self.staff_id)

        self.assertEqual(context.exception.message,
                         'Connection to verification_api timed out: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E403')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_decline_worklist_item(self, mock_post):
        mock_post.return_value.json.return_value = {'case_id': self.item_id, 'staff_id': self.staff_id,
                                                    'status_updated': True, 'reason': self.decline_reason,
                                                    'advice': self.decline_advice}
        mock_post.return_value.status_code = 201

        verification_api = VerificationAPI()
        response = verification_api.decline_worklist_item(self.item_id, self.staff_id, self.decline_reason,
                                                          self.decline_advice)

        self.assertEqual(response, {'case_id': self.item_id, 'staff_id': self.staff_id,
                                    'status_updated': True, 'reason': self.decline_reason,
                                    'advice': self.decline_advice})

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_decline_worklist_item_http_error(self, mock_post):
        mock_post.side_effect = HTTPError(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.decline_worklist_item(self.item_id, self.staff_id, self.decline_reason,
                                                   self.decline_advice)

        self.assertEqual(context.exception.message,
                         'Received the following response from verification_api: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E401')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_decline_worklist_item_connection_error(self, mock_post):
        mock_post.side_effect = ConnectionError(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.decline_worklist_item(self.item_id, self.staff_id, self.decline_reason,
                                                   self.decline_advice)

        self.assertEqual(context.exception.message,
                         'Encountered an error connecting to verification_api: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E402')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_decline_worklist_item_timeout_error(self, mock_post):
        mock_post.side_effect = Timeout(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.decline_worklist_item(self.item_id, self.staff_id, self.decline_reason,
                                                   self.decline_advice)

        self.assertEqual(context.exception.message,
                         'Connection to verification_api timed out: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E403')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_close_account(self, mock_post):
        mock_post.return_value.json.return_value = {"staff_id": self.staff_id,
                                                    "requester": self.close_requester,
                                                    "case_id": self.item_id,
                                                    "status_updated": True,
                                                    "close_detail": self.close_reason
                                                    }
        mock_post.return_value.status_code = 201

        verification_api = VerificationAPI()
        response = verification_api.close_account(self.item_id, self.staff_id, self.close_requester,
                                                  self.close_reason)

        self.assertEqual(response, {"staff_id": self.staff_id,
                                    "requester": self.close_requester,
                                    "case_id": self.item_id,
                                    "status_updated": True,
                                    "close_detail": self.close_reason
                                    })

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_close_account_http_error(self, mock_post):
        mock_post.side_effect = HTTPError(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.close_account(self.item_id, self.staff_id, self.close_requester,
                                           self.close_reason)

        self.assertEqual(context.exception.message,
                         'Received the following response from verification_api: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E401')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_close_account_connection_error(self, mock_post):
        mock_post.side_effect = ConnectionError(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.close_account(self.item_id, self.staff_id, self.close_requester,
                                           self.close_reason)

        self.assertEqual(context.exception.message,
                         'Encountered an error connecting to verification_api: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E402')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_close_account_timeout_error(self, mock_post):
        mock_post.side_effect = Timeout(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.close_account(self.item_id, self.staff_id, self.close_requester,
                                           self.close_reason)

        self.assertEqual(context.exception.message,
                         'Connection to verification_api timed out: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E403')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.get")
    @use_test_request_context
    def test_get_decline_reasons(self, mock_get):
        mock_get.return_value.json.return_value = [{'decline_reason': 'test',
                                                    'decline_text': 'This is a test decline reason'}]
        mock_get.return_value.status_code = 200

        verification_api = VerificationAPI()
        response = verification_api.get_decline_reasons()

        self.assertEqual(response, [{'decline_reason': 'test',
                                     'decline_text': 'This is a test decline reason'}])

    @mock.patch("requests.Session.get")
    @use_test_request_context
    def test_get_decline_reasons_http_error(self, mock_get):
        mock_get.side_effect = HTTPError(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.get_decline_reasons()

        self.assertEqual(context.exception.message,
                         'Received the following response from verification_api: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E401')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.get")
    @use_test_request_context
    def test_get_decline_reasons_connection_error(self, mock_get):
        mock_get.side_effect = ConnectionError(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.get_decline_reasons()

        self.assertEqual(context.exception.message,
                         'Encountered an error connecting to verification_api: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E402')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.get")
    @use_test_request_context
    def test_get_decline_reasons_timeout_error(self, mock_get):
        mock_get.side_effect = Timeout(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.get_decline_reasons()

        self.assertEqual(context.exception.message,
                         'Connection to verification_api timed out: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E403')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_add_note(self, mock_post):
        response_message = 'Note added for user {}'.format(self.item_id)
        mock_post.return_value.json.return_value = {"message": response_message}
        mock_post.return_value.status_code = 201

        verification_api = VerificationAPI()
        response = verification_api.add_note(self.item_id, self.staff_id, self.note_text)

        self.assertEqual(response, {"message": response_message})

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_add_note_http_error(self, mock_post):
        mock_post.side_effect = HTTPError(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.add_note(self.item_id, self.staff_id, self.note_text)

        self.assertEqual(context.exception.message,
                         'Received the following response from verification_api: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E401')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_add_note_connection_error(self, mock_post):
        mock_post.side_effect = ConnectionError(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.add_note(self.item_id, self.staff_id, self.note_text)

        self.assertEqual(context.exception.message,
                         'Encountered an error connecting to verification_api: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E402')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_add_note_timeout_error(self, mock_post):
        mock_post.side_effect = Timeout(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.add_note(self.item_id, self.staff_id, self.note_text)

        self.assertEqual(context.exception.message,
                         'Connection to verification_api timed out: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E403')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_perform_search(self, mock_post):
        mock_post.return_value.json.return_value = [{'case_id': 1}]
        mock_post.return_value.status_code = 200

        search_entries = {
            "first_name": "test",
            "last_name": "",
            "organisation_name": "",
            "email": "",
        }

        verification_api = VerificationAPI()
        response = verification_api.perform_search(search_entries)

        self.assertEqual(response, [{'case_id': 1}])
        self.assertEqual(mock_post.call_count, 1)

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_perform_search_http_error(self, mock_post):
        mock_post.side_effect = HTTPError(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            search_entries = {
                "first_name": "test",
                "last_name": "",
                "organisation_name": "",
                "email": "",
            }

            verification_api = VerificationAPI()
            verification_api.perform_search(search_entries)

        self.assertEqual(context.exception.message,
                         'Received the following response from verification_api: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E401')
        self.assertEqual(context.exception.http_code, 500)
        self.assertEqual(mock_post.call_count, 1)

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_perform_search_connection_error(self, mock_post):
        mock_post.side_effect = ConnectionError(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            search_entries = {
                "first_name": "test",
                "last_name": "",
                "organisation_name": "",
                "email": "",
            }

            verification_api = VerificationAPI()
            verification_api.perform_search(search_entries)

        self.assertEqual(context.exception.message,
                         'Encountered an error connecting to verification_api: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E402')
        self.assertEqual(context.exception.http_code, 500)
        self.assertEqual(mock_post.call_count, 1)

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_perform_search_timeout_error(self, mock_post):
        mock_post.side_effect = Timeout(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            search_entries = {
                "first_name": "test",
                "last_name": "",
                "organisation_name": "",
                "email": "",
            }

            verification_api = VerificationAPI()
            verification_api.perform_search(search_entries)

        self.assertEqual(context.exception.message,
                         'Connection to verification_api timed out: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E403')
        self.assertEqual(context.exception.http_code, 500)
        self.assertEqual(mock_post.call_count, 1)

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_update_user_details(self, mock_post):
        response_message = 'Updated user details for ID: {}'.format(self.item_id)
        mock_post.return_value.json.return_value = {"message": response_message}
        mock_post.return_value.status_code = 201

        response = VerificationAPI().update_user_details(self.item_id, {})

        self.assertEqual(response, {"message": response_message})

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_update_user_details_http_error(self, mock_post):
        mock_post.side_effect = HTTPError(self.error_msg)

        with self.assertRaises(ApplicationError) as c:
            VerificationAPI().update_user_details(self.item_id, {})

        self.assertEqual(c.exception.message,
                         'Received the following response from verification_api: {}'.format(self.error_msg))
        self.assertEqual(c.exception.code, 'E401')
        self.assertEqual(c.exception.http_code, 500)
        self.assertEqual(mock_post.call_count, 1)

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_update_user_details_connection_error(self, mock_post):
        mock_post.side_effect = ConnectionError(self.error_msg)

        with self.assertRaises(ApplicationError) as c:
            VerificationAPI().update_user_details(self.item_id, {})

        self.assertEqual(c.exception.message,
                         'Encountered an error connecting to verification_api: {}'.format(self.error_msg))
        self.assertEqual(c.exception.code, 'E402')
        self.assertEqual(c.exception.http_code, 500)
        self.assertEqual(mock_post.call_count, 1)

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_update_user_details_timeout_error(self, mock_post):
        mock_post.side_effect = Timeout(self.error_msg)

        with self.assertRaises(ApplicationError) as c:
            VerificationAPI().update_user_details(self.item_id, {})

        self.assertEqual(c.exception.message,
                         'Connection to verification_api timed out: {}'.format(self.error_msg))
        self.assertEqual(c.exception.code, 'E403')
        self.assertEqual(c.exception.http_code, 500)
        self.assertEqual(mock_post.call_count, 1)

    @mock.patch("requests.Session.get")
    @use_test_request_context
    def test_get_dataset_activity(self, mock_get):
        case_id = 999
        mock_get.return_value.json.return_value = ['test']
        mock_get.return_value.status_code = 200

        verification_api = VerificationAPI()
        response = verification_api.get_dataset_activity(case_id)

        mock_get.assert_called_once()
        self.assertEqual(response, ['test'])

    @mock.patch("requests.Session.get")
    @use_test_request_context
    def test_get_dataset_activity_http_error(self, mock_get):
        case_id = 999
        mock_get.side_effect = HTTPError(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.get_dataset_activity(case_id)

        mock_get.assert_called_once()
        self.assertEqual(context.exception.message,
                         'Received the following response from verification_api: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E401')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.get")
    @use_test_request_context
    def test_get_dataset_activity_connection_error(self, mock_get):
        case_id = 999
        mock_get.side_effect = ConnectionError(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.get_dataset_activity(case_id)

        mock_get.assert_called_once()
        self.assertEqual(context.exception.message,
                         'Encountered an error connecting to verification_api: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E402')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.get")
    @use_test_request_context
    def test_get_dataset_activity_timeout_error(self, mock_get):
        case_id = 999
        mock_get.side_effect = Timeout(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.get_dataset_activity(case_id)

        mock_get.assert_called_once()
        self.assertEqual(context.exception.message,
                         'Connection to verification_api timed out: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E403')
        self.assertEqual(context.exception.http_code, 500)

    @use_test_request_context
    def test_update_dataset_access(self):
        case_id = 999
        staff_id = 'cs999pb'

        # this is mocking the data that would come from calling verification_api.get_user_dataset_access()
        current_access = [{'name': 'nps', 'licences': {'nps': {'agreed': True}, 'nps_sample': {'agreed': False}}}]

        # Updated access is flask's request.form which is an ImmutableMultiDict data structure with .getlist method
        updated_access = ImmutableMultiDict([('nps', 'nps_sample')])

        verification_api = VerificationAPI()
        verification_api._request = MagicMock()

        verification_api.update_dataset_access(case_id, staff_id, current_access, updated_access)

        expected_data = {
            'staff_id': staff_id,
            'licences': [
                {
                    'licence_id': 'nps',
                    'agreed': False
                },
                {
                    'licence_id': 'nps_sample',
                    'agreed': True
                }
            ]
        }

        # There is logic in update_dataset_access to create an array of licences with true/false agreed states
        # Ensure that the HTTP _request method is being called with correct data based on this logic
        verification_api._request.assert_called_with(
            uri='case/999/update_dataset_access'.format(case_id),
            data=json.dumps(expected_data)
        )

    @use_test_request_context
    def test_update_dataset_access_only_update_if_needed(self):
        case_id = 999
        staff_id = 'cs999pb'

        # this is mocking the data that would come from calling verification_api.get_user_dataset_access()
        current_access = [{'name': 'nps', 'licences': {'nps': {'agreed': True}, 'nps_sample': {'agreed': False}}}]

        # Updated access is flask's request.form which is an ImmutableMultiDict data structure with .getlist method
        updated_access = ImmutableMultiDict([('nps', 'nps'), ('nps', 'nps_sample')])

        verification_api = VerificationAPI()
        verification_api._request = MagicMock()

        verification_api.update_dataset_access(case_id, staff_id, current_access, updated_access)

        # Expect that if you already have nps then don't try to update again
        expected_data = {
            'staff_id': staff_id,
            'licences': [
                {
                    'licence_id': 'nps_sample',
                    'agreed': True
                }
            ]
        }

        # There is logic in update_dataset_access to create an array of licences with true/false agreed states
        # Ensure that the HTTP _request method is being called with correct data based on this logic
        verification_api._request.assert_called_with(
            uri='case/999/update_dataset_access'.format(case_id),
            data=json.dumps(expected_data)
        )

    @use_test_request_context
    def test_update_dataset_access_no_update(self):
        case_id = 999
        staff_id = 'cs999pb'

        # this is mocking the data that would come from calling verification_api.get_user_dataset_access()
        current_access = [{'name': 'nps', 'licences': {'nps': {'agreed': True}, 'nps_sample': {'agreed': True}}}]

        # Updated access is flask's request.form which is an ImmutableMultiDict data structure with .getlist method
        updated_access = ImmutableMultiDict([('nps', 'nps'), ('nps', 'nps_sample')])

        verification_api = VerificationAPI()
        verification_api._request = MagicMock()

        result = verification_api.update_dataset_access(case_id, staff_id, current_access, updated_access)

        # If nothing to update should return empty dict() and don't call verification-api
        self.assertEqual(result, {})
        verification_api._request.assert_not_called()

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_update_dataset_access_http_error(self, mock_post):
        case_id = 999
        staff_id = 'cs999pb'
        current_access = [{'name': 'nps', 'licences': {'nps': {'agreed': True}, 'nps_sample': {'agreed': False}}}]
        updated_access = ImmutableMultiDict([('nps', 'nps_sample')])
        mock_post.side_effect = HTTPError(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.update_dataset_access(case_id, staff_id, current_access, updated_access)

        mock_post.assert_called_once()
        self.assertEqual(context.exception.message,
                         'Received the following response from verification_api: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E401')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_update_dataset_access_connection_error(self, mock_post):
        case_id = 999
        staff_id = 'cs999pb'
        current_access = [{'name': 'nps', 'licences': {'nps': {'agreed': True}, 'nps_sample': {'agreed': False}}}]
        updated_access = ImmutableMultiDict([('nps', 'nps_sample')])
        mock_post.side_effect = ConnectionError(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.update_dataset_access(case_id, staff_id, current_access, updated_access)

        mock_post.assert_called_once()
        self.assertEqual(context.exception.message,
                         'Encountered an error connecting to verification_api: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E402')
        self.assertEqual(context.exception.http_code, 500)

    @mock.patch("requests.Session.post")
    @use_test_request_context
    def test_update_dataset_access_timeout_error(self, mock_post):
        case_id = 999
        staff_id = 'cs999pb'
        current_access = [{'name': 'nps', 'licences': {'nps': {'agreed': True}, 'nps_sample': {'agreed': False}}}]
        updated_access = ImmutableMultiDict([('nps', 'nps_sample')])
        mock_post.side_effect = Timeout(self.error_msg)

        with self.assertRaises(ApplicationError) as context:
            verification_api = VerificationAPI()
            verification_api.update_dataset_access(case_id, staff_id, current_access, updated_access)

        mock_post.assert_called_once()
        self.assertEqual(context.exception.message,
                         'Connection to verification_api timed out: {}'.format(self.error_msg))
        self.assertEqual(context.exception.code, 'E403')
        self.assertEqual(context.exception.http_code, 500)
