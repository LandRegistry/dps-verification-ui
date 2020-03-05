import os
import requests
from flask import g, current_app
from verification_ui.main import app


dir_ = os.path.dirname(os.path.abspath(__file__))
personal_item_json = open(os.path.join(dir_, 'data/personal_item.json'), 'r').read()


def create_personal_worklist_item():
    with app.app_context() as ac:
        ac.g.requests = requests.Session()
        base_url = current_app.config['VERIFICATION_API_URL']
        headers = {"Accept": "application/json", "Content-Type": "application/json"}

        with app.test_request_context():
            post_url = "{}/case".format(base_url)
            post_response = g.requests.post(post_url, data=personal_item_json, headers=headers)
            data = post_response.json()
            item_id = data['case_id']

            get_url = '{}/case/{}'.format(base_url, item_id)
            get_response = g.requests.get(get_url, headers=headers)
            return get_response.json()
