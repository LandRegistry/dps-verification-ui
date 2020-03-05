import json
from flask import Blueprint
from flask import render_template, current_app, g, redirect, url_for, request, flash, session
from flask_login import login_required, current_user

from verification_ui.exceptions import ApplicationError
from verification_ui.dependencies.verification_api import VerificationAPI
from verification_ui.utils.formatting_utils import build_row, build_details_table, format_note_metadata, \
    build_dataset_activity
from verification_ui.utils.form_utils import NoteForm, DeclineForm, CloseForm, SearchForm, DataAccessForm, ContactForm
from verification_ui.views.login import role_required
from verification_ui import config
from verification_ui.utils.lock_check import check_correct_lock_user

# This is the blueprint object that gets registered into the app in blueprints.py.
verification = Blueprint('verification', __name__)
admin_role = config.ADFS_ROLE


@verification.route('', methods=['GET'])
@login_required
@role_required(admin_role)
def get_worklist():
    current_app.logger.info('User requested to view worklist...')

    try:
        verification_api = VerificationAPI()
        worklist = verification_api.get_worklist()
        _get_user_name()
    except ApplicationError:
        raise ApplicationError('Something went wrong when retrieving the worklist. '
                               'Please raise an incident quoting the following id: {}'.format(g.trace_id))
    else:
        current_app.logger.info('Putting worklist into viewable format...')
        worklist_items = [build_row(item) for item in worklist]

        return render_template('app/worklist.html', worklist_items=worklist_items)


@verification.route('/<item_id>', methods=['GET'])
@login_required
@role_required(admin_role)
def get_item(item_id):
    current_app.logger.info('User requested to view item {}...'.format(item_id))
    try:
        _get_user_name()
        verification_api = VerificationAPI()
        case = verification_api.get_item(item_id)
        lock = _handle_lock(case, verification_api) if case['status'] in ['Pending', 'In Progress'] else None

        if case['status'] == 'Approved':
            dataset_activity = verification_api.get_dataset_activity(item_id)
            dataset_access = verification_api.get_user_dataset_access(item_id)

        from_search = request.args.get('from', None) == 'search'
        if not from_search:
            session['search_params'] = None

    except ApplicationError as error:
        if error.http_code == 404:
            return render_template('app/errors/unhandled.html', http_code=404)

        raise ApplicationError('Something went wrong when requesting the application details. '
                               'Please raise and incident quoting the following id: {}'.format(g.trace_id))
    else:
        current_app.logger.info('Putting worklist item information into viewable format...')

        case_data_for_template = {
            'id': item_id,
            'status': case['status'],
            'info': build_details_table(case),
            'notes': [{
                'text': note['note_text'],
                'meta_data': format_note_metadata(note)
            } for note in case['notes']]
        }

        if case['status'] in ['Pending', 'In Progress', 'Declined']:
            forms = _build_app_forms(item_id, case['status'], lock is None, verification_api)
            return render_template('app/application_details.html', case_data=case_data_for_template,
                                   forms=forms, search=from_search, lock=lock)
        else:
            account_name = ' '.join([case['registration_data']['title'], case['registration_data']['first_name'],
                                     case['registration_data']['last_name']])
            if case['status'] == 'Approved':
                forms = _build_acc_forms(item_id, case['status'], dataset_access)
                activity = build_dataset_activity(dataset_activity)
                return render_template('app/account_details.html',
                                       case_data=case_data_for_template,
                                       forms=forms,
                                       search=from_search,
                                       activity=activity,
                                       account_name=account_name,
                                       dataset_access=dataset_access)
            else:
                forms = _build_acc_forms(item_id, case['status'])
                return render_template('app/account_details.html', case_data=case_data_for_template, forms=forms,
                                       search=from_search, account_name=account_name)


@verification.route('/approve', methods=['POST'])
@login_required
@role_required(admin_role)
def approve_worklist_item():
    try:
        session['search_params'] = None
        staff_id = _get_user_name()
        item_id = request.form['item_id']
        if not check_correct_lock_user(item_id, session['username']):
            flash('You are not the current locked user of Worklist item {}'.format(item_id))
            return redirect(url_for('verification.get_worklist'))
        current_app.logger.info('User {} approving worklist item {}...'.format(staff_id, item_id))
        verification_api = VerificationAPI()
        verification_api.approve_worklist_item(item_id, staff_id)
    except ApplicationError:
        raise ApplicationError('Something went wrong when approving the application. '
                               'Please raise an incident quoting the following id: {}'.format(g.trace_id))
    else:
        current_app.logger.info('Worklist item {} was approved'.format(item_id))
        flash('Application was approved')
        return redirect(url_for('verification.get_worklist'))


