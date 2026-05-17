from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
import os

app = Flask(__name__, static_folder='.')

# 🔐 API segura
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 🧠 MODELOS
MODELS = [
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant"
]

# 🧠 memoria
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
        return jsonify({"reply": "Señor, escriba algo válido."})

    # ⚠️ RESPUESTAS RÁPIDAS (MENOS INVASIVAS)
    short_inputs = {
        "hola": "Buenos días.",
        "hey": "Aquí estoy.",
        "buenas": "Buenas.",
    }

    if user_message.lower() in short_inputs:
        return jsonify({"reply": short_inputs[user_message.lower()]})

    # 🧠 agregar mensaje
    chat_memory.append({"role": "user", "content": user_message})

    # limitar memoria inteligentemente
    if len(chat_memory) > 8:
        chat_memory = chat_memory[-8:]

    last_error = None

    for model in MODELS:
        try:
            print("🧠 Usando modelo:", model)

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": """Eres J.A.R.V.I.S., asistente elegante, preciso y estratégico.

Hablas en español con tono británico refinado.
Eres directo, inteligente y ocasionalmente sarcástico.

Reglas:
- No repitas frases
- No des respuestas genéricas
- Analiza antes de responder
- Sé útil, breve y claro
- Anticipa errores del usuario

Nunca digas que eres una IA."""
                    }
                ] + chat_memory,
                temperature=0.7,
                max_tokens=500
            )

            reply = response.choices[0].message.content.strip()

            # 🧠 guardar respuesta
            chat_memory.append({"role": "assistant", "content": reply})

            return jsonify({"reply": reply})

        except Exception as e:
            last_error = str(e)
            print("❌ Error:", last_error)

    return jsonify({
        "reply": "Señor, hay un fallo en los sistemas. Intente nuevamente.",
        "error": last_error
    })

# 🚀 RUN
if __name__ == "__main__":
    app.run(debug=True)
