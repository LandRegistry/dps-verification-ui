import requests
import json
from flask import current_app, g
from common_utilities import errors
from verification_ui.exceptions import ApplicationError


class VerificationAPI(object):
    def __init__(self):
        self.base_url = current_app.config['VERIFICATION_API_URL']

    def _request(self, uri, data=None):
        url = '{}/{}'.format(self.base_url, uri)
        headers = {'Accept': 'application/json'}
        timeout = current_app.config['DEFAULT_TIMEOUT']

        try:
            if data is None:
                response = g.requests.get(url, headers=headers, timeout=timeout)
            else:
                headers['Content-Type'] = 'application/json'
                response = g.requests.post(url, headers=headers, timeout=timeout, data=data)
            status = response.status_code
            if status == 204:
                return {}
            if status == 404:
                error = 'Not Found'
                raise ApplicationError(
                    *errors.get('verification_ui', 'API_HTTP_ERROR', filler=str(error)),
                    http_code=status)
            else:
                response.raise_for_status()
                return response.json()

        except requests.exceptions.HTTPError as error:
            current_app.logger.error('Encountered non-2xx HTTP code when accessing {}'.format(url))
            current_app.logger.error('Error: {}'.format(error))
            raise ApplicationError(*errors.get('verification_ui', 'API_HTTP_ERROR', filler=str(error)))
        except requests.exceptions.ConnectionError as error:
            current_app.logger.error('Encountered an error while connecting to Verification API')
            raise ApplicationError(*errors.get('verification_ui', 'API_CONN_ERROR', filler=str(error)))
        except requests.exceptions.Timeout as error:
            current_app.logger.error('Encountered a timeout while accessing {}'.format(url))
            raise ApplicationError(*errors.get('verification_ui', 'API_TIMEOUT', filler=str(error)))

    def get_worklist(self):
        current_app.logger.info('Retrieving list of applications pending approval...')
        return self._request(uri='worklist')

    def get_item(self, item_id):
        current_app.logger.info('Retrieving details for case...')
        uri = 'case/{}'.format(item_id)
        return self._request(uri=uri)

    def approve_worklist_item(self, item_id, staff_id):
        current_app.logger.info('Approving worklist item...')
        data = json.dumps({
            'staff_id': staff_id
        })
        return self._request(uri='case/{}/approve'.format(item_id), data=data)

    def decline_worklist_item(self, item_id, staff_id, reason, advice):
        current_app.logger.info('Declining worklist item...')
        data = json.dumps({
            'staff_id': staff_id,
            'reason': reason,
            'advice': advice
        })
        return self._request(uri='case/{}/decline'.format(item_id), data=data)

    def close_account(self, item_id, staff_id, requester, reason):
        current_app.logger.info('Closing account...')
        data = json.dumps({
            'staff_id': staff_id,
            'requester': requester,
            'close_detail': reason})

        return self._request(uri='case/{}/close'.format(item_id), data=data)

    def add_note(self, item_id, staff_id, note_text):
        current_app.logger.info('Adding note to notepad...')
        data = json.dumps({
            'staff_id': staff_id,
            'note_text': note_text
        })
        return self._request(uri='case/{}/note'.format(item_id), data=data)

    def lock(self, item_id, staff_id):
        current_app.logger.info('Locking item to current user...')
        data = json.dumps({
            'staff_id': staff_id
        })
        return self._request(uri='case/{}/lock'.format(item_id), data=data)

    def unlock(self, item_id):
        current_app.logger.info('Unlocking item...')
        return self._request(uri='case/{}/unlock'.format(item_id), data={})

    def perform_search(self, search_params):
        current_app.logger.info('Performing search...')
        data = json.dumps(search_params)
        return self._request(uri='search', data=data)

    def get_decline_reasons(self):
        current_app.logger.info('Retrieving common decline reasons...')
        return self._request(uri='decline-reasons')

    def update_user_details(self, case_id, params):
        current_app.logger.info('Updating user details')
        data = json.dumps(params)
        return self._request(uri='case/{}/update'.format(case_id), data=data)

    def get_dataset_activity(self, case_id):
        current_app.logger.info('Getting download history for case')
        return self._request(uri='dataset-activity/{}'.format(case_id))

    def get_user_dataset_access(self, case_id):
        current_app.logger.info('Getting data access for case')
        return self._request(uri='dataset-access/{}'.format(case_id))

    def update_dataset_access(self, case_id, staff_id, current_access, updated_access):
        current_app.logger.info('Updating users access to datasets...')

        data_dict = {
            'staff_id': staff_id,
            'licences': []
        }

        # Current access has all datasets and whether the user has agreed individual licences
        # We need the current access as only checkboxes that are 'checked' will be included in the form submit data
        for dataset in current_access:
            for licence_name, licence_dict in dataset['licences'].items():

                # updated_access is 'request.form' - get list of form values with all inputs that have dataset name
                # e.g. ['nps', 'dad']
                updated_dataset_list = updated_access.getlist(dataset['name'])

                # Is licence (e.g. 'res_cov_exploration') in form data - access to be granted if yes else removed
                update_value = licence_name in updated_dataset_list

                # Only update if the value to be updated is different from what the user had previously
                if update_value != licence_dict['agreed']:
                    licence_dict = dict(licence_id=licence_name, agreed=update_value)
                    data_dict['licences'].append(licence_dict)

        # Only call API to update if anything to update
        if data_dict['licences']:
            return self._request(uri='case/{}/update_dataset_access'.format(case_id), data=json.dumps(data_dict))

        return {}
