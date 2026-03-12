from flask import Flask, render_template, request, jsonify
from model import LegalAssistantModel

app = Flask(__name__)

# Load model once on startup
model = LegalAssistantModel()
model.load_trained()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask_question():
    try:
        data = request.get_json()
        user_query = data.get("query", "").strip()

        if not user_query:
            return jsonify({"error": "Query cannot be empty."}), 400

        result = model.predict(user_query)

        return jsonify({
            "query": result["query"],
            "answer": result["best_answer"],
            "category": result["category"],
            "similarity": result["similarity"],
            "top_matches": result["top_matches"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health():
    return jsonify({"status": "ok", "message": "NyayaAI backend is running"})


if __name__ == "__main__":
    app.run(debug=True)