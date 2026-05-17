from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
import os

app = Flask(__name__, static_folder='.')

# 🔐 API KEY
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    raise ValueError("⚠️ GROQ_API_KEY no configurada.")

client = Groq(api_key=api_key)

# ✅ MODELO ESTABLE (uno solo, sin conflictos)
MODEL = "llama3-70b-8192"

# 🧠 MEMORIA (limitada y eficiente)
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
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "Señor, necesito una instrucción válida."})

        # 🧠 PERSONALIDAD JARVIS (simple pero efectiva)
        system_prompt = """
Eres J.A.R.V.I.S., asistente personal de alta precisión.

Hablas en español con tono británico elegante, directo y educado.
Te diriges al usuario como "Señor".

Reglas:
- Sé breve pero inteligente
- Responde con claridad absoluta
- Puedes usar sarcasmo ligero si es apropiado
- Anticipa errores o mejora las ideas del usuario
- No repitas frases
- No suenes como IA
"""

        # 🧠 guardar usuario
        chat_memory.append({"role": "user", "content": user_message})

        # 🔒 limitar memoria
        if len(chat_memory) > 6:
            chat_memory = chat_memory[-6:]

        print("🧠 Procesando:", user_message)

        # 🚀 LLAMADA A GROQ
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": system_prompt}] + chat_memory,
            temperature=0.6,
            max_tokens=300
        )

        reply = response.choices[0].message.content.strip()

        # 🧠 guardar respuesta
        chat_memory.append({"role": "assistant", "content": reply})

        print("✅ Respuesta:", reply)

        return jsonify({"reply": reply})

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({
            "reply": "Señor, hay una interrupción en el sistema. Intente nuevamente.",
            "error": str(e)
        })


# 🚀 RUN
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
