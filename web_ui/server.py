from flask import Flask, request, jsonify
from flask import render_template
from multiprocessing import Value

app = Flask(__name__, template_folder="templates")
param = Value('d', 0.0)  # shared float value

@app.route("/")
def index():
    with param.get_lock():
        current_value = param.value
    return render_template("index.html", num_strands=current_value)

@app.route("/set_param", methods=["POST"])
def set_param():
    data = request.get_json()
    new_value = float(data.get("num_strands", 0.0))
    with param.get_lock():
        param.value = new_value
    return jsonify({"status": "ok", "num_strands": param.value})

if __name__ == "__main__":
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(debug=False, port=5000)