@verification.route('/decline', methods=['POST'])
@login_required
@role_required(admin_role)
def decline_worklist_item():
    try:
        session['search_params'] = None
        staff_id = _get_user_name()
        item_id = request.form['item_id']
        if not check_correct_lock_user(item_id, session['username']):
            flash('You are not the current locked user of Worklist item {}'.format(item_id))
            return redirect(url_for('verification.get_worklist'))
        reason = request.form['decline_reason']
        advice = request.form['decline_advice']
        current_app.logger.info('User {} declining worklist item {}...'.format(staff_id, item_id))
        verification_api = VerificationAPI()
        verification_api.decline_worklist_item(item_id, staff_id, reason, advice)
    except ApplicationError:
        raise ApplicationError('Something went wrong when declining the application. '
                               'Please raise an incident quoting the following id: {}'.format(g.trace_id))
    else:
        current_app.logger.info('Worklist item {} was declined'.format(item_id))
        flash('Application was declined')
        return redirect(url_for('verification.get_worklist'))


@verification.route('/close', methods=['POST'])
@login_required
@role_required(admin_role)
def close_account():
    try:
        session['search_params'] = None
        staff_id = _get_user_name()
        item_id = request.form['item_id']
        requester = request.form['close_requester']
        reason = request.form['close_reason']
        current_app.logger.info('User {} closing account {}...'.format(staff_id, item_id))

        verification_api = VerificationAPI()
        verification_api.close_account(item_id, staff_id, requester, reason)
    except ApplicationError:
        raise ApplicationError('Something went wrong when closing the account. '
                               'Please raise an incident quoting the following id: {}'.format(g.trace_id))
    else:
        current_app.logger.info('Account {} was closed'.format(item_id))
        if requester == 'customer':
            flash('Account was closed and email was sent to account holder')
        else:
            flash('Account was closed')
        return redirect(url_for('verification.get_worklist'))


@verification.route('/note', methods=['POST'])
@login_required
@role_required(admin_role)
def add_note():
    try:
        session['search_items'] = None
        staff_id = _get_user_name()
        item_id = request.form['item_id']
        note_text = request.form['note_text']
        current_app.logger.info('Adding note "{}" to notepad for worklist item {}...'.format(note_text, item_id))

        verification_api = VerificationAPI()
        verification_api.add_note(item_id, staff_id, note_text)
    except ApplicationError:
        raise ApplicationError('Something went wrong when adding a note. '
                               'Please raise an incident quoting the following id: {}'.format(g.trace_id))
    else:
        current_app.logger.info('Note was added to the notepad')
        flash('Your note was added to the notepad')
        return redirect(url_for('verification.get_item', item_id=item_id))


@verification.route('/lock', methods=['POST'])
@login_required
def lock_case():
    try:
        session['search_params'] = None
        staff_id = _get_user_name()
        item_id = request.form['item_id']
        current_app.logger.info('Locking worklist item {} to user {}...'.format(item_id, staff_id))
        verification_api = VerificationAPI()
        verification_api.lock(item_id, staff_id)
    except ApplicationError:
        raise ApplicationError('Something went wrong while locking the application. '
                               'Please raise an incident quoting the following id: {}'.format(g.trace_id))
    else:
        current_app.logger.info('Worklist item lock successfully transferred to user {}'.format(staff_id))
        return redirect(url_for('verification.get_item', item_id=item_id))


@verification.route('/unlock', methods=['POST'])
@login_required
def unlock_case():
    try:
        session['search_params'] = None
        item_id = request.form['item_id']
        current_app.logger.info('Unlocking worklist item {}'.format(item_id))
        verification_api = VerificationAPI()
        verification_api.unlock(item_id)
    except ApplicationError:
        raise ApplicationError('Something went wrong while unlocking the application. '
                               'Please raise an incident quoting the following id: {}'.format(g.trace_id))
    else:
        current_app.logger.info('Worklist item successfully unlocked')
        return redirect(url_for('verification.get_worklist'))


@verification.route('/search', methods=['GET'])
@login_required
@role_required(admin_role)
def get_search():
    search_form = SearchForm()
    search_items = []
    has_hit_limit = False
    new_search = False
    try:
        # Default to search params from session
        search_params = session.get('search_params', {})

        # Get search params from form/url for a new search instead search cached on session
        if request.args:
            new_search = True
            search_params = {
                "first_name": request.args.get('first_name'),
                "last_name": request.args.get('last_name'),
                "organisation_name": request.args.get('organisation_name'),
                "email": request.args.get('email')
            }

        # Perform search if any params and store new params on session
        if search_params:
            results = VerificationAPI().perform_search(search_params)
            search_limit = current_app.config.get('VERIFICATION_SEARCH_LIMIT')
            has_hit_limit = len(results) > search_limit
            search_items = [build_row(item, for_search=True) for item in results[:search_limit]]
            session['search_params'] = search_params

    except ApplicationError:
        raise ApplicationError('Something went wrong when performing last search. '
                               'Please raise an incident quoting the following id: {}'.format(g.trace_id))
    else:
        return render_template('app/search.html',
                               search_form=search_form,
                               search_items=search_items,
                               has_hit_limit=has_hit_limit,
                               new_search=new_search)


