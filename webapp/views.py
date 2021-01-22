import json
import functools
import time
import hashlib
import os
import plotly

from flask import (
    render_template,
    Blueprint,
    request,
    redirect,
    flash,
    current_app,
    jsonify,
)

from .forms import SurveyForm
from .sheets import write_to_sheet, get_sheet_data, submit_to_survey, get_schools
from .db import get_db
from .viz import gen_network
from .utils import encrypt_string


blueprint = Blueprint("pages", __name__)
db = None


@blueprint.route("/", methods=["GET"])
def home():
    return render_template("pages/consent_template.html")


@blueprint.route("/survey", methods=["GET", "POST"])
def survey():
    form = SurveyForm(request.form)
    if form.validate_on_submit():
        password = submit_to_sheet_and_gen_password(form.data)
        return render_template("pages/thankyou_template.html", password=password)
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(
                    "Error in the %s field - %s"
                    % (getattr(form, field).label.text, error),
                    "error",
                )
    return render_template("forms/survey.html", form=form)


def submit_to_sheet_and_gen_password(data):
    del data["csrf_token"]

    # TODO Replace w/ Enum
    for x in [
        "School",
        "Name",
        "Age",
        "Grade",
        "Gender",
        "Closest 1",
        "Closest 2",
        "Closest 3",
        "Influence",
        "Vape",
    ]:
        assert x in data

    data["School"] = encrypt_string(data["School"].strip().lower())[:10]

    def normalize_name(name: str) -> str:
        return name.replace("-", "").strip().lower()

    data["Name"] = encrypt_string(normalize_name(data["Name"]))
    data["Closest 1"] = encrypt_string(normalize_name(data["Closest 1"]))
    data["Closest 2"] = encrypt_string(normalize_name(data["Closest 2"]))
    data["Closest 3"] = encrypt_string(normalize_name(data["Closest 3"]))
    if data.get("Closest 4", "") != "":
        data["Closest 4"] = encrypt_string(normalize_name(data["Closest 4"]))
    else:
        data["Closest 4"] = ""
    if data.get("Closest 5", "") != "":
        data["Closest 5"] = encrypt_string(normalize_name(data["Closest 5"]))
    else:
        data["Closest 5"] = ""
    if data.get("Closest 6", "") != "":
        data["Closest 6"] = encrypt_string(normalize_name(data["Closest 6"]))
    else:
        data["Closest 6"] = ""
    if data.get("Closest 7", "") != "":
        data["Closest 7"] = encrypt_string(normalize_name(data["Closest 7"]))
    else:
        data["Closest 7"] = ""

    data["password"] = encrypt_string(data["Name"])[:8]
    submit_to_survey(data)
    return data["password"]


@blueprint.route("/about", methods=["GET"])
def about():
    return render_template("pages/about_template.html")


@blueprint.route("/viz", methods=["GET"])
def viz():
    schools = get_schools()
    return render_template("pages/viz_template.html", schools=schools)


@blueprint.route("/get_graph", methods=["POST"])
def get_graph():
    data = request.get_json(force=True)
    school, force = data.get("school"), data.get("force")
    try:
        return jsonify(
            {"graph": create_graph_if_not_cached(school, force=force), "success": True}
        )
    except Exception as e:
        return jsonify({"error": str(e)})


def create_graph_if_not_cached(school_name, force=False):
    global db
    if not db:
        db = get_db()
    graph, gen_time = db.get_graph_and_gen_time_for_school(school_name)
    if force or gen_time is None or graph is None:
        print("Regenerating")
        data = get_sheet_data(school_name)
        graph = gen_network(data)
        db.set_graph_for_school(school_name, graph)
        return graph
    else:
        print("Cached")
        return graph
