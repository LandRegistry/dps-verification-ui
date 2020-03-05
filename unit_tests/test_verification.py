import pytest
import unittest
import os
import json
from unittest import mock
from urllib.parse import urlparse
from verification_ui.main import app
from verification_ui.exceptions import ApplicationError
from verification_ui.views import verification


dir_ = os.path.dirname(os.path.abspath(__file__))
personal_item_data = open(os.path.join(dir_, 'data/personal_item.json'), 'r').read()


@pytest.mark.skip(reason="This is an integration test and is being affected by openresty")
class TestVerification(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.test_personal_item = json.loads(personal_item_data)
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['LOGIN_DISABLED'] = 'True'

        with self.app as c:
            with c.session_transaction() as session:
                session['username'] = 'test'

    def tearDown(self):
        app.config['WTF_CSRF_ENABLED'] = True

    @mock.patch('verification_ui.views.verification.build_row')
    @mock.patch('verification_ui.views.verification.VerificationAPI')
    def test_get_worklist(self, mock_api, mock_build):
        mock_api.return_value.get_worklist.return_value = self.test_personal_item
        mock_build.return_value = [{'text': '01/01/2019'}, {'text': 'UK Personal'}, {'text': 'Mr Test User'},
                                   {'html': '<a href="/verification/worklist/1">View details</a>'}]

        response = self.app.get('/verification/worklist')
        data = response.data.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('Worklist', data)
        self.assertIn('Mr Test User', data)

    @mock.patch('verification_ui.views.verification.VerificationAPI')
    def test_get_worklist_error(self, mock_api):
        mock_api.return_value.get_worklist.side_effect = ApplicationError('Test error')

        response = self.app.get('/verification/worklist')
        data = response.data.decode()

        self.assertEqual(response.status_code, 500)
        self.assertIn('Something went wrong when retrieving the worklist.', data)

    @mock.patch('verification_ui.views.verification.format_note_metadata')
    @mock.patch('verification_ui.views.verification.build_details_table')
    @mock.patch('verification_ui.views.verification.VerificationAPI')
    def test_get_item_personal(self, mock_api, mock_build, mock_note):
        mock_api.return_value.get_item.return_value = self.test_personal_item
        mock_api.return_value.get_decline_reasons.return_value = [{'decline_reason': 'test',
                                                                   'decline_text': 'This is a test decline reason'}]
        mock_build.return_value = [{'key': {'text': 'Full Name'}, 'value': {'text': 'Mr Test User'},
                                    'actions': {'items': []}},
                                   {'key': {'text': 'Address'}, 'value': {'html': '1 The Street'},
                                    'actions': {'items': []}},
                                   {'key': {'text': 'Telephone Number'}, 'value': {'text': '07527111333'},
                                    'actions': {'items': []}},
                                   {'key': {'text': 'Account Type'}, 'value': {'text': 'UK Personal'},
                                    'actions': {'items': []}}]
        mock_note.return_value = 'Added by testuser on 01/01/2019 12:12:12'

        response = self.app.get('/verification/worklist/1')
        data = response.data.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('Application information', data)
        self.assertIn('07527111333', data)

    @mock.patch('verification_ui.views.verification.VerificationAPI')
    def test_get_item_error(self, mock_api):
        mock_api.return_value.get_item.side_effect = ApplicationError('Test error')

        response = self.app.get('/verification/worklist/3')
        data = response.data.decode()

        self.assertEqual(response.status_code, 500)
        self.assertIn('Something went wrong when requesting the application details.', data)

    @mock.patch('verification_ui.views.verification.VerificationAPI')
    def test_approve_worklist_item(self, _):
        test_form_data = {'item_id': '1'}

        response = self.app.post('/verification/worklist/approve', data=test_form_data, follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, '/verification/worklist')

    @mock.patch('verification_ui.views.verification.VerificationAPI')
    def test_approve_worklist_item_error(self, mock_api):
        mock_api.return_value.approve_worklist_item.side_effect = ApplicationError('Test error')
        test_form_data = {'item_id': '1'}

        response = self.app.post('/verification/worklist/approve', data=test_form_data, follow_redirects=False)
        data = response.data.decode()

        self.assertEqual(response.status_code, 500)
        self.assertIn('Something went wrong when approving the application.', data)

    @mock.patch('verification_ui.views.verification.VerificationAPI')
    def test_decline_worklist_item(self, _):
        test_form_data = {'item_id': '1', 'decline_reason': 'Registration number'}

        response = self.app.post('/verification/worklist/decline', data=test_form_data, follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, '/verification/worklist')

    @mock.patch('verification_ui.views.verification.VerificationAPI')
    def test_decline_worklist_item_error(self, mock_api):
        mock_api.return_value.decline_worklist_item.side_effect = ApplicationError('Test error')
        test_form_data = {'item_id': '1', 'decline_reason': 'Registration number'}

        response = self.app.post('/verification/worklist/decline', data=test_form_data, follow_redirects=False)
        data = response.data.decode()

        self.assertEqual(response.status_code, 500)
        self.assertIn('Something went wrong when declining the application.', data)

    @mock.patch('verification_ui.views.verification.VerificationAPI')
    def test_close_account(self, _):
        test_form_data = {'item_id': '1', 'close_requester': 'hmlr', 'close_reason': 'Test close reason'}

        response = self.app.post('/verification/worklist/close', data=test_form_data, follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, '/verification/worklist')

    @mock.patch('verification_ui.views.verification.VerificationAPI')
    def test_close_account_error(self, mock_api):
        mock_api.return_value.close_account.side_effect = ApplicationError('Test error')
        test_form_data = {'item_id': '1', 'close_requester': 'hmlr', 'close_reason': 'Test close reason'}

        response = self.app.post('/verification/worklist/close', data=test_form_data, follow_redirects=False)
        data = response.data.decode()

        self.assertEqual(response.status_code, 500)
        self.assertIn('Something went wrong when closing the account.', data)

    @mock.patch('verification_ui.views.verification.VerificationAPI')
    def test_add_note(self, _):
        test_form_data = {'item_id': '1', 'note_text': 'This is yet another note'}

        response = self.app.post('/verification/worklist/note', data=test_form_data, follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, '/verification/worklist/1')

    @mock.patch('verification_ui.views.verification.VerificationAPI')
    def test_add_note_error(self, mock_api):
        mock_api.return_value.add_note.side_effect = ApplicationError('Test error')
        test_form_data = {'item_id': '1', 'note_text': 'This is yet another note'}

        response = self.app.post('/verification/worklist/note', data=test_form_data, follow_redirects=False)
        data = response.data.decode()

        self.assertEqual(response.status_code, 500)
        self.assertIn('Something went wrong when adding a note.', data)

    @mock.patch('verification_ui.views.verification.VerificationAPI')
    def test_lock(self, _):
        test_form_data = {'item_id': '1'}
        response = self.app.post('/verification/worklist/lock', data=test_form_data, follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, '/verification/worklist/1')

    @mock.patch('verification_ui.views.verification.VerificationAPI')
    def test_lock_error(self, mock_api):
        mock_api.return_value.lock.side_effect = ApplicationError('Test error')
        test_form_data = {'item_id': '1'}

        response = self.app.post('/verification/worklist/lock', data=test_form_data, follow_redirects=False)
        data = response.data.decode()

        self.assertEqual(response.status_code, 500)
        self.assertIn('Something went wrong while locking the application.', data)

    @mock.patch('verification_ui.views.verification.VerificationAPI')
    def test_unlock(self, _):
        test_form_data = {'item_id': '1'}
        response = self.app.post('/verification/worklist/unlock', data=test_form_data, follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, '/verification/worklist')

    @mock.patch('verification_ui.views.verification.VerificationAPI')
    def test_unlock_error(self, mock_api):
        mock_api.return_value.lock.side_effect = ApplicationError('Test error')
        test_form_data = {'item_id': '1'}

        response = self.app.post('/verification/worklist/unlock', data=test_form_data, follow_redirects=False)
        data = response.data.decode()

        self.assertEqual(response.status_code, 500)
        self.assertIn('Something went wrong while unlocking the application.', data)

    def test_populate_username(self):
        test_username = 'TestUser'
        with app.test_request_context():
            result = verification.get_user_name()

        self.assertEqual(result, test_username)

    @mock.patch('verification_ui.views.verification.session')
    def test_get_search(self, mock_session):
        mock_session.get.return_value = [{'text': '01/01/2019'}, {'text': 'UK Personal'}, {'text': 'Mr Test User'},
                                         {'html': '<a href="/verification/worklist/1">View details</a>'}]
        response = self.app.get('/verification/worklist/search')
        data = response.data.decode()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_session.get.call_count, 1)
        self.assertIn('Search', data)
        self.assertIn('Mr Test User', data)

    @mock.patch('verification_ui.views.verification.session')
    def test_get_search_empty_session(self, mock_session):
        mock_session.get.return_value = None
        response = self.app.get('/verification/worklist/search')
        data = response.data.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('Search', data)
        self.assertEqual(mock_session.get.call_count, 1)

    @mock.patch('verification_ui.views.verification.build_row')
    @mock.patch('verification_ui.views.verification.VerificationAPI')
    def test_post_search(self, mock_api, mock_build):
        mock_api.return_value.perform_search.return_value = self.test_personal_item
        mock_build.return_value = [{'text': '01/01/2019'}, {'text': 'UK Personal'}, {'text': 'Mr Test User'},
                                   {'html': '<a href="/verification/worklist/1">View details</a>'}]
        search_entries = {
            "first_name": "test",
            "last_name": "",
            "organisation_name": "",
            "email": "",
        }

        response = self.app.post('/verification/worklist/search', data=search_entries, follow_redirects=False)
        data = response.data.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('Search', data)
        self.assertIn('Mr Test User', data)
        self.assertEqual(mock_api.return_value.perform_search.call_count, 1)
        self.assertEqual(mock_build.call_count, 1)

    @mock.patch('verification_ui.views.verification.build_row')
    @mock.patch('verification_ui.views.verification.VerificationAPI')
    def test_post_search_no_result(self, mock_api, mock_build):
        mock_api.return_value.perform_search.return_value = None
        mock_build.return_value = []
        search_entries = {
            "first_name": "test",
            "last_name": "",
            "organisation_name": "",
            "email": "",
        }

        response = self.app.post('/verification/worklist/search', data=search_entries, follow_redirects=False)
        data = response.data.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('Search', data)
        self.assertIn('No results found', data)
        self.assertEqual(mock_api.return_value.perform_search.call_count, 1)
        self.assertEqual(mock_build.call_count, 0)

    @mock.patch('verification_ui.views.verification.build_row')
    @mock.patch('verification_ui.views.verification.VerificationAPI')
    def test_post_search_error(self, mock_api, mock_build):
        mock_api.return_value.perform_search.side_effect = ApplicationError('Test error')
        mock_build.return_value = []
        search_entries = {
            "first_name": "test",
            "last_name": "",
            "organisation_name": "",
            "email": "",
        }

        response = self.app.post('/verification/worklist/search', data=search_entries, follow_redirects=False)
        data = response.data.decode()

        self.assertEqual(response.status_code, 500)
        self.assertIn('Something went wrong when performing the search.', data)
        self.assertEqual(mock_api.return_value.perform_search.call_count, 1)
        self.assertEqual(mock_build.call_count, 0)

    @mock.patch('verification_ui.views.verification.VerificationAPI')
    def test_update_contact_preferences(self, mock_api):
        form_data = {
            'item_id': '123',
            'contactable': 'True'
        }

        response = self.app.post('/verification/worklist/update_contact_preferences',
                                 data=form_data,
                                 follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, '/verification/worklist/123')

    @mock.patch('verification_ui.views.verification.VerificationAPI')
    def test_update_contact_preferences_error(self, mock_api):
        mock_api.return_value.update_user_details.side_effect = ApplicationError('error')
        form_data = {
            'item_id': '123',
            'contactable': 'True'
        }

        response = self.app.post('/verification/worklist/update_contact_preferences',
                                 data=form_data,
                                 follow_redirects=False)

        data = response.data.decode()

        self.assertEqual(response.status_code, 500)
        self.assertIn('Something went wrong when updating contact preferences', data)
