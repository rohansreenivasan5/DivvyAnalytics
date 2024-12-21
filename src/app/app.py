import os
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai

app = Flask(__name__)

# Load query template from a file
QUERY_TEMPLATE_FILE = "query.txt"


def load_query_template():
    with open(QUERY_TEMPLATE_FILE, "r") as file:
        return file.read()


# Generate final query with user's input
def generate_query(user_query):
    query_template = load_query_template()
    final_query = f"{query_template}\n\nUser Query: {user_query}"
    return final_query


# Call Gemini API
def get_gemini_response(query):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content([{"parts": [{"text": query}]}])
    return response.text.strip()


# Flask routes
@app.route("/")
def index():
    return render_template("index.html")  # Serve the front-end HTML


@app.route("/query", methods=["POST"])
def query():
    user_query = request.json.get("user_query", "")
    if not user_query:
        return jsonify({"error": "User query is required"}), 400

    # Generate query and get response
    final_query = generate_query(user_query)
    try:
        gemini_response = get_gemini_response(final_query)
        return jsonify({"response": gemini_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
