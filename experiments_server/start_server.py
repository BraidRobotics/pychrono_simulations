from experiments_server import app

def start_server():
    app.run(debug=True, port=8000)
    