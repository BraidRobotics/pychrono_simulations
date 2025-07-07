from flask import Flask, render_template, request, redirect, url_for, flash
import logging

from experiments import run_experiments, run_no_experiment

from database.experiment_series_queries import select_all_experiment_series, select_experiment_series_by_name, is_experiment_series_name_unique, \
    insert_experiment_series, update_experiment_series, delete_experiment_series
from database.experiments_queries import select_all_experiments_by_series_name, delete_experiments_by_series_name


log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__, template_folder="templates")

app.secret_key = "this will never be deployed anywy to production so no harm in pushing the secret key"


##########################################################################################
# Pages
##########################################################################################

@app.route("/")
def index_page():
    experiment_series = select_all_experiment_series()
    return render_template(
        "frontpage/frontpage.html",
        experiment_series=experiment_series
    )

@app.route("/experiments/<experiment_series_name>", methods=["GET"])
def experiments_page(experiment_series_name):
    experiment_series = select_experiment_series_by_name(experiment_series_name)
    experiments = select_all_experiments_by_series_name(experiment_series_name)
    return render_template(
        "experiments/experiments.html",
        experiment_series=experiment_series,
        experiments=experiments
    )


##########################################################################################
# API Routes Experiment Series
##########################################################################################

@app.route("/api/experiment_series", methods=["GET"])
def get_experiment_series():
    experiment_series = select_all_experiment_series()
    return {"experiment_series": experiment_series}, 200

@app.route("/api/experiment_series", methods=["POST"])
def create_experiment_series_route():
    experiment_series_name = request.form.get("experiment_series_name")
    
    if not is_experiment_series_name_unique(experiment_series_name):
        flash(f"Experiment series name '{experiment_series_name}' already exists.", "error")
        return redirect(url_for('index_page'))
    
    experiment_series = insert_experiment_series(experiment_series_name)
    run_no_experiment(experiment_series)

    return redirect(url_for("experiments_page", experiment_series_name=experiment_series_name))


@app.route("/api/experiment_series/<experiment_series_name>", methods=["PATCH"])
def update_experiment_series_route(experiment_series_name):
    experiment_series = update_experiment_series(experiment_series_name, request.get_json())
    run_no_experiment(experiment_series)

    return {"status": "success", "message": f"Updated experiment series {experiment_series_name}"}, 200

# uses POST since HTML forms do not support the DELETE method
@app.route("/api/experiment_series/delete/<experiment_series_name>", methods=["POST"])
def delete_experiment_series_route(experiment_series_name):
    delete_experiment_series(experiment_series_name)

    flash(f"Experiment series with name {experiment_series_name} has been deleted.", "success")

    return redirect(url_for('index_page'))


##########################################################################################
# API Routes Experiments
##########################################################################################

@app.route("/api/experiments/all/<experiment_series_name>", methods=["POST"])
def run_experiments_route(experiment_series_name):
    delete_experiments_by_series_name(experiment_series_name) 

    # todo delete image if it exists

    experiment_series = select_experiment_series_by_name(experiment_series_name)
    run_experiments(experiment_series)

    return redirect(url_for("experiments_page", experiment_series_name=experiment_series_name))

@app.route("/api/experiments/single/<experiment_series_name>", methods=["POST"])
def run_single_experiment_route():
    print("todo: run single experiment (visual mode or not, photo / video) defined in the url path variables")

