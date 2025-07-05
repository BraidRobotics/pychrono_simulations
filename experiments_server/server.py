from flask import Flask, render_template

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__, template_folder="templates")

@app.route("/")
def index_page():
    return render_template(
        "frontpage/frontpage.html",
    )

@app.route("/experiments", methods=["GET"])
def experiments_page():
    return render_template(
        "experiments/experiments.html",
    )


