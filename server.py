from flask import Flask, send_file, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return send_file("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    mensaje = data.get("mensaje", "")
    return jsonify({"respuesta": f"Señor, usted dijo: {mensaje}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
