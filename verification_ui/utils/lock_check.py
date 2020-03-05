import logging
from verification_ui.dependencies.verification_api import VerificationAPI

log = logging.getLogger(__name__)


def check_correct_lock_user(item_id, username):
    verficiation_api = VerificationAPI()
    result = verficiation_api.get_item(item_id)
    locked_user = result['staff_id']
    current_user = username
    if locked_user is None:
        return True
    elif locked_user != current_user:
        return False
    else:
        return True
