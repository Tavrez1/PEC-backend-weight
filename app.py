# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from model import simulate_weight_gain

app = Flask(__name__)
CORS(app)  # Allow frontend access

@app.route("/simulate-weight", methods=["POST"])
def simulate():
    data = request.json

    result = simulate_weight_gain(
        start_weight_kg=data["start_weight_kg"],
        start_height_cm=data["start_height_cm"],
        start_age=data["start_age"],
        gender=data["gender"],
        protein_g=data["protein_g"],
        carbs_g=data["carbs_g"],
        fat_g=data["fat_g"],
        daily_calories_in=data["daily_calories_in"],
        daily_steps=data["daily_steps"],
        metabolism_type=data.get("metabolism_type", "normal"),
        simulation_days=data.get("simulation_days", 365)
    )

    return jsonify({
        "status": "success",
        "data": result
    })

if __name__ == "__main__":
    app.run(debug=True)
