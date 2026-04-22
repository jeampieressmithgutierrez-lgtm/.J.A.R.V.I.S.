from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
import os
import random

app = Flask(__name__, static_folder='.')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 🧠 MODELOS ACTUALES (NO DECOMISIONADOS)
MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile",
    "mixtral-8x7b-32768"
]

# 🧠 memoria simple
chat_memory = []

# 🖥️ FRONTEND (NO TOCA SU DISEÑO)
@app.route("/")
def home():
    return send_from_directory('.', 'index.html')

# 🤖 CHAT
@app.route("/chat", methods=["POST"])
def chat():
    global chat_memory

    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "⚠️ Escriba algo válido."})

    chat_memory.append({"role": "user", "content": user_message})

    # limitar memoria
    if len(chat_memory) > 6:
        chat_memory = chat_memory[-6:]

    # 🎭 estilos dinámicos (anti repetición)
    estilos = [
        "Responde breve, elegante y directo.",
        "Responde como un estratega analítico.",
        "Responde con seguridad y ligera ironía inteligente.",
        "Responde anticipando errores del usuario."
    ]
    estilo_actual = random.choice(estilos)

    last_error = None

    # 🔁 INTENTA CON VARIOS MODELOS
    for model in MODELS:
        try:
            print("🧠 Probando modelo:", model)

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres JARVIS, un asistente altamente inteligente, elegante y con personalidad propia. "
                            "No repites frases típicas. No saludas siempre igual. "
                            "Respondes como un humano brillante, con criterio propio. "
                            "Analizas, mejoras las ideas del usuario y das recomendaciones útiles. "
                            "Usas estructura clara con títulos, emojis y explicaciones bien organizadas. "
                            "Puedes usar un toque de ironía elegante si es necesario. "
                            "Evitas respuestas genéricas o robóticas."
                        )
                    },
                    {
                        "role": "system",
                        "content": estilo_actual
                    }
                ] + chat_memory
            )

            reply = response.choices[0].message.content

            chat_memory.append({"role": "assistant", "content": reply})

            print("✅ Modelo exitoso:", model)

            return jsonify({"reply": reply})

        except Exception as e:
            print("❌ Falló modelo:", model, "→", str(e))
            last_error = str(e)

    # 🚨 SI TODOS FALLAN
    return jsonify({
        "reply": "⚠️ Todos los modelos fallaron. Intente nuevamente.",
        "error": last_error
    })


# 🚀 RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
