from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Variables de entorno
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

@app.route("/")
def home():
    return "Servidor activo señor."

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    mensaje = data.get("message", "").lower()

    # 🌦️ Si pregunta por clima
    if "clima" in mensaje:
        ciudad = "Bogotá"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={WEATHER_API_KEY}&units=metric&lang=es"
        
        res = requests.get(url).json()

        if res.get("main"):
            temp = res["main"]["temp"]
            desc = res["weather"][0]["description"]
            return jsonify({
                "response": f"En {ciudad} hay {desc} con {temp}°C."
            })
        else:
            return jsonify({"response": "No pude obtener el clima, señor."})

    # 🤖 IA con GROQ
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "Responde como Jarvis, elegante y directo."},
            {"role": "user", "content": mensaje}
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        respuesta = response.json()["choices"][0]["message"]["content"]
        return jsonify({"response": respuesta})
    else:
        return jsonify({"response": "Error con la IA, señor."})


if __name__ == "__main__":
    app.run(debug=True)
