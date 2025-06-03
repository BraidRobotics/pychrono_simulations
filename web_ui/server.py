from flask import Flask, request, jsonify
from flask import render_template
from multiprocessing import Value
from config import braided_structure_config

app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    with braided_structure_config.lock:
        return render_template(
            "index.html",
            num_strands=braided_structure_config.num_strands,
            radius=braided_structure_config.radius,
            pitch=braided_structure_config.pitch,
            num_layers=braided_structure_config.num_layers
        )

@app.route("/set_param", methods=["POST"])
def set_param():
    data = request.get_json()
    with braided_structure_config.lock:
        if "num_strands" in data:
            braided_structure_config.num_strands = float(data["num_strands"])
        if "radius" in data:
            braided_structure_config.radius = float(data["radius"])
        if "pitch" in data:
            braided_structure_config.pitch = float(data["pitch"])
        if "num_layers" in data:
            braided_structure_config.num_layers = int(data["num_layers"])
        braided_structure_config.rebuild_requested = True
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(debug=False, port=5000)