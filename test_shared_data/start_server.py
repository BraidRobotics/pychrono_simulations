import threading
from server import app



def start_server():
    threading.Thread(target=lambda: app.run(debug=False, port=8000), daemon=True).start()


