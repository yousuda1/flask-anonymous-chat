from flask import Flask, render_template, request, redirect, session, url_for
from flask_socketio import SocketIO
import random
import string

app = Flask(__name__)
app.config["SECRET_KEY"] = "mysecretkey"

socketio = SocketIO(app, cors_allowed_origins="*")


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
        return redirect(url_for("index"))

    return render_template("chat.html", username=username)


@socketio.on("join_chat")
def handle_join(data):
    username = data["username"]
    print(f"{username} joined")

    socketio.emit("chat_message", {
        "username": "System",
        "text": f"{username} joined the chat"
    })


@socketio.on("send_chat_message")
def handle_send_message(data):
    print("Message received:", data)

    socketio.emit("chat_message", {
        "username": data["username"],
        "text": data["text"]
    })


@socketio.on("leave_chat")
def handle_leave(data):
    username = data["username"]
    print(f"{username} left")

    socketio.emit("chat_message", {
        "username": "System",
        "text": f"{username} left the chat"
    })


if __name__ == "__main__":
    socketio.run(app, debug=True)