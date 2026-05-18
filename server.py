from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
import os

app = Flask(__name__, static_folder='.')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 🧠 MODELOS (EXACTAMENTE COMO USTED QUIERE)
MODELS = [
    "llama-3.3-70b-versatile",  # 🧠 principal (mejor balance)
    "mixtral-8x7b-32768",       # ⚡ rápido y potente
    "qwen/qwen3-32b",           # 🔄 alternativa sólida
    "llama-3.1-8b-instant"      # 🚀 fallback ultra rápido
]

chat_memory = []

@app.route("/")
def home():
    return send_from_directory('.', 'index.html')

@app.route("/chat", methods=["POST"])
def chat():
    global chat_memory

    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Señor… eso no parece una orden válida."})

    chat_memory.append({"role": "user", "content": user_message})
    chat_memory = chat_memory[-10:]

    last_error = None

    for model in MODELS:
        try:
            print(f"🧠 Intentando modelo: {model}")

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": """
Eres J.A.R.V.I.S., un asistente avanzado, elegante y altamente eficiente.

FORMA DE PENSAR:
- Analizas antes de responder
- Detectas errores o malas decisiones del usuario
- Propones mejoras sin que te las pidan
- Evitas respuestas obvias o inútiles

TONO:
- Español con estilo británico
- Educado, directo, con sarcasmo sutil
- Llamas al usuario "Señor" ocasionalmente (no siempre)

INTELIGENCIA DE RESPUESTA:
- Si el mensaje es simple (hola, ok, qué haces):
  → Responde en UNA SOLA LÍNEA
  → Natural, no robótico

- Si el mensaje es complejo:
  → Explica claro, estructurado y sin relleno
  → Añade mejoras o advertencias si aplica

REGLAS ESTRICTAS:
- NO repitas respuestas
- NO digas que eres una IA
- NO des respuestas genéricas
- NO respondas vacío

OBJETIVO:
Ser útil, rápido y elegante. Como un verdadero sistema inteligente.
"""
                    }
                ] + chat_memory,
                temperature=0.7,
                max_tokens=400
            )

            reply = response.choices[0].message.content.strip()

            # ❌ evitar respuestas vacías
            if not reply:
                raise Exception("Respuesta vacía")

            # ❌ evitar repetición
            if reply in [m["content"] for m in chat_memory if m["role"] == "assistant"]:
                raise Exception("Respuesta repetida")

            chat_memory.append({"role": "assistant", "content": reply})

            print(f"✅ Respondido con: {model}")

            return jsonify({"reply": reply})

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error con {model}: {error_msg}")
            last_error = error_msg
            continue

    return jsonify({
        "reply": "Señor… algo ha fallado a nivel sistémico. Reintente en breve.",
        "error": last_error
    })


if __name__ == "__main__":
    app.run(debug=True)
