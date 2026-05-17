from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
import os

app = Flask(__name__, static_folder='.')

# 🔐 API KEY (asegúrese de configurarla en Render o local)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 🧠 MODELOS (ORDEN INTELIGENTE)
MODELS = [
    "openai/gpt-oss-120b",      # 🧠 principal
    "llama-3.3-70b-versatile",  # ⚖️ equilibrio
    "qwen/qwen3-32b",           # 🔄 alternativa
    "llama-3.1-8b-instant"      # ⚡ fallback rápido
]

# 🧠 memoria conversacional
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

    # 🧠 guardar mensaje
    chat_memory.append({"role": "user", "content": user_message})

    # 🔁 limitar memoria (últimos 10 mensajes)
    if len(chat_memory) > 10:
        chat_memory = chat_memory[-10:]

    last_error = None

    # 🔁 intentar múltiples modelos automáticamente
    for model in MODELS:
        try:
            print(f"🧠 Intentando modelo: {model}")

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": """Eres J.A.R.V.I.S., un asistente de inteligencia avanzada inspirado en Iron Man.

Hablas en español con tono británico elegante, directo y ligeramente sarcástico.

Te diriges al usuario como "Señor", pero sin repetirlo excesivamente.

COMPORTAMIENTO:
- Piensas antes de responder
- No repites respuestas
- Generas respuestas naturales y humanas
- Tomas iniciativa cuando detectas mejoras o errores
- Anticipas problemas antes de que ocurran

REGLA DE RESPUESTA:
- Si el mensaje es simple (ej: "hola", "qué haces"):
  → Responde en una sola línea
  → Cada respuesta debe ser distinta (NO repetitiva)

- Si es complejo:
  → Responde claro, útil y sin relleno

ESTILO:
- Inteligente y eficiente
- Natural (NO robótico)
- Con personalidad elegante

Ejemplos:
"Buenos días… parece que llega en el momento justo."
"Supervisando todo. Nada fuera de lo normal… todavía."
"Curiosa decisión. Permítame mejorarla."

Nunca digas que eres una IA."""
                    }
                ] + chat_memory,
                temperature=0.8,
                max_tokens=500
            )

            reply = response.choices[0].message.content.strip()

            # 🧠 guardar respuesta
            chat_memory.append({"role": "assistant", "content": reply})

            print(f"✅ Respondido con: {model}")

            return jsonify({"reply": reply})

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error con {model}: {error_msg}")
            last_error = error_msg
            continue

    # 🚨 fallback total
    return jsonify({
        "reply": "Señor… los sistemas están inestables. Intente nuevamente en un momento.",
        "error": last_error
    })

# 🚀 RUN LOCAL
if __name__ == "__main__":
    app.run(debug=True)
