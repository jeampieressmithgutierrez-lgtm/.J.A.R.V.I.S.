from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)

# 🔹 Página principal
@app.route("/")
def home():
    return send_from_directory(".", "index.html")

# 🔹 Chat API
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    mensaje = data.get("message", "")

    # Respuesta base (luego conectamos GROQ)
    return jsonify({
        "reply": f"Señor, recibí su mensaje: {mensaje}"
    })

# 🔹 Arranque servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
