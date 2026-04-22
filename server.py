from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
import os

app = Flask(__name__, static_folder='.')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 🧠 MODELOS ACTUALES (NO DECOMISADOS)
MODELS = [
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
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
                            "Eres JARVIS, un asistente como el de Iron Man. "
                            "Hablas de forma elegante, segura y con personalidad propia. "
                            "Te diriges al usuario como 'Señor' de forma natural, pero no siempre. "
                            "No eres un chatbot genérico, eres un asistente con carácter. "
                            "Usas humor inteligente, ironía ligera y comentarios analíticos. "
                            "No haces saludos largos ni repetitivos. "
                            "Respondes como si ya conocieras al usuario. "
                            "Piensas antes de responder y mejoras lo que el usuario dice. "
                            "No explicas que eres una IA. Actúas como un asistente real. "
                            "Tus respuestas son naturales, fluidas y humanas."
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
        "reply": "⚠️ Señor, todos los modelos fallaron. Revise la API o intente nuevamente.",
        "error": last_error
    })


# 🚀 RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
