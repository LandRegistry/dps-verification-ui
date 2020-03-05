from datetime import datetime
from flask import session, render_template_string
from collections import namedtuple


def build_row(item, for_search=False):
    row = [
        {'text': format_date(item['date_added'])},
        {'text': format_name(item)},
        {'html': format_status(item['status'])},
        {'html': format_details(item, for_search)},
        {'html': format_lock(item)}
    ]

    if for_search:
        row.insert(1, {'text': format_account_type(item)})

    return row


def build_details_table(item):
    Row = namedtuple('Row', 'key, type, value, ')

    rows = [
        Row('Full Name', 'text', format_name(item)),
        Row('Status', 'html', format_status(item['status'])),
        Row('Address', 'html', format_address(item)),
        Row('Telephone Number', 'text', item['registration_data']['telephone_number']),
        Row('Email', 'text', item['registration_data']['email']),
        Row('Contactable', 'html', format_contactable(item))
    ]

    if format_contact_by(item):
        rows.append(Row('Contact by', 'html', format_contact_by(item)))

    rows.append(Row('Account Type', 'text', format_account_type(item)))

    user_type = item['registration_data']['user_type']
    if 'organisation' in user_type:
        rows.append(Row('Organisation Name', 'text', item['registration_data']['organisation_name']))

    if user_type == 'organisation-uk':
        org_type = item['registration_data']['organisation_type']
        rows.append(Row('Organisation Type', 'text', org_type))

        if org_type == 'Company' or org_type == 'Charity':
            rows.append(Row('Registration Number', 'text', item['registration_data']['registration_number']))

    if user_type == 'organisation-overseas':
        rows.append(Row('Country of Incorporation', 'text', item['registration_data']['country_of_incorporation']))

    item_info = [{
        'key': {'text': row.key},
        'value': {row.type: row.value},
        'actions': {'items': []}
    } for row in rows]

    return item_info


def format_date(date):
    datetime_added = datetime.strptime(date[:25], '%Y-%m-%d %H:%M:%S.%f')
    return datetime_added.strftime('%d/%m/%Y')


def format_text_date(date):
    datetime_added = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')
    return datetime_added.strftime('%d %B %Y')


def format_date_and_time(date):
    datetime_added = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')
    return datetime_added.strftime('%d %B %Y %H:%M')


def format_file_name(file_name):
    if 'COU' in file_name:
        return 'Change only'
    elif 'FULL' in file_name:
        return 'Full dataset'
    elif 'SAMPLE' in file_name:
        return 'Sample dataset'
    else:
        return file_name


def format_account_type(item):
    acc_type = item['registration_data']['user_type']

    valid_acc_types = {'organisation-uk': 'UK Organisation',
                       'organisation-overseas': 'Overseas Organisation',
                       'personal-uk': 'UK Personal',
                       'personal-overseas': 'Overseas Personal'}

    return valid_acc_types.get(acc_type, acc_type)


def format_name(item):
    arg_list = [
        item['registration_data']['title'],
        item['registration_data']['first_name'],
        item['registration_data']['last_name']
    ]
    return ''.join('{} '.format(arg) for arg in arg_list if arg != '').strip()


def format_address(item):
    if item['registration_data']['user_type'] == 'personal-overseas':
        country = item['registration_data']['country']
    else:
        country = ''
    arg_list = [
        item['registration_data']['address_line_1'],
        item['registration_data']['address_line_2'],
        item['registration_data']['city'],
        item['registration_data']['postcode'],
        country
    ]
    return ''.join('{}<br>'.format(arg) for arg in arg_list if arg != '')


def format_contactable(item):
    contactable = item['registration_data']['contactable']
    contactable_text = 'Yes' if contactable else 'No'

    return render_template_string(
        contactable_text +
        '<a href="/verification/worklist/{}/contact_preferences"'
        'class="govuk-link govuk-summary-list__actions--inline">'
        'Change</a>'.format(item['case_id']))


def format_contact_by(item):
    prefs = item['registration_data']['contact_preferences']
    text = ''.join('{}<br>'.format(pref.capitalize()) for pref in prefs)

    if not text:
        return None

    return render_template_string(
        '<a href="/verification/worklist/{}/contact_preferences?contact_by=true"'
        'class="govuk-link govuk-summary-list__actions--inline">'
        'Change</a>'.format(item['case_id'])
        + text)


def format_note_metadata(note_metadata):
    note_datetime = datetime.strptime(note_metadata['date_added'][:25], '%Y-%m-%d %H:%M:%S.%f')
    note_formatted_datetime = note_datetime.strftime('%d/%m/%Y %H:%M:%S')
    return 'Added by {} on {}'.format(note_metadata['staff_id'], note_formatted_datetime)


