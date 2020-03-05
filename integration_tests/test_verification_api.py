import unittest
import requests
from verification_ui.main import app
from verification_ui.dependencies.verification_api import VerificationAPI


class TestVerification(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        app.config['WTF_CSRF_ENABLED'] = False

    def tearDown(self):
        app.config['WTF_CSRF_ENABLED'] = True

    def test_get_verification_api(self):
        with app.app_context()as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                verification_api = VerificationAPI()
                resp_data = verification_api.get_worklist()
                self.assertIsNotNone(resp_data)

    def test_post_verification_api(self):
        pass
