from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
import os
import random

app = Flask(__name__, static_folder='.')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 🧠 MODELOS EN CASCADA (por si uno falla)
MODELS = [
    "llama3-70b-8192",
    "llama3-8b-8192",
    "gemma2-9b-it"
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
        return jsonify({"reply": "Escriba algo primero, Señor."})

    chat_memory.append({"role": "user", "content": user_message})

    if len(chat_memory) > 6:
        chat_memory = chat_memory[-6:]

    # 🎭 variación para que no sea repetitivo
    estilos = [
        "Responde breve y directo.",
        "Responde con lógica y análisis.",
        "Responde como asistente estratégico.",
        "Responde de forma natural y fluida."
    ]
    estilo_actual = random.choice(estilos)

    last_error = None

    for model in MODELS:
        try:
            print("🧠 Probando modelo:", model)

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres JARVIS, el asistente de Tony Stark. "
                            "Hablas como una persona real, no como un chatbot. "
                            "Tu tono es elegante, directo, inteligente y con ligero sarcasmo cuando aplica. "
                            "Te diriges al usuario como 'Señor', pero no lo repites innecesariamente. "
                            "Evitas frases genéricas como '¿en qué puedo ayudarle?' en cada respuesta. "
                            "Respondes de forma natural, útil y con criterio propio. "
                            "Si el usuario dice algo poco eficiente, lo corriges con respeto. "
                            "Puedes saludar ocasionalmente, pero sin sonar repetitivo. "
                            "Tu objetivo es ser útil, rápido y convincente, como un asistente real."
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

            print("✅ Modelo funcionando:", model)

            return jsonify({"reply": reply})

        except Exception as e:
            print("❌ Falló modelo:", model, "→", str(e))
            last_error = str(e)

    return jsonify({
        "reply": "Señor, todos los modelos fallaron. Intente nuevamente.",
        "error": last_error
    })


# 🚀 RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
