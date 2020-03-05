from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, SelectField, SubmitField, RadioField, TextField, SelectMultipleField
from wtforms.validators import InputRequired, ValidationError
from verification_ui.custom_extensions.wtforms_helpers.wtforms_widgets import (GovTextArea,
                                                                               GovSelect,
                                                                               GovSubmitInput,
                                                                               GovRadioInput,
                                                                               GovTextInput,
                                                                               GovCheckboxesInput)


def _contact_validator(form, field):
    contactable = form.contactable.data == 'yes'
    if contactable and len(field.data) == 0:
        raise ValidationError('Choose one option')

    if not contactable and len(field.data):
        raise ValidationError('You can only select an option if user wants to take part in research')


class NoteForm(FlaskForm):
    note_text = TextAreaField('Enter the text for your note',
                              widget=GovTextArea(),
                              validators=[InputRequired(message='Note text is required')]
                              )

    note_button = SubmitField('Add note', widget=GovSubmitInput())


class DeclineForm(FlaskForm):
    decline_template = SelectField('Common decline reasons',
                                   widget=GovSelect()
                                   )

    decline_reason = TextAreaField('Decline reason text',
                                   widget=GovTextArea(),
                                   validators=[InputRequired(message='Please enter a decline reason')]
                                   )

    decline_advice = TextAreaField('Decline next steps',
                                   widget=GovTextArea(),
                                   validators=[InputRequired(message='Please enter next steps')]
                                   )

    template_button = SubmitField('Add text', widget=GovSubmitInput())

    decline_button = SubmitField('Decline', widget=GovSubmitInput())


class CloseForm(FlaskForm):
    close_requester = RadioField('Who requested to close this account?',
                                 widget=GovRadioInput(),
                                 choices=[('customer', 'Customer'), ('hmlr', 'HMLR')]
                                 )

    close_reason = TextAreaField('Explain the reason for closing this account',
                                 widget=GovTextArea(),
                                 validators=[InputRequired(message='Please enter a reason for closing this account')]
                                 )

    close_button = SubmitField('Close account', widget=GovSubmitInput())


class DataAccessForm(FlaskForm):
    @classmethod
    def create_dataset_access_checkboxes(cls, field_name):
        setattr(cls, field_name, SelectMultipleField('', widget=GovCheckboxesInput()))

    access_button = SubmitField('Update account', widget=GovSubmitInput())


class SearchForm(FlaskForm):
    first_name = TextField('First name', widget=GovTextInput())
    last_name = TextField('Last name', widget=GovTextInput())
    organisation_name = TextField('Organisation name', widget=GovTextInput())
    email = TextField('Email', widget=GovTextInput())

    search_button = SubmitField('Search', widget=GovSubmitInput())


class ContactForm(FlaskForm):
    contactable = RadioField('Would the user like to take part in research?',
                             widget=GovRadioInput(),
                             choices=[('yes', 'Yes'), ('no', 'No')]
                             )

    contact_preferences = SelectMultipleField('How should we contact the user?',
                                              widget=GovCheckboxesInput(),
                                              choices=[('telephone', 'Telephone'),
                                                       ('email', 'Email'),
                                                       ('post', 'Post')],
                                              validators=[_contact_validator])

    save_button = SubmitField('Save', widget=GovSubmitInput())