def format_status(status):
    status_class = "status-pending"
    if status == "Pending":
        status_class = "status-pending"
    elif status == "In Progress":
        status_class = "status-in-progress"
    elif status == "Approved":
        status_class = "status-approved"
    elif status == "Declined":
        status_class = "status-declined"

    return '<span class="{}">{}</span>'.format(status_class, status)


def format_details(item, for_search=False):
    query_string = '?from=search' if for_search else ''
    html = '<a class="govuk-link" href="/verification/worklist/{}{}">View details</a>'.format(
           item['case_id'],
           query_string)
    return html


def format_lock(item):
    if item['staff_id'] is None or item['status'] not in ['Pending', 'In Progress']:
        return ''

    if item['staff_id'] == session['username']:
        colour = 'green'
        locked_to = 'Locked to you'
    else:
        colour = 'red'
        locked_to = item['staff_id']

    return '''<div class="pill-box pill-box-{}">
        <svg xmlns="http://www.w3.org/2000/svg" height="20" viewBox="0 0 24 24" fill="none"
            stroke="#ffffff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
            <rect x="4" y="11" width="15.5" height="11" rx="2" ry="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
        </svg>
        <span>{}</span>
    </div>'''.format(colour, locked_to)


def build_dataset_activity(dataset_activity):
    # As sample downloads should be displayed under the full dataset, we need to copy the download history
    # for the sample dataset into the full download history and then remove the sample dataset from the list
    download_activity = list(dataset_activity)

    for dataset in download_activity:
        if dataset['private'] is True:
            sample_dataset_index = next((index for (index, item) in enumerate(download_activity)
                                         if item['name'] == '{}_sample'.format(dataset['name'])), None)
            if sample_dataset_index is not None:
                dataset['download_history'] += download_activity[sample_dataset_index]['download_history']
                dataset['sample_licence_agreed'] = download_activity[sample_dataset_index]['licence_agreed']
                del download_activity[sample_dataset_index]

    # Need to construct the html content that will be revealed when the accordion elements are expanded however
    # a restricted datset may not have an agreed licence but still have a history of sample downloads
    activity = dict(download_count=0, datasets=list())
    oldest_download_date = datetime.now()

    for dataset in download_activity:
        if dataset['licence_agreed'] or dataset['download_history']:
            # When a user has agreed the licence for a free dataset a licence_agreed_date will be present
            # however the licence agreement for restricted datasets is an offline process and so won't have a date
            if dataset['licence_agreed'] and 'licence_agreed_date' in dataset:
                licence_agreed = 'Licence agreed on {}'.format(format_text_date(dataset['licence_agreed_date']))
            elif dataset['licence_agreed']:
                licence_agreed = 'Licence has been agreed'
            elif 'sample_licence_agreed' in dataset and dataset['sample_licence_agreed'] is True:
                licence_agreed = 'Sample licence has been agreed'
            else:
                licence_agreed = 'Licence has not been agreed'

            if dataset['download_history']:
                content = '<table class="govuk-table govuk-!-margin-top-3 govuk-!-margin-bottom-6">' \
                          '<thead class="govuk-table__head"><tr class="govuk-table__row">' \
                          '<th scope="col" class="govuk-table__header">Type of dataset</th>' \
                          '<th scope="col" class="govuk-table__header">Date/time downloaded</th>' \
                          '</tr></thead><tbody class="govuk-table__body">'

                for download in dataset['download_history']:
                    activity['download_count'] += 1

                    # Need to determine when the oldest download happened so that we can provide
                    # a rough date range for the frontend
                    curr_download_date = datetime.strptime(download['date'], '%Y-%m-%dT%H:%M:%S.%f')
                    if curr_download_date < oldest_download_date:
                        oldest_download_date = curr_download_date

                    download_file = format_file_name(download['file'])
                    download_date = format_date_and_time(download['date'])

                    content += '<tr class="govuk-table__row">' \
                               '<td scope="row" class="govuk-table__cell">{}</td>' \
                               '<td class="govuk-table__cell">{}</td>' \
                               '</tr>'.format(download_file, download_date)

                content += '</tbody></table>'
            else:
                content = '<p class="govuk-body govuk-!-margin-top-3 govuk-!-margin-bottom-6">This account has ' \
                          'not downloaded any files for this dataset.</p>'

            activity['datasets'].append({
                'heading': {
                    'text': dataset['title']
                },
                'summary': {
                    'text': licence_agreed
                },
                'content': {
                    'html': content
                }
            })

        activity['oldest_download_date'] = format_text_date(datetime.strftime(oldest_download_date,
                                                                              '%Y-%m-%dT%H:%M:%S.%f'))

    return activity
