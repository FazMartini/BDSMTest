# Type python app.py

from flask import Flask, jsonify, request
import os
import json

app = Flask(__name__, static_folder='static')

# LOAD QUIZ DATA
with open("questions.json") as f:
    data = json.load(f)

traits = data["traits"]
questions = data["questions"]
matrix = data["trait_matrix"]

exclusivity = matrix["exclusivity"]
synergy = matrix["synergy"]

# Serve index.html at root
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/bdsm-personality-test')
def personality_test():
    return app.send_static_file('index.html')

# Endpoint to get the questions
@app.route('/questions', methods=['GET'])
def get_questions():
    try:
        with open("questions.json", "r") as f:
            dataset = json.load(f)
        # Send only the questions array
        return jsonify(dataset["questions"])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve the frontend HTML file when visiting the root URL
@app.route('/submit', methods=['POST'])
def submit_answers():
    try:
        # Load questions dataset
        with open("questions.json", "r") as f:
            dataset = json.load(f)

        questions = dataset["questions"]
        traits = dataset["traits"]
        matrix = dataset.get("trait_matrix", {})
        exclusivity = matrix.get("exclusivity", {})
        synergy = matrix.get("synergy", {})

        # Load user answers
        user_answers = {ans['id']: ans.get('answer', 0) for ans in request.json}

        # Initialize raw scores
        raw_trait_scores = {t: 0.0 for t in traits}
        trait_counts = {t: 0.0 for t in traits}

        for q in questions:
            qid = q['id']
            if qid not in user_answers:
                continue

            ans = float(user_answers[qid])

            # Reverse scoring (1-5 scale)
            if q.get("reverse", False):
                ans = 6 - ans

            primary_weight = float(q.get("primary_weight", 1.0))

            # Primary trait
            raw_trait_scores[q["primary_trait"]] += ans * primary_weight
            trait_counts[q["primary_trait"]] += primary_weight

            # Secondary traits
            for sec_trait, weight in q.get("secondary_traits", {}).items():
                weight = float(weight)
                if sec_trait in raw_trait_scores:
                    raw_trait_scores[sec_trait] += ans * weight
                    trait_counts[sec_trait] += abs(weight)

        # Apply exclusivity and synergy to raw scores
        adjusted_trait_scores = raw_trait_scores.copy()

        # Exclusivity: subtract conflicting trait influence using raw scores
        for trait, conflicts in exclusivity.items():
            if trait not in adjusted_trait_scores:
                continue
            for other_trait, penalty in conflicts.items():
                if other_trait in raw_trait_scores:
                    adjusted_trait_scores[trait] -= raw_trait_scores[other_trait] * float(penalty)

        # Synergy: add bonus based on overlap using raw scores
        for trait, partners in synergy.items():
            if trait not in adjusted_trait_scores:
                continue
            for other_trait, bonus in partners.items():
                if other_trait in raw_trait_scores:
                    boost = min(raw_trait_scores[trait], raw_trait_scores[other_trait]) * float(bonus)
                    adjusted_trait_scores[trait] += boost

        # Clamp negatives to zero
        for t in traits:
            adjusted_trait_scores[t] = max(0.0, adjusted_trait_scores[t])

        # Normalize to 0-100%
        trait_percentages = {}
        for t in traits:
            if trait_counts[t] > 0:
                pct = (adjusted_trait_scores[t] / (trait_counts[t] * 5)) * 100
                pct = max(0, min(100, pct))   # clamp to 0–100
                trait_percentages[t] = round(pct, 1)
            else:
                trait_percentages[t] = 0.0

        # Return result
        return jsonify({
            "trait_percentages": trait_percentages
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=5000, debug=True)
if __name__ == '__main__':
    app.run(debug=True)