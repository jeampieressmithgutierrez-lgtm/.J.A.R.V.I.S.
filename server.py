from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
import os

app = Flask(__name__)

# 🔑 Cliente Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 🌐 Página principal
@app.route("/")
def home():
    return send_from_directory(".", "index.html")

# 🤖 Chat IA real
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    mensaje = data.get("message", "")

    if not mensaje:
        return jsonify({"reply": "Señor, no recibí ningún mensaje."})

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Eres JARVIS, un asistente elegante, preciso y directo."},
                {"role": "user", "content": mensaje}
            ]
        )

        respuesta = completion.choices[0].message.content

        return jsonify({"reply": respuesta})

    except Exception as e:
        return jsonify({"reply": f"Error en IA: {str(e)}"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
