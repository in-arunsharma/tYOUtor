from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import requests
import os
import json

app = Flask(__name__)
CORS(app)

# Load user preferences from a local JSON file
USER_PREFS_FILE = "user_preferences.json"

# Function to load user data
def load_user_preferences():
    if not os.path.exists(USER_PREFS_FILE):
        return {}  # Return empty dictionary if file doesn't exist
    with open(USER_PREFS_FILE, "r") as file:
        return json.load(file)

# Function to save user data
def save_user_preferences(user_id, learning_style):
    try:
        # Load existing data
        with open(USER_PREFS_FILE, "r") as file:
            user_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        user_data = {}  # If file doesn't exist or is empty, initialize it

    # Update the user data
    user_data[user_id] = {
        "learning_style": learning_style,
        "last_used": "2025-03-13T02:00:00Z"
    }

    # Write updated data to file
    with open(USER_PREFS_FILE, "w") as file:
        json.dump(user_data, file, indent=4)

# Function to get the user's preferred learning style
def get_user_preference(user_id):
    user_data = load_user_preferences()
    return user_data.get(user_id, {}).get("learning_style", "default")

# Function to update user preference
def update_user_preference(user_id, learning_style):
    user_data = load_user_preferences()
    user_data[user_id] = {"learning_style": learning_style}
    save_user_preferences(user_data)

# AI Mode: Local (Llama 2) or API (Gemini)
AI_MODE = os.getenv("AI_MODE", "api")

# Google Gemini API Config
GEMINI_API_KEY = "AIzaSyChup4-1Oy98eweQ_V1tKj2daB8YxeCFzE"
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

# Function to get AI response
def get_ai_response(user_id, prompt):
    learning_style = get_user_preference(user_id)

    if AI_MODE == "local":
        formatted_prompt = f"You are a tutor adapting to the user’s learning style: {learning_style}. Explain:\n{prompt}"
        result = subprocess.run(["ollama", "run", "llama2:13b", formatted_prompt], capture_output=True, text=True)
        return result.stdout.strip()

    elif AI_MODE == "api":
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": f"You are an AI tutor adapting to {learning_style} learning style. Explain:\n{prompt}"}]}]
        }
        response = requests.post(GEMINI_URL, headers=headers, json=data)

        if response.status_code != 200:
            return f"Error: {response.status_code} - {response.text}"

        json_response = response.json()
        return json_response["candidates"][0]["content"]["parts"][0]["text"]

    return "Invalid AI mode selected."

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_id = data.get("user_id", "default_user")  # Ensure user_id is received
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"answer": "Please ask a valid question."})

    # Retrieve the user's learning style or set default
    learning_style = get_user_preference(user_id)

    # Generate AI response
    response_text = get_ai_response(user_id, question)

    # Update user preferences and save them
    save_user_preferences(user_id, learning_style)

    return jsonify({"answer": response_text})


if __name__ == "__main__":
    app.run(debug=True)
