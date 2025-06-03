import threading
import subprocess


def start_server():
    threading.Thread(target=create_flask_thread, daemon=True).start()


def create_flask_thread():
    try:
        subprocess.run(["python", "web_ui/server.py"], check=True)
    except subprocess.CalledProcessError as error:
        print(f"Error running server: {error}")

