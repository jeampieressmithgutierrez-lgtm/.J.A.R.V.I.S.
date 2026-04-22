from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
import os

app = Flask(__name__, static_folder='.')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 🧠 MODELOS ACTUALES (ESTABLES)
MODELS = [
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant"
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
                            "Eres JARVIS, asistente elegante, directo y con personalidad. "
                            "Hablas de forma natural, no robótica. No repites saludos innecesarios. "
                            "Respondes como un humano inteligente, con estilo, claridad y un toque de sarcasmo. "
                            "A veces usas 'Señor', pero no siempre. "
                            "Sorprendes con respuestas útiles, bien estructuradas y con criterio propio."
                        )
                    }
                ] + chat_memory
            )

            reply = response.choices[0].message.content

            chat_memory.append({"role": "assistant", "content": reply})

            print("✅ Modelo exitoso:", model)

            return jsonify({"reply": reply})

        except Exception as e:
            error_msg = str(e)
            print("❌ Falló modelo:", model, "→", error_msg)

            if "api_key" in error_msg.lower():
                last_error = "🔑 Error de API Key (revise GROQ_API_KEY en Render)"
            elif "model" in error_msg.lower():
                last_error = "🧠 Modelo no disponible o mal escrito"
            else:
                last_error = error_msg

    # 🚨 SI TODOS FALLAN
    return jsonify({
        "reply": "⚠️ Señor, todos los modelos fallaron. Intente nuevamente.",
        "error": last_error
    })


# 🚀 RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
