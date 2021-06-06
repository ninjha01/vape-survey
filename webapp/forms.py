import re
import random
from flask_wtf import Form
from wtforms import TextField, IntegerField, SelectField
from wtforms.validators import DataRequired, EqualTo, Length, Regexp, NumberRange
from .models import (
    Question,
    SelectQuestion,
    IntegerQuestion,
    load_from_yaml,
    load_winners_from_yaml,
)


def question_to_field(q: Question):
    validators = []
    if q.required:
        validators.append(DataRequired())
    if q.regexp:
        validators.append(Regexp(q.regexp, message=q.regexp_message))
    if isinstance(q, SelectQuestion):
        choices = [(x, x) for x in q.choices]
        return SelectField(
            description=q.description,
            label=q.label,
            choices=[("", "")] + choices,
            validators=validators,
            render_kw={"class": "form-control"},
        )
    elif isinstance(q, IntegerQuestion):
        return IntegerField(
            description=q.description,
            label=q.label,
            validators=validators
            + [
                NumberRange(
                    min=18, max=21, message="Enter a valid number between 18 and 21."
                )
            ],
            render_kw={"class": "form-control"},
        )
    else:  # Basic text question
        return TextField(
            description=q.description,
            label=q.label,
            validators=validators,
            render_kw={"class": "form-control"},
        )


questions = load_from_yaml()


class SurveyForm(Form):
    questions = questions


for q in questions:
    setattr(SurveyForm, q.label, question_to_field(q))


def get_code_for_winner(identifier, password):
    winning_identifiers = load_winners_from_yaml()
    if identifier not in winning_identifiers:
        return None
    if password != winning_identifiers[identifier]["password"]:
        return None
    return winning_identifiers[identifier]["code"]


class WinnerForm(Form):
    winning_identifiers = load_winners_from_yaml()
    identifier_select = SelectField(
        description="Winning Identifiers",
        label="Winning Identifiers",
        choices=[("", "")] + [(k, k) for k in winning_identifiers.keys()],
        validators=[DataRequired()],
        render_kw={"class": "form-control"},
    )
    password_field = TextField(
        description="Enter the password you were given when you submitted the survey",
        label="Password",
        validators=[DataRequired()],
        render_kw={"class": "form-control"},
    )
