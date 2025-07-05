from flask import Flask, render_template, request, redirect, url_for, flash
import logging
from database import select_all_experiment_series, select_experiment_series_by_name, is_experiment_series_name_unique, \
    insert_experiment_series, select_all_experiments_by_series_id

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
    return render_template(
        "experiments/experiments.html",
        experiment_series=experiment_series,
    )


##########################################################################################
# API Routes Experiment Series
##########################################################################################

@app.route("/api/experiment_series", methods=["GET"])
def get_experiment_series():
    experiment_series = select_all_experiment_series()
    return {"experiment_series": experiment_series}, 200

@app.route("/api/experiment_series/<int:experiment_series_id>", methods=["GET"])
def get_experiment_series_by_id(experiment_series_id):
    ...
    # experiment_series = select_experiment_series_by_id(experiment_series_id)
    # if not experiment_series:
    #     return {"error": "Experiment series not found"}, 404
    
    # experiments = select_all_experiments_by_series_id(experiment_series_id)
    # return {
    #     "experiment_series": experiment_series,
    #     "experiments": experiments
    # }, 200

@app.route("/api/experiment_series", methods=["POST"])
def create_experiment_series():
    experiment_series_name = request.form.get("experiment_series_name")
    
    if not is_experiment_series_name_unique(experiment_series_name):
        flash(f"Experiment series name '{experiment_series_name}' already exists.", "error")
        return redirect(url_for('index_page'))
    
    experiment_series_id = insert_experiment_series(experiment_series_name)

    return redirect(url_for("experiments_page", experiment_series_name=experiment_series_name, experiment_series_id=experiment_series_id))



@app.route("/api/experiment_series/<int:experiment_series_id>", methods=["PUT"])
def update_experiment_series(experiment_series_id):
    print(f"todo: update experiment series with ID: {experiment_series_id}")
    return {"status": "success", "message": f"Updated experiment series {experiment_series_id}"}, 200

@app.route("/api/experiment_series/<int:experiment_series_id>/delete", methods=["DELETE"])
def delete_experiment_series(experiment_series_id):
    print(f"todo: delete all experiments in series with ID: {experiment_series_id}")
    return {"status": "success", "message": f"Deleted all experiments in series {experiment_series_id}"}, 200


##########################################################################################
# API Routes Experiments
##########################################################################################

@app.route("/api/experiments/all/<int:experiment_series_id>", methods=["POST"])
def run_experiments():
    print("todo: run all experiments in the series")

@app.route("/api/experiments/single/<int:experiment_id>", methods=["POST"])
def run_single_experiment():
    print("todo: run single experiment (visual mode or not, photo / video) defined in the url path variables")

@app.route("/api/experiments/<int:experiment_series_id>/delete", methods=["DELETE"])
def delete_all_experiments_in_series(experiment_series_id):
    print(f"todo: delete experiment with ID: {experiment_series_id}")
    return {"status": "success", "message": f"Deleted experiment {experiment_series_id}"}, 200
