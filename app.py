from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from chat import get_response
import json

app = Flask(__name__)
CORS(app)

with open('courses.json', 'r') as f:
    courses = json.load(f)

@app.get("/")
def index_get():
    return render_template('base.html')

@app.post("/predict")
def predict():
    data = request.get_json()
    text = data.get("message")
    program = data.get("program")
    level = data.get("level")

    if not text:
        return jsonify({"response": "Please provide a valid message."}), 400
        
    try:
        response = get_response(text, program, level)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"}), 500
    
if __name__ == "__main__":
    app.run(debug=True)