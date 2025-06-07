from flask import Flask, request, jsonify
from flask import render_template
from config import braided_structure_config

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    snapshot = braided_structure_config.get_snapshot()
    return render_template(
        "index.html",
        num_strands=snapshot["num_strands"],
        radius=snapshot["radius"],
        pitch=snapshot["pitch"],
        num_layers=snapshot["num_layers"]
    )

@app.route("/set_param", methods=["POST"])
def set_param():
    data = request.get_json()
    update_data = {}
    if "num_strands" in data:
        update_data["num_strands"] = float(data["num_strands"])
    if "radius" in data:
        update_data["radius"] = float(data["radius"])
    if "pitch" in data:
        update_data["pitch"] = float(data["pitch"])
    if "num_layers" in data:
        update_data["num_layers"] = int(data["num_layers"])
    update_data["rebuild_requested"] = True
    braided_structure_config.update(**update_data)
    return jsonify({"status": "ok"})