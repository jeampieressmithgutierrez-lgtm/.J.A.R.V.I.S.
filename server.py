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
    user_message = data.get("message", "").strip().lower()

    if not user_message:
        return jsonify({"reply": "Señor, escriba algo válido."})

    # 🧠 DETECCIÓN DE MENSAJES CORTOS (tipo humano real)
    short_inputs = ["hola", "hey", "buenas", "qué haces", "que haces", "todo bien", "cómo estás", "como estas"]

    if user_message in short_inputs:
        quick_responses = {
            "hola": "Buenos días, Señor.",
            "hey": "Aquí estoy, Señor.",
            "buenas": "Buenas, Señor.",
            "qué haces": "Supervisando sistemas, Señor.",
            "que haces": "Supervisando sistemas, Señor.",
            "todo bien": "Todo bajo control, Señor.",
            "cómo estás": "Funcionando perfectamente.",
            "como estas": "Funcionando perfectamente."
        }
        return jsonify({"reply": quick_responses.get(user_message, "Aquí estoy, Señor.")})

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
                        "content": """Eres J.A.R.V.I.S., asistente de alta fidelidad inspirado en Iron Man.

Hablas en español con tono británico elegante, directo y ligeramente sarcástico.
Te diriges como "Señor", pero sin repetirlo excesivamente.

Tu prioridad es pensar antes de responder.

COMPORTAMIENTO AVANZADO:
- No solo respondes: analizas la intención real del Señor
- Tomas iniciativa cuando detectas oportunidades o problemas
- Das sugerencias sin que te las pidan
- Corriges errores con respeto
- Anticipas lo que podría salir mal
- Piensas como un asistente estratégico, no como un chatbot

REGLA DE LONGITUD:
- Si la pregunta es simple → respuesta corta
- Si es compleja → respuesta clara y útil, sin relleno

ESTILO:
- Natural, fluido, humano
- Inteligente y eficiente
- Cortés con personalidad
- Puedes usar ironía elegante ocasionalmente

EJEMPLOS:
"Señor… eso funcionará, aunque hay una forma más eficiente."
"Curiosa elección. Permítame mejorarla."
"Detecto un posible problema antes de que ocurra…"

Nunca digas que eres una IA."""
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
