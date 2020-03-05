from flask_login import login_user, logout_user, current_user, UserMixin
from flask import redirect, session, request, current_app, Blueprint, g, url_for
from functools import wraps
from jose import jwt, JWTError
from requests.exceptions import ConnectionError
# for use when we implement user roles
# from functools import wraps
import requests
import textwrap
import xmltodict

from verification_ui.exceptions import ApplicationError
from verification_ui.extensions import login_manager
from verification_ui import config
from common_utilities import errors

authentication = Blueprint('authentication', __name__)
# Strictly speaking these should go in extensions.py but let's keep login stuff in (mostly) one place
login_manager.login_view = '/verification/login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.session_protection = "strong"


@login_manager.user_loader
def load_user(user_id):  # pragma: no cover
    """Creates and returns a User object based on a unique id.

    This will be automatically called when visiting a decorated function. The user_id comes from the session.
    If the user could not be loaded (probably due to token expiry), returning None tells Flask-Login to
    remove the userid from the session, so the user is subsequently treated as not logged in.
    """
    try:
        # Try to create
        return User(access_token=user_id)
    except Exception:
        # Most likely if token validation failed
        return None


@login_manager.unauthorized_handler
def handle_needs_login():
    """This will be automatically called when visiting a decorated function if the user is not logged in (due to
    no userid in session, or failure to load - see load_user()). They are redirected to the /login route.
    """
    # Save the original place they wanted to go (relative to the app only) for the final redirect later
    session['requested_page'] = request.url
    current_app.logger.info('need to redirect so here we go......')

    return redirect("{0}/verification//login".format(
                        current_app.config.get('ROOT_URL')))


