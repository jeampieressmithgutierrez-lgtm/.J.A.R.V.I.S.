from flask import Flask, request, jsonify
import os
from groq import Groq

app = Flask(__name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route("/")
def home():
    return "Servidor activo, Señor."

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    mensaje = data.get("mensaje")

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Responde como JARVIS, elegante y directo."},
                {"role": "user", "content": mensaje}
            ]
        )

        respuesta = response.choices[0].message.content

        return jsonify({"respuesta": respuesta})

    except Exception as e:
        return jsonify({"error": str(e)})
