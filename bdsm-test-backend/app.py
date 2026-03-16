# Type python app.py

from flask import Flask, jsonify, request, send_from_directory
import os
import json

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Serve the frontend HTML file when visiting the root URL
@app.route('/')
def index():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'index.html')

@app.route('/bdsm-personality-test')
def personality_test():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'index.html')

# Serve static files (CSS, JS, etc.)
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)

# Endpoint to get the questions
@app.route('/questions', methods=['GET'])
def get_questions():
    try:
        with open("questions.json", "r") as f:
            questions = json.load(f)
        return jsonify(questions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to get the traits for a specific question
@app.route('/traits/<question_id>', methods=['GET'])
def get_traits(question_id):
        with open("questions.json", "r") as f:
            questions = json.load(f)
        question = next((q for q in questions if q['id'] == question_id), None)
        if question:
            return jsonify(question['traits'])
        else:
            return jsonify({'error': 'Question not found'}), 404

# Endpoint to get the traits for all questions
@app.route('/all_traits', methods=['GET'])
def get_all_traits():
        with open("questions.json", "r") as f:
            questions = json.load(f)
        traits = set()
        for question in questions:
            traits.update(question['traits'].keys())
        return jsonify(list(traits))

# Endpoint to submit the answers and calculate the results
@app.route('/submit', methods=['POST'])
def submit_answers():
    try:
        with open("questions.json", "r") as f:
            questions = json.load(f)

        answers = request.json
        trait_scores = {trait: 0.0 for question in questions for trait in question['traits']}
        
        for answer in answers:
            question = next((q for q in questions if q['id'] == answer['id']), None)
            if not question:
                return jsonify({'error': f"Question {answer['id']} not found"}), 404
            # Update trait scores based on the answer (ensure numeric)
            val = float(answer.get('answer', 0))
            for trait, score in question['traits'].items():
                trait_scores[trait] += score * val
        
        # Return traits sorted largest to smallest (preserves order in Python 3.7+)
        sorted_traits = dict(sorted(trait_scores.items(), key=lambda kv: kv[1], reverse=True))
        return jsonify(sorted_traits)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
