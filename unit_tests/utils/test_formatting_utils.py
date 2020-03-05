import unittest
import os
import json
from unittest import mock
from verification_ui.main import app
from verification_ui.utils.formatting_utils import (build_row,
                                                    build_details_table,
                                                    format_date,
                                                    format_text_date,
                                                    format_date_and_time,
                                                    format_file_name,
                                                    format_account_type,
                                                    format_name, format_address,
                                                    format_note_metadata,
                                                    format_status,
                                                    format_contactable,
                                                    format_contact_by,
                                                    build_dataset_activity)


dir_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
personal_item_data = open(os.path.join(dir_, 'data/personal_item.json'), 'r').read()
uk_org_item_data = open(os.path.join(dir_, 'data/uk_org_item.json'), 'r').read()
overseas_org_item_data = open(os.path.join(dir_, 'data/overseas_org_item.json'), 'r').read()


class TestFormattingUtils(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.test_personal_item = json.loads(personal_item_data)
        self.test_uk_org_item = json.loads(uk_org_item_data)
        self.test_overseas_org_item = json.loads(overseas_org_item_data)

    @mock.patch('verification_ui.utils.formatting_utils.format_status',
                return_value='<span class="status-pending">Pending</span>')
    @mock.patch('verification_ui.utils.formatting_utils.format_name', return_value='Mr Test User')
    @mock.patch('verification_ui.utils.formatting_utils.format_account_type', return_value='UK Personal')
    @mock.patch('verification_ui.utils.formatting_utils.format_date', return_value='01/01/2019')
    def test_build_row_from_search(self, *_):
        worklist_row = build_row(self.test_personal_item, for_search=True)

        expected_result = [
            {'text': '01/01/2019'},
            {'text': 'UK Personal'},
            {'text': 'Mr Test User'},
            {'html': '<span class="status-pending">Pending</span>'},
            {'html': '<a class="govuk-link" href="/verification/worklist/1?from=search">View details</a>'},
            {'html': ''}
        ]

        self.assertEqual(worklist_row, expected_result)

    @mock.patch('verification_ui.utils.formatting_utils.session', return_value=mock.MagicMock())
    @mock.patch('verification_ui.utils.formatting_utils.format_status',
                return_value='<span class="status-pending">Pending</span>')
    @mock.patch('verification_ui.utils.formatting_utils.format_name', return_value='Mr Test User')
    @mock.patch('verification_ui.utils.formatting_utils.format_account_type', return_value='UK Organisation')
    @mock.patch('verification_ui.utils.formatting_utils.format_date', return_value='01/01/2019')
    @mock.patch('verification_ui.utils.formatting_utils.format_lock', return_value='<p>FAKE SVG</p>')
    def test_build_row_locked(self, mock_user, *_):
        mock_user.get_employee_legacy_id.return_value = 'LRTM100'
        worklist_row = build_row(self.test_uk_org_item, for_search=False)

        expected_result = [
            {'text': '01/01/2019'},
            {'text': 'Mr Test User'},
            {'html': '<span class="status-pending">Pending</span>'},
            {'html': '<a class="govuk-link" href="/verification/worklist/2">View details</a>'},
            {'html': '<p>FAKE SVG</p>'}
        ]

        self.assertListEqual(worklist_row, expected_result)

    @mock.patch('verification_ui.utils.formatting_utils.format_account_type')
    @mock.patch('verification_ui.utils.formatting_utils.format_address')
    @mock.patch('verification_ui.utils.formatting_utils.format_name')
    def test_build_personal_worklist_item_info(self, mock_name, mock_address, mock_acc_type):
        mock_name.return_value = 'Mr Test User'
        mock_address.return_value = '1 Test Street<br>Testyton<br>TE5 T3R5<br>UK<br>'
        mock_acc_type.return_value = 'UK Personal'
        phone_no = self.test_personal_item['registration_data']['telephone_number']
        email = self.test_personal_item['registration_data']['email']
        status = 'Pending'

        with app.test_request_context():
            worklist_item_info = build_details_table(self.test_personal_item)
            self.assertEqual(worklist_item_info,
                             [{'key': {'text': 'Full Name'},
                               'value': {'text': 'Mr Test User'},
                               'actions': {'items': []}},
                              {'key': {'text': 'Status'},
                               'value': {'html': format_status(status)},
                               'actions': {'items': []}},
                              {'key': {'text': 'Address'},
                               'value': {'html': '1 Test Street<br>Testyton<br>TE5 T3R5<br>UK<br>'},
                               'actions': {'items': []}},
                              {'key': {'text': 'Telephone Number'},
                               'value': {'text': phone_no},
                               'actions': {'items': []}},
                              {'key': {'text': 'Email'},
                               'value': {'text': email},
                               'actions': {'items': []}},
                              {'key': {'text': 'Contactable'},
                               'value': {'html': format_contactable(self.test_personal_item)},
                               'actions': {'items': []}},
                              {'key': {'text': 'Contact by'},
                               'value': {'html': format_contact_by(self.test_personal_item)},
                               'actions': {'items': []}},
                              {'key': {'text': 'Account Type'},
                               'value': {'text': 'UK Personal'},
                               'actions': {'items': []}}])

    @mock.patch('verification_ui.utils.formatting_utils.format_account_type')
    @mock.patch('verification_ui.utils.formatting_utils.format_address')
    @mock.patch('verification_ui.utils.formatting_utils.format_name')
    def test_build_uk_org_worklist_item_info(self, mock_name, mock_address, mock_acc_type):
        mock_name.return_value = 'Mr Test User'
        mock_address.return_value = '1 Test Street<br>Testyton<br>TE5 T3R5<br>'
        mock_acc_type.return_value = 'UK Organisation'
        status = 'Pending'
        phone_no = self.test_uk_org_item['registration_data']['telephone_number']
        email = self.test_uk_org_item['registration_data']['email']
        org_name = self.test_uk_org_item['registration_data']['organisation_name']
        org_type = self.test_uk_org_item['registration_data']['organisation_type']
        reg_no = self.test_uk_org_item['registration_data']['registration_number']

        with app.test_request_context():
            worklist_item_info = build_details_table(self.test_uk_org_item)
            self.assertEqual(worklist_item_info,
                             [{'key': {'text': 'Full Name'},
                               'value': {'text': 'Mr Test User'},
                               'actions': {'items': []}},
                              {'key': {'text': 'Status'},
                               'value': {'html': format_status(status)},
                               'actions': {'items': []}},
                              {'key': {'text': 'Address'},
                               'value': {'html': '1 Test Street<br>Testyton<br>TE5 T3R5<br>'},
                               'actions': {'items': []}},
                              {'key': {'text': 'Telephone Number'},
                               'value': {'text': phone_no},
                               'actions': {'items': []}},
                              {'key': {'text': 'Email'},
                               'value': {'text': email},
                               'actions': {'items': []}},
                              {'key': {'text': 'Contactable'},
                               'value': {'html': format_contactable(self.test_uk_org_item)},
                               'actions': {'items': []}},
                              {'key': {'text': 'Contact by'},
                               'value': {'html': format_contact_by(self.test_uk_org_item)},
                               'actions': {'items': []}},
                              {'key': {'text': 'Account Type'},
                               'value': {'text': 'UK Organisation'},
                               'actions': {'items': []}},
                              {'key': {'text': 'Organisation Name'},
                               'value': {'text': org_name},
                               'actions': {'items': []}},
                              {'key': {'text': 'Organisation Type'},
                               'value': {'text': org_type},
                               'actions': {'items': []}},
                              {'key': {'text': 'Registration Number'},
                               'value': {'text': reg_no},
                               'actions': {'items': []}}])

    @mock.patch('verification_ui.utils.formatting_utils.format_account_type')
    @mock.patch('verification_ui.utils.formatting_utils.format_address')
    @mock.patch('verification_ui.utils.formatting_utils.format_name')
    def test_build_overseas_org_worklist_item_info(self, mock_name, mock_address, mock_acc_type):
        mock_name.return_value = 'Madame Testy Userre'
        mock_address.return_value = '1 Rue de Test<br>Testyville<br>75001<br>'
        mock_acc_type.return_value = 'Overseas Organisation'
        phone_no = self.test_overseas_org_item['registration_data']['telephone_number']
        email = self.test_overseas_org_item['registration_data']['email']
        org_name = self.test_overseas_org_item['registration_data']['organisation_name']
        country_incorp = self.test_overseas_org_item['registration_data']['country_of_incorporation']
        status = 'Pending'

        with app.test_request_context():
            worklist_item_info = build_details_table(self.test_overseas_org_item)
            self.assertEqual(worklist_item_info,
                             [{'key': {'text': 'Full Name'},
                               'value': {'text': 'Madame Testy Userre'},
                               'actions': {'items': []}},
                              {'key': {'text': 'Status'},
                               'value': {'html': format_status(status)},
                               'actions': {'items': []}},
                              {'key': {'text': 'Address'},
                               'value': {'html': '1 Rue de Test<br>Testyville<br>75001<br>'},
                               'actions': {'items': []}},
                              {'key': {'text': 'Telephone Number'},
                               'value': {'text': phone_no},
                               'actions': {'items': []}},
                              {'key': {'text': 'Email'},
                               'value': {'text': email},
                               'actions': {'items': []}},
                              {'key': {'text': 'Contactable'},
                               'value': {'html': format_contactable(self.test_overseas_org_item)},
                               'actions': {'items': []}},
                              {'key': {'text': 'Contact by'},
                               'value': {'html': format_contact_by(self.test_overseas_org_item)},
                               'actions': {'items': []}},
                              {'key': {'text': 'Account Type'},
                               'value': {'text': 'Overseas Organisation'},
                               'actions': {'items': []}},
                              {'key': {'text': 'Organisation Name'},
                               'value': {'text': org_name},
                               'actions': {'items': []}},
                              {'key': {'text': 'Country of Incorporation'},
                               'value': {'text': country_incorp},
                               'actions': {'items': []}}])

    def test_format_date(self):
        datetime_string = '2019-01-01 12:12:12.000000'

        formatted_date = format_date(datetime_string)

        self.assertEqual(formatted_date, '01/01/2019')

    def test_format_text_date(self):
        datetime_string = '2019-01-01T12:12:12.000000'

        formatted_date = format_text_date(datetime_string)

        self.assertEqual(formatted_date, '01 January 2019')

    def test_format_date_and_time(self):
        datetime_string = '2019-01-01T12:12:12.000000'

        formatted_date = format_date_and_time(datetime_string)

        self.assertEqual(formatted_date, '01 January 2019 12:12')

    def test_format_file_name_cou(self):
        file_name = 'CCOD_COU_2019_08.zip'

        formatted_file_name = format_file_name(file_name)

        self.assertEqual(formatted_file_name, 'Change only')

    def test_format_file_name_full(self):
        file_name = 'CCOD_FULL_2019_08.zip'

        formatted_file_name = format_file_name(file_name)

        self.assertEqual(formatted_file_name, 'Full dataset')

    def test_format_file_name_sample(self):
        file_name = 'LR_NPS_SAMPLE.zip'

        formatted_file_name = format_file_name(file_name)

        self.assertEqual(formatted_file_name, 'Sample dataset')

    def test_format_file_name_unrecognised(self):
        file_name = 'LR_NPS.zip'

        formatted_file_name = format_file_name(file_name)

        self.assertEqual(formatted_file_name, file_name)

    def test_format_account_type(self):
        data = {
            'registration_data': {
                'user_type': 'organisation-uk'
            }}

        formatted_acc_type = format_account_type(data)

        self.assertEqual(formatted_acc_type, 'UK Organisation')

    def test_format_account_type_unrecognised_type(self):
        data = {
            'registration_data': {
                'user_type': 'uk-organisation'
            }}

        formatted_acc_type = format_account_type(data)

        self.assertEqual(formatted_acc_type, 'uk-organisation')

    def test_format_name(self):
        data = {
            'registration_data': {
                'title': 'Mr',
                'first_name': 'Test',
                'last_name': 'User'
            }}
        name = format_name(data)

        self.assertEqual(name, 'Mr Test User')

    def test_format_name_blank_part(self):
        data = {
            'registration_data': {
                'title': 'Mr',
                'first_name': '',
                'last_name': 'User'
            }}

        formatted_name = format_name(data)

        self.assertEqual(formatted_name, 'Mr User')

    def test_format_address_uk_org(self):
        data = {
            'registration_data': {
                'address_line_1': '1 Test Street',
                'address_line_2': 'Testyville',
                'city': 'Testyton',
                'country': 'UK',
                'postcode': 'TE5 T3R5',
                'user_type': 'organisation-uk'
            }}

        formatted_address = format_address(data)

        self.assertEqual(formatted_address, '1 Test Street<br>Testyville<br>Testyton<br>TE5 T3R5<br>')

    def test_format_address_overseas_org(self):
        data = {
            'registration_data': {
                'address_line_1': '1 Test Street',
                'address_line_2': 'Testyville',
                'city': 'Testyton',
                'country_of_incorporation': 'France',
                'postcode': 'TE5 T3R5',
                'user_type': 'organisation-overseas'
            }}

        formatted_address = format_address(data)

        self.assertEqual(formatted_address, '1 Test Street<br>Testyville<br>Testyton<br>TE5 T3R5<br>')

    def test_format_address_blank_part(self):
        data = {
            'registration_data': {
                'address_line_1': '1 Test Street',
                'address_line_2': '',
                'city': 'Testyton',
                'country': 'France',
                'postcode': 'TE5 T3R5',
                'user_type': 'personal-overseas'
            }}

        formatted_address = format_address(data)

        self.assertEqual(formatted_address, '1 Test Street<br>Testyton<br>TE5 T3R5<br>France<br>')

    def test_format_note_metadata(self):
        note_data = self.test_personal_item['notes'][0]

        note_metadata = format_note_metadata(note_data)

        self.assertEqual(note_metadata, 'Added by testuser on 01/01/2019 12:12:12')

    def test_build_dataset_activity_with_sample(self):
        dataset_activity = [
                                {
                                    "licence_agreed_date": "2018-08-27T12:12:12.000000",
                                    "name": "nps",
                                    "title": "National Polygon Service",
                                    "download_history": [
                                        {
                                            "date": "2018-08-28T12:12:12.000000",
                                            "file": "NSD_COU_2019_08.zip"
                                        }
                                    ],
                                    "private": True,
                                    "licence_agreed": True,
                                    "id": "1b91267f-0e8f-41d2-bf73-5a3a6f8f5fc6"
                                },
                                {
                                    "licence_agreed_date": "2018-07-27T12:12:12.000000",
                                    "name": "nps_sample",
                                    "title": "National Polygon Service Sample",
                                    "download_history": [
                                        {
                                            "date": "2018-07-20T12:12:12.000000",
                                            "file": "LR_NPS_SAMPLE.zip"
                                        }
                                    ],
                                    "private": False,
                                    "licence_agreed": True,
                                    "id": "15724bf1-ca69-40a7-98c6-a1e324dfe460"
                                }
                            ]

        activity = build_dataset_activity(dataset_activity)

        self.assertEqual(2, activity['download_count'])
        self.assertEqual('20 July 2018', activity['oldest_download_date'])
        self.assertEqual(1, len(activity['datasets']))
        self.assertEqual('National Polygon Service', activity['datasets'][0]['heading']['text'])
        self.assertEqual('Licence agreed on 27 August 2018', activity['datasets'][0]['summary']['text'])
        self.assertIn('Change only', activity['datasets'][0]['content']['html'])
        self.assertIn('Sample dataset', activity['datasets'][0]['content']['html'])

    def test_build_dataset_activity_no_sample(self):
        dataset_activity = [
                                {
                                    "licence_agreed_date": "2018-09-27T12:12:12.000000",
                                    "name": "ccod",
                                    "title": "UK companies that own property in England and Wales",
                                    "download_history": [
                                        {
                                            "date": "2018-09-28T12:12:12.000000",
                                            "file": "CCOD_COU_2019_08.zip"
                                        }
                                    ],
                                    "private": True,
                                    "licence_agreed": True,
                                    "id": "1b91267f-0e7f-42c2-bf73-5a3a6f8f5ec6"
                                }
                            ]

        activity = build_dataset_activity(dataset_activity)

        self.assertEqual(1, activity['download_count'])
        self.assertEqual('28 September 2018', activity['oldest_download_date'])
        self.assertEqual(1, len(activity['datasets']))
        self.assertEqual('UK companies that own property in England and Wales',
                         activity['datasets'][0]['heading']['text'])
        self.assertEqual('Licence agreed on 27 September 2018', activity['datasets'][0]['summary']['text'])
        self.assertIn('Change only', activity['datasets'][0]['content']['html'])

    def test_build_dataset_activity_licence_agreed_restricted(self):
        dataset_activity = [
                                {
                                    "name": "nps",
                                    "title": "National Polygon Service",
                                    "download_history": [
                                        {
                                            "date": "2018-08-28T12:12:12.000000",
                                            "file": "NSD_COU_2019_08.zip"
                                        }
                                    ],
                                    "private": True,
                                    "licence_agreed": True,
                                    "id": "1b91267f-0e7f-42c2-bf73-5a3a6f8f5fc6"
                                }
                            ]

        activity = build_dataset_activity(dataset_activity)

        self.assertEqual(1, activity['download_count'])
        self.assertEqual('28 August 2018', activity['oldest_download_date'])
        self.assertEqual(1, len(activity['datasets']))
        self.assertEqual('National Polygon Service', activity['datasets'][0]['heading']['text'])
        self.assertEqual('Licence has been agreed', activity['datasets'][0]['summary']['text'])
        self.assertIn('Change only', activity['datasets'][0]['content']['html'])

    def test_build_dataset_activity_licence_not_agreed(self):
        dataset_activity = [
                                {
                                    "name": "nps",
                                    "title": "National Polygon Service",
                                    "download_history": [
                                        {
                                            "date": "2018-08-28T12:12:12.000000",
                                            "file": "NSD_COU_2019_08.zip"
                                        }
                                    ],
                                    "private": True,
                                    "licence_agreed": False,
                                    "id": "1b91267f-0e7f-42c2-bf73-5a3a6f8f5fc6"
                                }
                            ]

        activity = build_dataset_activity(dataset_activity)

        self.assertEqual(1, activity['download_count'])
        self.assertEqual('28 August 2018', activity['oldest_download_date'])
        self.assertEqual(1, len(activity['datasets']))
        self.assertEqual('National Polygon Service', activity['datasets'][0]['heading']['text'])
        self.assertEqual('Licence has not been agreed', activity['datasets'][0]['summary']['text'])
        self.assertIn('Change only', activity['datasets'][0]['content']['html'])

    def test_build_dataset_activity_no_download_history(self):
        dataset_activity = [
                                {
                                    "licence_agreed_date": "2018-09-27T12:12:12.000000",
                                    "name": "ccod",
                                    "title": "UK companies that own property in England and Wales",
                                    "download_history": [],
                                    "private": True,
                                    "licence_agreed": True,
                                    "id": "1b91267f-0e7f-42c2-bf73-5a3a6f8f5ec6"
                                }
                            ]

        activity = build_dataset_activity(dataset_activity)

        self.assertEqual(0, activity['download_count'])
        self.assertEqual(1, len(activity['datasets']))
        self.assertEqual('UK companies that own property in England and Wales',
                         activity['datasets'][0]['heading']['text'])
        self.assertEqual('Licence agreed on 27 September 2018', activity['datasets'][0]['summary']['text'])
        self.assertIn('This account has not downloaded any files for this dataset.',
                      activity['datasets'][0]['content']['html'])
