from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from huggingface_hub import InferenceClient
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pirate_secret'
socketio = SocketIO(app)

# Gunakan token dari environment variable (Render/Heroku)
HF_TOKEN = os.getenv("HF_TOKEN")
client = InferenceClient(model="meta-llama/Llama-3.2-3B-Instruct", token=HF_TOKEN)

chat_history = [
    {"role": "system", "content": "Berbicaralah seperti guru."}
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ping")
def ping():
    return "OK", 200  # Untuk pengecekan uptime/keep alive

@socketio.on("send_message")
def handle_message(data):
    user_input = data["message"]
    chat_history.append({"role": "user", "content": user_input})

    emit("receive_message", {"role": "user", "content": user_input}, broadcast=True)

    response = client.chat_completion(
        messages=chat_history,
        temperature=0.3,
        top_p=0.4
    )

    bot_reply = response.choices[0].message["content"]
    chat_history.append({"role": "assistant", "content": bot_reply})

    emit("receive_message", {"role": "assistant", "content": bot_reply}, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