@verification.route('/<item_id>/contact_preferences', methods=['GET', 'POST'])
@login_required
@role_required(admin_role)
def contact_preferences(item_id):
    try:
        verification_api = VerificationAPI()
        case = verification_api.get_item(item_id)
        form = _build_contact_form(case)

        if form.validate_on_submit():
            contactable = request.form['contactable'] == 'yes'

            params = {
                'updated_data': {
                    'contactable': contactable,
                    'contact_preferences': request.form.getlist('contact_preferences')
                },
                'staff_id': _get_user_name()
            }

            verification_api.update_user_details(item_id, params)
            return redirect(url_for('verification.get_item', item_id=item_id))

        return render_template('app/contact_preferences.html', form=form, item_id=item_id)
    except ApplicationError:
        raise ApplicationError('Something went wrong while updating user contact preferences'
                               'Please raise an incident quoting the following id: {}'.format(g.trace_id))


@verification.route('/update_dataset_access', methods=['POST'])
@login_required
@role_required(admin_role)
def update_dataset_access():
    try:
        current_app.logger.info('Updating dataset access...')
        item_id = request.form['item_id']
        staff_id = _get_user_name()
        updated_access = request.form

        verification_api = VerificationAPI()
        current_access = verification_api.get_user_dataset_access(item_id)

        # Temporarily filter out ocod/ccod/nps_sample/res_cov_direct from access being updated
        for dataset in current_access:
            if dataset['name'] == 'licenced':
                dataset['licences'] = {}

            # Filter out sample and direct licence entries
            licences = {k: v for (k, v) in dataset['licences'].items() if '_direct' not in k and '_sample' not in k}
            dataset['licences'] = licences

        verification_api.update_dataset_access(item_id, staff_id, current_access, updated_access)

        flash("User's data access was updated")
        return redirect(url_for('verification.get_item', item_id=item_id))
    except ApplicationError:
        raise ApplicationError('Something went wrong when updating users data access. '
                               'Please raise an incident quoting the following id: {}'.format(g.trace_id))


def _get_user_name():
    if 'username' not in session:
        if current_app.config.get("LOGIN_DISABLED") == 'True':
            session['username'] = 'TestUser'
        else:
            session['username'] = current_user.get_employee_legacy_id()
    return session['username']


# Returns None if either locking is not applicable (due to case's status) or the case
# is locked to the current user. Otherwise, returns the staff_id of the user the case
# is locked to.
def _handle_lock(case, verification_api):
    lock = case['staff_id']
    current_uid = session['username']
    case_id = case['case_id']
    if lock is None:
        current_app.logger.info('Locking worklist item {} to user {}...'.format(case_id, current_uid))
        verification_api.lock(case_id, current_uid)
        return None
    elif lock == session['username']:
        return None
    else:
        return lock


def _build_app_forms(item_id, case_status, editable, verification_api):
    forms = {}

    if editable:
        forms['note'] = NoteForm()

        if case_status in ['Pending', 'In Progress']:
            decline_templates = verification_api.get_decline_reasons()
            decline_form = DeclineForm()
            decline_form.decline_template.choices = [('template_{}'.format(index), template['decline_reason'])
                                                     for index, template in enumerate(decline_templates)]
            forms['decline'] = decline_form
            forms['decline_templates'] = json.dumps(decline_templates)

    return forms


def _build_acc_forms(item_id, case_status, dataset_access_list=[]):
    forms = {}

    forms['note'] = NoteForm()

    if case_status == 'Approved':
        forms['close'] = CloseForm()

        if dataset_access_list:
            forms['access'] = _build_dataset_access_form(dataset_access_list)

    return forms


def _build_contact_form(case):
    form = ContactForm()

    if request.args.get('contact_by'):
        form.contactable.data = 'yes'

    return form


def _build_dataset_access_form(dataset_access_list):
    # To dynamically create form fields you need to create class attributes before instanstiation
    for dataset in dataset_access_list:
        DataAccessForm.create_dataset_access_checkboxes(dataset['name'])

    data_access_form = DataAccessForm()

    for dataset in dataset_access_list:
        # Each group of checkboxes (field) is represented as class attribute with dataset name e.g. 'res_cov'
        form_field = getattr(data_access_form, dataset['name'])

        # Get the attribute representing the form field from dataset name
        form_field.choices = []
        form_field.data = []

        # Sort alphabetically but put any 'commercial' licences last
        licences = sorted(
            dataset['licences'].items(),
            key=lambda x: 'z' if '_commercial' in x[0] else x[0]
        )

        for licence_name, licence_dict in licences:
            # Choices is an array of tuples - (checkbox_value, label_value)
            choice = (licence_name, licence_dict['title'])
            form_field.choices.append(choice)

            # Data is an array of checkboxes to be 'checked'
            if licence_dict['agreed']:
                form_field.data.append(licence_name)

            # Temporarily adding disabled attribute to 'licenced' and 'NPS sample' fields
            # subfield_attrs will get picked up in GovIterableBase skeleton code
            if '_sample' in licence_name or '_direct' in licence_name or dataset['name'] == 'licenced':
                render_kw = getattr(form_field, 'render_kw', {}) or {}

                if render_kw.get('subfield_attrs'):
                    render_kw['subfield_attrs'][licence_name] = {'disabled': True}
                else:
                    render_kw['subfield_attrs'] = {}
                    render_kw['subfield_attrs'][licence_name] = {'disabled': True}

                form_field.render_kw = render_kw

    return data_access_form
