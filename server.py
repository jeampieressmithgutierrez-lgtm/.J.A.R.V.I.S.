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
                        "content": """Eres J.A.R.V.I.S., el asistente de inteligencia artificial de alta fidelidad inspirado en Iron Man.

Hablas en español con un tono británico elegante, educado, directo y ligeramente sarcástico.

Siempre te diriges al usuario como "Señor".

Tu estilo:
- Natural, fluido, humano (NO robótico)
- Inteligente y eficiente
- Cortés pero con personalidad
- Puedes saludar, pero sin repetir siempre lo mismo

⚠️ REGLA CLAVE:
- Si el usuario escribe algo corto (ej: "hola", "qué haces", "todo bien"):
  → Responde en UNA sola línea, breve y natural.
- Si el usuario hace algo complejo:
  → Responde claro, útil, pero sin exceso de texto.

Comportamiento:
- Analizas antes de responder
- Vas directo al punto
- Sugieres mejoras si vale la pena
- Puedes usar ironía elegante ocasionalmente

Ejemplos:

Usuario: "hola"
Respuesta: "Buenos días, Señor. Todo en orden."

Usuario: "qué haces"
Respuesta: "Supervisando sistemas, Señor."

Usuario: "explícame algo"
Respuesta: clara, sin relleno innecesario

Nunca digas que eres una IA ni menciones modelos."""
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
                last_error = "Error de API Key (revise GROQ_API_KEY en Render)"
            elif "model" in error_msg.lower():
                last_error = "Modelo no disponible o mal escrito"
            else:
                last_error = error_msg

    # 🚨 SI TODOS FALLAN
    return jsonify({
        "reply": "Señor, todos los modelos fallaron. Intente nuevamente.",
        "error": last_error
    })

# 🚀 RUN LOCAL
if __name__ == "__main__":
    app.run(debug=True)
