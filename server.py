from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
import os

app = Flask(__name__, static_folder='.')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 🧠 MODELOS EN CASCADA (anti-decomiso)
MODELS = [
    "llama3-70b-8192",   # principal
    "llama3-8b-8192",    # respaldo rápido
    "gemma2-9b-it"       # respaldo alternativo
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
        return jsonify({"reply": "⚠️ Señor, escriba algo válido."})

    chat_memory.append({"role": "user", "content": user_message})

    # limitar memoria
    if len(chat_memory) > 6:
        chat_memory = chat_memory[-6:]

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
                            "Eres JARVIS, asistente elegante, directo y analítico. "
                            "Respondes con estructura clara, usando títulos, emojis y explicaciones útiles. "
                            "Das recomendaciones y mejoras las ideas del usuario."
                        )
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
        "reply": "⚠️ Señor, todos los modelos fallaron. Intente nuevamente.",
        "error": last_error
    })


# 🚀 RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