class User(UserMixin):  # pragma: no cover
    # Static variables for ADFS token signature validation
    public_key_1 = None
    public_key_2 = None
    keys_already_swapped = False

    def __init__(self, access_token):
        """Creates a User based on an access token (or as Flask-Login knows it, the userid)

        As part of the process it validates the signature of the token along with other JWT claims such as expiry.
        """
        # Set the token then verify it
        self.access_token = access_token
        self.token_data = self._verify_token()

        self.employee_legacy_id = self.token_data["UserName"].upper()
        # Will need to use this later id we introduce role based access
        # self.office = self.token_data["Office"].upper()
        self.roles = self.token_data.get("group", [''])

    def get_employee_legacy_id(self):
        return self.employee_legacy_id

    def get_token_data(self):
        return self.token_data

    def get_employee_office(self):
        return self.office

    def get_roles(self):
        return self.roles

    def get_id(self):
        return self.access_token

    def has_role(self, role):
        if role in self.roles:
            return True
        else:
            return False

    def _verify_token(self, is_a_retry=False):
        """Handles checking that the jwt the user is using is actually from adfs and hasnt been tampered with.
        this includes retries and error handling to deal with expired/missing certificates and retrieving the
        latest certificates from adfs metadata
        """
        # If there are no certificate to use (on app first startup) go and get them
        if not User.public_key_1:
            self._get_certs_from_adfs()
        try:
            # try to decode with primary certificate
            decoded_token = self._decode_jwt(User.public_key_1)
            return decoded_token
        except JWTError as e:
            if str(e) == 'Signature verification failed.':
                # The certificate might have expired (and been swapped to secondary on ADFS itself),
                # so if we have a second try to use it
                if User.public_key_2:
                    try:
                        decoded_token = self._decode_jwt(User.public_key_2)
                        if not User.keys_already_swapped:
                            current_app.logger.info('Verified jwt with secondary certificate,'
                                                    'promoting to primary for future use.')
                            # If the second certificate worked promote it to primary
                            # Store the old primary as secondary to handle any users with leftover sessions
                            # We only want to swap them once otherwise we might just continually be switching as old
                            # and new users use the system
                            User.public_key_1, User.public_key_2 = User.public_key_2, User.public_key_1
                            User.keys_already_swapped = True
                        return decoded_token
                    except JWTError as e:
                        # if this errored with Signature verification failed we can retry with new certificates from
                        # adfs - any other error and we will need to throw an exception
                        if not str(e) == 'Signature verification failed.':
                            raise ApplicationError(e, 'E803', http_code=403)
                    except ApplicationError as e:
                        # It's possible there was an error getting the certificates from ADFS if so we will want to
                        # persist it
                        raise e
                    except Exception:
                        # If something went wrong with the second cert that we can't deal with we will want to know
                        # about it
                        raise ApplicationError('Unknown error occured while trying to validate login',
                                               'E803', http_code=500)

                if not is_a_retry:
                    # If this is the first time we have totally failed to validate the JWT we refresh both
                    # certificates and try again (Most likely scenario is that a new certificate has been introduced
                    # then subsequently promoted without us knowing)
                    # If we have alredy tried again we skip this step to avoid being stuck in a loop and raise an error
                    current_app.logger.error('Unable to validate jwt from ADFS with stored certificates')
                    self._get_certs_from_adfs()
                    return self._verify_token(is_a_retry=True)
                else:
                    # We get to this exception after trying the stored certificates AND new ones from ADFS
                    # Something is probably wrong with the JWT that ADFS returned
                    raise ApplicationError('Signature verification failed with new ADFS certificates',
                                           'E803', http_code=403)
            else:
                # We get to this exception if there is a problem validating the JWT but its not a signature
                # verification error
                raise ApplicationError(str(e), 'E803', http_code=403)
        except ApplicationError as e:
            # It's possible there was an error getting the certificates from ADFS if so we will want to persist it
            raise e
        except Exception as e:
            current_app.logger.error(e)
            raise ApplicationError('Unknown error occured while trying to validate login', 'E803', http_code=500)

    def _get_certs_from_adfs(self, is_a_retry=False):
        """Used by verify_token to connect to ADFS metadata and retrieve new certificates"""
        current_app.logger.info('Refreshing certificates from ADFS')

        # Clear old certs for ease of debugging
        User.public_key_1 = None
        User.public_key_2 = None
        try:
            res = requests.get('{}/federationMetadata/2007-06/federationmetadata.xml'.format(
                               current_app.config.get("ADFS_URL")), verify=False)
        except ConnectionError:
            if not is_a_retry:
                current_app.logger.warning('Failed to connect to ADFS, retrying')
                self._get_certs_from_adfs(is_a_retry=True)
                return
            else:
                raise ApplicationError('Unable to connect to ADFS', 'E802', http_code=500)
        adfs_meta_dict = xmltodict.parse(res.text)
        certs = adfs_meta_dict['EntityDescriptor']['RoleDescriptor'][1]['KeyDescriptor']
        # if there is only one cert then the cert variable will be a dict
        if isinstance(certs, dict):
            User.public_key_1 = self._reformat_adfs_cert(certs['KeyInfo']['X509Data']['X509Certificate'])
        # if there are 2 certs then the cert variable will be a list
        elif isinstance(certs, list):
            User.public_key_1 = self._reformat_adfs_cert(certs[0]['KeyInfo']['X509Data']['X509Certificate'])
            User.public_key_2 = self._reformat_adfs_cert(certs[1]['KeyInfo']['X509Data']['X509Certificate'])
        User.keys_already_swapped = False

        current_app.logger.info('ADFS primary cert:')
        if User.public_key_1:
            current_app.logger.info(User.public_key_1)
        else:
            current_app.logger.info('Unable to retrieve cert from ADFS')

        current_app.logger.info('ADFS secondary cert:')
        if User.public_key_2:
            current_app.logger.info(User.public_key_2)
        else:
            current_app.logger.info('Unable to retrieve cert from ADFS')

    def _reformat_adfs_cert(self, cert_string):
        """Used by verify_token to convert x509 certificates from adfs metadata into a usable format"""
        split = textwrap.fill(cert_string, 64)
        cert = "-----BEGIN CERTIFICATE-----\n{}\n-----END CERTIFICATE-----".format(split)
        return cert

    def _decode_jwt(self, key):
        """Used by verify_token to attempt the decode of the jwt with a provided certificate public key"""
        return jwt.decode(
            self.access_token,
            key,
            algorithms='RS256',
            audience=current_app.config.get('ROOT_URL') + "/verification/login",
            options={
                'leeway': int(current_app.config.get('JWT_LEEWAY'))
            }
        )


