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


@blueprint.route("/", methods=["GET", "POST"])
def home():
    form = SurveyForm(request.form)
    if form.validate_on_submit():
        submit_to_sheet(form.data)
        return redirect("/thankyou")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(
                    "Error in the %s field - %s"
                    % (getattr(form, field).label.text, error),
                    "error",
                )
    return render_template("forms/survey.html", form=form)


@blueprint.route("/thankyou", methods=["GET"])
def thankyou():
    return render_template("pages/thankyou_template.html")


def submit_to_sheet(data):
    del data["csrf_token"]

    for x in [
        "School",
        "Name",
        "Email",
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
    data["Name"] = encrypt_string(data["Name"].strip().lower())
    data["Closest 1"] = encrypt_string(data["Closest 1"].strip().lower())
    data["Closest 2"] = encrypt_string(data["Closest 2"].strip().lower())
    data["Closest 3"] = encrypt_string(data["Closest 3"].strip().lower())
    if "Email" in data:
        email = data["Email"]
        write_to_sheet(f"{data['School']} Emails", [email])
        data["Email"] = encrypt_string(data["Email"].strip().lower())
    submit_to_survey(data)


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
