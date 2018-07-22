import time
from flask import Flask, jsonify
import socket

app = Flask("my_app")
started_at = time.ctime()


@app.route("/")
def main_page():
    return "Hello World"


@app.route("/hostname")
def get_hostname():
    return str(socket.gethostname()) + "\n"


@app.route("/health")
def health():
    return jsonify(started_at=started_at)


if __name__ == "__main__":
    app.run("0.0.0.0", 80)