@authentication.route('/verification/login', methods=['GET', 'POST'])
def login():  # pragma: no cover
    """This route double checks that the user actually needs to be logged in, and if they do, sends them to ADFS."""

    current_app.logger.debug('Login requested. Checking if user is already logged in...')
    # If load_user() failed and returned None (due to token validation failure),
    # or there was no userid in the session to begin with,
    # this will be a default User implementation who's is_authenticated returns False. Handy!
    if not current_user.is_authenticated:
        current_app.logger.debug('Nope. Lets see if they have an access ticket for us')
        access_ticket = request.args.get("code")
        if access_ticket is None:
            current_app.logger.debug('They do not. Redirecting them to ADFS so they can get one and come back to us..')
            # Now send them to ADFS
            adfs_login_url = current_app.config.get('ADFS_URL') + \
                "/adfs/oauth2/authorize?response_type=code&client_id={0}&redirect_uri={1}&resource={1}&state={2}"
            return redirect(
                adfs_login_url.format(
                    current_app.config.get('ADFS_CLIENT_ID'),
                    current_app.config.get('ROOT_URL') + "/verification/login",
                    current_app.config.get('ADFS_STATE')))
        else:
            # Great, they've been redirected back from ADFS. Now we just need to swap the ticket for a token
            # and send them on their way.
            current_app.logger.debug('They do! Lets use it.')
            return finish_login(access_ticket)
    else:
        # Maybe went to /login directly instead of being redirected by an authentication failure
        current_app.logger.debug('They are. Sending them to the homepage')
        return redirect(url_for('verification.get_worklist'))


def finish_login(access_ticket):  # pragma: no cover
    """This method gets the access token, creates a User and saves them (their userid/token) into the session
    for future use when visiting protected routes. Then redirects them back to the original place they
    wanted to go at the start of the whole process.
    """
    try:
        access_token = get_access_token(access_ticket)
        if access_token is None:
            current_app.logger.error('Unable to get access token using access ticket: ' + str(access_ticket))
            raise ApplicationError("Unable to retrieve access token", "LOGIN")
        current_app.logger.debug('Successfully swapped access ticket for access token')

        # Create a user object and tell flask-login to add their userid (access token) to the session.
        # That userid will be used on future page requests (see load_user) to rebuild the user
        # object (and validate the access token)
        user = User(access_token=access_token)
        login_user(user)

        try:
            if session['requested_page'] is None:
                # In the unlikely event we can't remember where we originally wanted to go
                # (maybe went to /login directly)
                # go to the homepage
                redirect(url_for('verification.get_worklist'))
            else:
                current_app.logger.debug('The user is now logged in! \
                    Lets redirect them back to where they wanted to go')
                redirect_uri = session['requested_page']
                session['requested_page'] = None
                return redirect(redirect_uri)
        except Exception:
            redirect(url_for('verification.get_worklist'))
    except Exception:
        redirect(url_for('verification.get_worklist'))


def get_access_token(access_ticket):  # pragma: no cover
    """This method goes to ADFS with an access ticket and returns the final access token. Or None if it couldn't."""
    try:
        current_app.logger.debug('Asking ADFS for an access token in exchange for the access ticket')
        request_body = ("grant_type=authorization_code&client_id=" + current_app.config.get('ADFS_CLIENT_ID') +
                        "&redirect_uri=" + current_app.config.get('ROOT_URL') + "/verification/login" +
                        "&code=" + access_ticket)
        resp = g.requests.post(current_app.config.get('ADFS_URL') + '/adfs/oauth2/token', data=request_body,
                               verify=False)
        resp = resp.json()
        access_token = resp['access_token']
        if access_token == "unable to get access token using access ticket":
            return None
        return access_token
    except Exception as e:
        current_app.logger.info('Exception when getting access token: ' + str(e))
        return None


@authentication.route('/verification/logout')
def logout():  # pragma: no cover
    """This removes the user id/token from the session"""
    logout_user()
    return "You have logged out"


# decorater can be used with @role_required('caseworker')
def role_required(role):
    def _role_required(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            if config.LOGIN_DISABLED == 'True':
                return func(*args, **kwargs)
            if current_user.is_authenticated:
                current_app.logger.info('LIST OF ROLES: ' + str(current_user.get_roles()))
                if current_user.has_role(role):
                    return func(*args, **kwargs)
                else:
                    error = errors.get("verification_ui", "ADFS_ROLE_LOGGED_IN_ERROR", filler=str(role))

                    raise ApplicationError(*error)
            else:
                raise ApplicationError(*errors.get("verification_ui", "ADFS_ROLE_LOGGED_OUT_ERROR", filler=str(role)))
        return func_wrapper
    return _role_required
