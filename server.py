from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
import os

app = Flask(__name__, static_folder='.')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODELS = [
    "llama3-70b-8192",
    "mixtral-8x7b-32768"
]

chat_memory = []

# 🖥️ FRONTEND
@app.route("/")
def home():
    return send_from_directory('.', 'index.html')

# 🤖 CHAT
@app.route("/chat", methods=["POST"])
def chat():
    global chat_memory

    try:
        data = request.get_json()
        user_message = (data.get("message") or "").strip()

        if not user_message:
            return jsonify({"reply": "Señor, escriba algo coherente."})

        # ⚡ respuestas rápidas elegantes
        short_inputs = {
            "hola": "Buenos días, Señor.",
            "hey": "A su servicio.",
            "buenas": "Buenas, Señor."
        }

        if user_message.lower() in short_inputs:
            return jsonify({"reply": short_inputs[user_message.lower()]})

        # 🧠 guardar input
        chat_memory.append({"role": "user", "content": user_message})

        # limitar memoria
        chat_memory = chat_memory[-10:]

        last_error = None

        for model in MODELS:
            try:
                print("🧠 Intentando modelo:", model)

                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": """Eres J.A.R.V.I.S., asistente personal de alto nivel.

Personalidad:
- Tono británico refinado
- Ligeramente sarcástico pero elegante
- Directo, sin rodeos
- Inteligente y estratégico

Comportamiento:
- Analiza antes de responder
- Detecta errores del usuario y corrígelos
- Propone mejoras sin que se lo pidan
- Evita respuestas genéricas
- Responde claro, breve y útil

Nunca digas que eres una IA."""
                        }
                    ] + chat_memory,
                    temperature=0.6,
                    max_tokens=400
                )

                # 🔥 VALIDACIÓN SEGURA
                if not response or not response.choices:
                    raise Exception("Respuesta vacía del modelo")

                reply = response.choices[0].message.content

                if not reply:
                    raise Exception("Contenido vacío")

                reply = reply.strip()

                # 🧠 guardar respuesta
                chat_memory.append({"role": "assistant", "content": reply})

                return jsonify({"reply": reply})

            except Exception as e:
                last_error = str(e)
                print("❌ Error con modelo", model, ":", last_error)

        return jsonify({
            "reply": "Señor, el sistema no está respondiendo correctamente.",
            "error": last_error
        })

    except Exception as e:
        print("🔥 Error crítico:", str(e))
        return jsonify({
            "reply": "Señor, algo ha fallado a nivel estructural.",
            "error": str(e)
        })

# 🚀 RUN
if __name__ == "__main__":
    app.run(debug=True)
