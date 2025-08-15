from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash, session, g
import logging

from experiments import run_experiments, run_non_experiment, run_visual_simulation_experiment

from database.queries.experiment_series_queries import select_all_experiment_series, select_all_experiment_series_grouped, select_experiment_series_by_name, is_experiment_series_name_unique, \
    insert_experiment_series_default, update_experiment_series, delete_experiment_series
from database.queries.experiments_queries import select_all_experiments_by_series_name, delete_experiments_by_series_name, select_experiment_by_series_name_and_id
from database.queries.graph_queries import get_material_thickness_vs_weight_chart_values, get_load_capacity_ratio_y_chart_values
from database.session import SessionLocal

from util import delete_experiment_series_folder

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__, template_folder="templates")

app.secret_key = "this will never be deployed anywy to production so no harm in pushing the secret key"

@app.before_request
def create_session():
	g.db = SessionLocal()

@app.teardown_appcontext
def teardown_session(exception=None):
	db = g.pop('db', None)
	if db is not None:
		db.close()


##########################################################################################
# Pages 
##########################################################################################

@app.route("/")
def index_page():
    grouped_experiment_series = select_all_experiment_series_grouped(g.db)
    
    return render_template(
        "frontpage/frontpage.html",
        grouped_experiment_series=grouped_experiment_series
    )

@app.route("/experiments/<experiment_series_name>", methods=["GET"])
def experiments_page(experiment_series_name):
    experiment_series = select_experiment_series_by_name(g.db, experiment_series_name)
    experiment_series_dict = {key: value for key, value in experiment_series.__dict__.items() if key != "_sa_instance_state"}
    experiments_raw = select_all_experiments_by_series_name(g.db, experiment_series_name)
    experiments = [
        {key: value for key, value in experiment.__dict__.items() if key != "_sa_instance_state"}
        for experiment in experiments_raw
    ]
    if experiment_series.is_experiments_outdated:
        flash(f"The experiments are outdated (experiment series config have been changed). Please run the experiments again.", "error")
    return render_template(
        "experiments/experimentsPage.html",
        experiment_series=experiment_series,
        experiment_series_dict=experiment_series_dict,
        experiments=experiments
    )

@app.route("/aggregated_charts", methods=["GET"])
def aggregated_charts_page():
    material_thickness_vs_weight_chart_values = get_material_thickness_vs_weight_chart_values(g.db)
    load_capacity_ratio_y_chart_values = get_load_capacity_ratio_y_chart_values(g.db)
    return render_template(
        "aggregatedChartsPage/aggregatedChartsPage.html",
        material_thickness_vs_weight_chart_values=material_thickness_vs_weight_chart_values,
        load_capacity_ratio_y_chart_values=load_capacity_ratio_y_chart_values
    )

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('../assets', filename)


##########################################################################################
# API Routes Experiment Series
##########################################################################################

@app.route("/api/experiment_series", methods=["GET"])
def get_experiment_series():
    experiment_series = select_all_experiment_series(g.db)
    return {"experiment_series": experiment_series}, 200

@app.route("/api/experiment_series", methods=["POST"])
def create_experiment_series_route():
    experiment_series_name = request.form.get("experiment_series_name")
    
    if not is_experiment_series_name_unique(g.db, experiment_series_name):
        flash(f"Experiment series name '{experiment_series_name}' already exists.", "error")
        return redirect(url_for('index_page'))
    
    experiment_series = insert_experiment_series_default(g.db, experiment_series_name)
    run_non_experiment(experiment_series)

    return redirect(url_for("experiments_page", experiment_series_name=experiment_series_name))


@app.route("/api/experiment_series/<experiment_series_name>", methods=["PATCH"])
def update_experiment_series_route(experiment_series_name):
    body = request.get_json()
    body["is_experiments_outdated"] = True
    experiment_series, errors = update_experiment_series(g.db, experiment_series_name, body)
    if experiment_series is None:
        for message in errors:
            flash(message, "error")
        return {"status": "error", "message": errors[0]}, 400

    run_non_experiment(experiment_series)

    return {"status": "success", "message": f"Updated experiment series {experiment_series_name}"}, 200

# uses POST since HTML forms do not support the DELETE method
@app.route("/api/experiment_series/delete/<experiment_series_name>", methods=["POST"])
def delete_experiment_series_route(experiment_series_name):
    delete_experiment_series(g.db, experiment_series_name)

    delete_experiment_series_folder(experiment_series_name)

    flash(f"Experiment series with name {experiment_series_name} has been deleted.", "success")

    return redirect(url_for('index_page'))


##########################################################################################
# API Routes Experiments
##########################################################################################

@app.route("/api/experiments/all/<experiment_series_name>", methods=["POST"])
def run_all_experiments_route(experiment_series_name):
    delete_experiments_by_series_name(g.db, experiment_series_name) 

    update_experiment_series(g.db, experiment_series_name, { "is_experiments_outdated": False })
    session.pop('_flashes', None)

    experiment_series = select_experiment_series_by_name(g.db, experiment_series_name)
    run_experiments(experiment_series)

    return redirect(url_for("experiments_page", experiment_series_name=experiment_series_name))

@app.route("/api/experiments/visualize_single/<experiment_series_name>/<experiment_id>", methods=["POST"])
def run_single_experiment_route(experiment_series_name, experiment_id):
    experiment_series = select_experiment_series_by_name(g.db, experiment_series_name)
    experiment = select_experiment_by_series_name_and_id(g.db, experiment_series_name, experiment_id)

    run_visual_simulation_experiment(experiment_series, experiment)
    
    return { "status": "success", "message": f"Running the simulation for experiment {experiment_id} in visual mode" }
