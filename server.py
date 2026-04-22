from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
import os

app = Flask(__name__, static_folder='.')

# 🔑 VALIDACIÓN DE API KEY
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("⚠️ Señor, falta configurar GROQ_API_KEY en Render.")

client = Groq(api_key=api_key)

# 🧠 MODELOS EN CASCADA (ACTUALIZADOS Y ESTABLES)
MODELS = [
    "llama-3.3-70b-versatile",   # 🔥 el mejor actual
    "llama-3.1-8b-instant"       # ⚡ rápido y estable
]

# 🧠 memoria simple
chat_memory = []

# 🖥️ FRONTEND
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

    if len(chat_memory) > 6:
        chat_memory = chat_memory[-6:]

    last_error = None

    # 🔁 INTENTO DE MODELOS
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
                ] + chat_memory,
                temperature=0.7,
                max_tokens=1024
            )

            reply = response.choices[0].message.content

            chat_memory.append({"role": "assistant", "content": reply})

            print("✅ Modelo exitoso:", model)

            return jsonify({"reply": reply})

        except Exception as e:
            print("❌ Falló modelo:", model, "→", str(e))
            last_error = str(e)

    # 🚨 SI TODO FALLA
    return jsonify({
        "reply": "⚠️ Señor, todos los modelos fallaron. Revise la API Key o el servicio.",
        "error": last_error
    })


# 🚀 RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
