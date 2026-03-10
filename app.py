from flask import Flask, render_template, request, redirect, session, url_for
from flask_socketio import SocketIO
import random
import string
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "mysecretkey"

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="eventlet"
)


def generate_guest_name():
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"Guest{suffix}"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username", "").strip()

        if not username:
            username = generate_guest_name()

        session["username"] = username
        return redirect(url_for("chat"))

    return render_template("index.html")


@app.route("/chat")
def chat():
    username = session.get("username")

    if not username:
        username = "hi"
        session["username"] = username

    return render_template("chat.html", username=username)


@socketio.on("join_chat")
def handle_join(data):
    username = data.get("username", "Guest")

    socketio.emit("chat_message", {
        "username": "System",
        "text": f"{username} joined the chat"
    })


@socketio.on("send_chat_message")
def handle_send_message(data):
    username = data.get("username", "Guest")
    text = data.get("text", "").strip()

    if not text:
        return

    print("Message received:", {"username": username, "text": text})

    socketio.emit("chat_message", {
        "username": username,
        "text": text
    })


@socketio.on("leave_chat")
def handle_leave(data):
    username = data.get("username", "Guest")

    socketio.emit("chat_message", {
        "username": "System",
        "text": f"{username} left the chat"
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=True)