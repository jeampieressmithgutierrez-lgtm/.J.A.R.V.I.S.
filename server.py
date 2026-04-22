from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# memoria simple (últimos mensajes)
chat_memory = []

@app.route("/")
def home():
    return "Servidor activo, señor."

@app.route("/chat", methods=["POST"])
def chat():
    global chat_memory

    user_message = request.json.get("message")

    chat_memory.append({"role": "user", "content": user_message})

    # limitar memoria
    if len(chat_memory) > 6:
        chat_memory = chat_memory[-6:]

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-70b-versatile",
                "messages": [
                    {
                        "role": "system",
                        "content": "Eres JARVIS: elegante, claro, con emojis, respuestas estructuradas con títulos."
                    }
                ] + chat_memory
            }
        )

        data = response.json()

        reply = data["choices"][0]["message"]["content"]

        chat_memory.append({"role": "assistant", "content": reply})

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"Error en IA: {str(e)}"})
