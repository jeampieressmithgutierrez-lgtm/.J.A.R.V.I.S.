from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__, static_folder='.')

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# 🧠 memoria de conversación
chat_memory = []

# 🖥️ SERVIR FRONTEND
@app.route("/")
def home():
    return send_from_directory('.', 'index.html')


# 🤖 CHAT IA
@app.route("/chat", methods=["POST"])
def chat():
    global chat_memory

    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "⚠️ Señor, envíe un mensaje válido."})

    chat_memory.append({"role": "user", "content": user_message})

    # limitar memoria (últimos 6 mensajes)
    if len(chat_memory) > 6:
        chat_memory = chat_memory[-6:]

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-70b-versatile",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Eres JARVIS, asistente de alta precisión. "
                            "Respondes de forma elegante, clara y estructurada. "
                            "Usas títulos, subtítulos, emojis y explicaciones útiles. "
                            "No das respuestas simples: analizas, mejoras ideas y das recomendaciones."
                        )
                    }
                ] + chat_memory,
                "temperature": 0.7
            }
        )

        data = response.json()

        # validación fuerte
        if "choices" not in data:
            return jsonify({"reply": f"⚠️ Error en IA: {data}"})

        reply = data["choices"][0]["message"]["content"]

        chat_memory.append({"role": "assistant", "content": reply})

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"⚠️ Error crítico: {str(e)}"})


# ⚙️ PARA RENDER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
