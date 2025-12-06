from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash, session, g
import logging
from pathlib import Path

from experiments import run_experiments, run_non_experiment, run_visual_simulation_experiment

from database.queries.experiment_series_queries import select_all_experiment_series, select_all_experiment_series_grouped, select_experiment_series_by_name, is_experiment_series_name_unique, \
    insert_experiment_series_default, update_experiment_series, delete_experiment_series
from database.queries.experiments_queries import select_all_experiments_by_series_name, delete_experiments_by_series_name, select_experiment_by_series_name_and_id
from database.queries.graph_queries import get_strand_radius_vs_weight_chart_values, get_load_capacity_ratio_y_chart_values
from database.session import SessionLocal

from util import delete_experiment_series_folder
from graphs.generate_after_experiments import delete_relevant_graphs



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

    safe_name = experiment_series_name.replace('/', '_').replace(' ', '_')
    force_graph_path = f"series_{safe_name}_force.html"
    height_graph_path = f"series_{safe_name}_height.html"
    elastic_recovery_graph_path = f"series_{safe_name}_elastic_recovery.html"

    graphs_dir = Path(__file__).parent / "assets" / "graphs"
    force_graph_exists = (graphs_dir / force_graph_path).exists()
    height_graph_exists = (graphs_dir / height_graph_path).exists()
    elastic_recovery_graph_exists = (graphs_dir / elastic_recovery_graph_path).exists()

    if experiment_series.is_experiments_outdated:
        flash(f"The experiments are outdated (experiment series config have been changed). Please run the experiments again.", "error")
    return render_template(
        "experiments/experimentsPage.html",
        experiment_series=experiment_series,
        experiment_series_dict=experiment_series_dict,
        experiments=experiments,
        force_graph_path=force_graph_path,
        height_graph_path=height_graph_path,
        elastic_recovery_graph_path=elastic_recovery_graph_path,
        force_graph_exists=force_graph_exists,
        height_graph_exists=height_graph_exists,
        elastic_recovery_graph_exists=elastic_recovery_graph_exists
    )

@app.route("/aggregated_charts", methods=["GET"])
def aggregated_charts_page():
    from database.session import get_session
    from database.queries.graph_queries import get_models_meeting_target_count

    # Graph paths
    load_capacity_graph_path = "load_capacity_ratio_y.html"

    # Get target achievement statistics
    session = get_session()
    target_stats = get_models_meeting_target_count(session)

    return render_template(
        "analysis/aggregatedCharts.html",
        load_capacity_graph_path=load_capacity_graph_path,
        target_stats=target_stats
    )

@app.route("/thickness_analysis", methods=["GET"])
def thickness_analysis_page():
    # Graph paths
    strand_thickness_graph_path = "strand_thickness_vs_weight.html"
    strand_thickness_force_graph_path = "strand_thickness_vs_force.html"
    strand_thickness_efficiency_graph_path = "strand_thickness_vs_efficiency.html"
    thickness_height_reduction_graph_path = "thickness_height_reduction_vs_force.html"

    return render_template(
        "analysis/thicknessAnalysis.html",
        strand_thickness_graph_path=strand_thickness_graph_path,
        strand_thickness_force_graph_path=strand_thickness_force_graph_path,
        strand_thickness_efficiency_graph_path=strand_thickness_efficiency_graph_path,
        thickness_height_reduction_graph_path=thickness_height_reduction_graph_path
    )

@app.route("/layer_analysis", methods=["GET"])
def layer_analysis_page():
    layer_height_reduction_vs_force_path = "layer_height_reduction_vs_force.html"
    layer_height_graph_path = "layer_count_vs_height.html"
    layer_force_graph_path = "layer_count_vs_force.html"
    layer_efficiency_graph_path = "layer_count_vs_efficiency.html"

    return render_template(
        "analysis/layerAnalysis.html",
        layer_height_reduction_vs_force_path=layer_height_reduction_vs_force_path,
        layer_height_graph_path=layer_height_graph_path,
        layer_force_graph_path=layer_force_graph_path,
        layer_efficiency_graph_path=layer_efficiency_graph_path
    )

@app.route("/strands_analysis", methods=["GET"])
def strands_analysis_page():
    strand_height_reduction_vs_force_path = "strand_height_reduction_vs_force.html"
    strand_stiffness_vs_compression_path = "strand_stiffness_vs_compression.html"
    strand_force_vs_displacement_path = "strand_force_vs_displacement.html"
    strand_count_weight_graph_path = "strand_count_vs_weight.html"
    strand_count_force_graph_path = "strand_count_vs_force.html"
    strand_count_efficiency_graph_path = "strand_count_vs_efficiency.html"

    return render_template(
        "analysis/strandsAnalysis.html",
        strand_height_reduction_vs_force_path=strand_height_reduction_vs_force_path,
        strand_stiffness_vs_compression_path=strand_stiffness_vs_compression_path,
        strand_force_vs_displacement_path=strand_force_vs_displacement_path,
        strand_count_weight_graph_path=strand_count_weight_graph_path,
        strand_count_force_graph_path=strand_count_force_graph_path,
        strand_count_efficiency_graph_path=strand_count_efficiency_graph_path
    )

@app.route("/force_no_force_analysis", methods=["GET"])
def force_no_force_analysis_page():
    # Graph paths
    recovery_by_thickness_graph_path = "recovery_by_thickness.html"
    recovery_by_layers_graph_path = "recovery_by_layers.html"
    recovery_by_strands_graph_path = "recovery_by_strands.html"
    recovery_heatmap_thickness_layers_path = "recovery_heatmap_thickness_layers.html"
    parameter_importance_graph_path = "recovery_parameter_importance.html"
    equilibrium_time_graph_path = "equilibrium_time.html"

    return render_template(
        "analysis/forceNoForceAnalysis.html",
        recovery_by_thickness_graph_path=recovery_by_thickness_graph_path,
        recovery_by_layers_graph_path=recovery_by_layers_graph_path,
        recovery_by_strands_graph_path=recovery_by_strands_graph_path,
        recovery_heatmap_thickness_layers_path=recovery_heatmap_thickness_layers_path,
        parameter_importance_graph_path=parameter_importance_graph_path,
        equilibrium_time_graph_path=equilibrium_time_graph_path
    )

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('../assets', filename)

@app.route('/graphs/<path:filename>')
def serve_graphs(filename):
    return send_from_directory('assets/graphs', filename)


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
    g.db.commit()  # Ensure commit before passing to subprocess
    run_non_experiment(experiment_series_name)

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

    g.db.commit()  # Ensure commit before passing to subprocess
    run_non_experiment(experiment_series_name)

    return {"status": "success", "message": f"Updated experiment series {experiment_series_name}"}, 200

# uses POST since HTML forms do not support the DELETE method
@app.route("/api/experiment_series/delete/<experiment_series_name>", methods=["POST"])
def delete_experiment_series_route(experiment_series_name):
    delete_experiment_series(g.db, experiment_series_name)

    delete_experiment_series_folder(experiment_series_name)

    safe_name = experiment_series_name.replace('/', '_').replace(' ', '_')
    delete_relevant_graphs(safe_name)

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
    experiment = select_experiment_by_series_name_and_id(g.db, experiment_series_name, int(experiment_id))

    run_visual_simulation_experiment(experiment_series, experiment)

    return { "status": "success", "message": f"Running the simulation for experiment {experiment_id} in visual mode" }
