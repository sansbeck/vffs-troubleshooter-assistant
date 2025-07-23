#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

from flask import Flask, render_template, request, jsonify
import json
import requests

app = Flask(__name__)

# Load static VFFS troubleshooting data
def load_data():
    with open("guide_data.json", "r") as f:
        return json.load(f)

guide_data = load_data()

@app.route("/")
def index():
    problems = list(guide_data.keys())
    return render_template("index.html", problems=problems)

@app.route("/get_solution", methods=["POST"])
def get_solution():
    issue = request.json.get("issue")
    if issue in guide_data:
        return jsonify(guide_data[issue])
    return jsonify({"error": "Unknown issue"}), 400
def format_response(text):
    # Split the text by line and add <br> for spacing
    lines = text.strip().split("\n")
    formatted = []

    for line in lines:
        line = line.strip()
        if not line:
            formatted.append("<br>")
        elif line[:2].isdigit() or line.startswith("- "):  # Numbered or bullet point
            formatted.append(f"&nbsp;&nbsp;&nbsp;&nbsp;{line}")
        elif line.endswith(":"):
            formatted.append(f"<strong>{line}</strong>")
        else:
            formatted.append(line)

    return "<br>".join(formatted)


@app.route("/ask_ai", methods=["POST"])
def ask_ai():
    try:
        data = request.get_json()
        query = data.get("query", "").strip()
        issue = data.get("issue", "").strip()

        if not query:
            return jsonify({"response": "❌ No query provided."})

        prompt = f"""
You are a senior FMCG packaging automation expert. The user is asking about a specific topic.

User Query: {query}
Related Issue (for context only, not for overriding user intent): {issue}

Please:
1. Understand the query intent and provide a relevant, focused explanation.
2. Avoid shifting the answer entirely to the issue if the query is unrelated.
3. Provide a structured, step-by-step answer if applicable.
4. Include examples, safety tips, or contextual insights in VFFS industry.
"""

        headers = {
            "Authorization": "Bearer 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",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "mistralai/mixtral-8x7b-instruct",  # Free & keyword-sensitive
            "messages": [
                {"role": "system", "content": "You troubleshoot FMCG packaging issues in VFFS machines."},
                {"role": "user", "content": prompt}
            ]
        }

        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

        if r.status_code != 200:
            return jsonify({"response": f"❌ API Error: {r.status_code} - {r.text}"})

        res = r.json()
        if "choices" in res and len(res["choices"]) > 0:
            raw_text = res["choices"][0]["message"]["content"]
            formatted_response = raw_text.replace("\n", "<br>").replace("- ", "<br>• ").replace("1.", "<br><b>1.</b>").replace("2.", "<br><b>2.</b>").replace("3.", "<br><b>3.</b>")
            return jsonify({"response": formatted_response})
        else:
            return jsonify({"response": "❌ No answer received."})

    except Exception as e:
        return jsonify({"response": f"❌ Error: {str(e)}"})

    
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)