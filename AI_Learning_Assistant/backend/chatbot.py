from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import requests
import os
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
#app = Flask(__name__)
#CORS(app)

# Load user preferences from a local JSON file
USER_PREFS_FILE = "user_preferences.json"
# Default parameters for personalization
DEFAULT_USER_PREFERENCES = {
    "learning_style": "step_by_step",
    "presentation_style": "einstein",
    "knowledge_level": "intermediate",
    "interaction_style": "tutor",
    "problem_solving": "guided",
    "personality_style": "casual",
    "preferred_subjects": ["physics", "math"],
    "explanation_length": "detailed",
    "learning_speed": "medium",
    "role_model": "feynman",
    "struggled_with": [],
    "goal_orientation": "mastery-approach",
    "self_efficacy": "medium",
    "motivation_type": "intrinsic",
    "personality_traits": ["openness", "conscientiousness"],
    "feedback_preference": "immediate",
    "social_learning_preference": "individual",
    "expectancy_value": {"expectancy": "high", "value": "high"}
}

def initial_user_assessment(user_id):
    """ Determines user preferences through a fun chat instead of MCQs. """

    questions = [
        "How do you like to learn? (Visual, Step-by-Step, Storytelling, Interactive)",
        "Do you like explanations to be formal, casual, humorous, or inspirational?",
        "Do you prefer short answers, detailed breakdowns, or interactive learning?",
        "Would you rather have direct answers, guided hints, or deep Socratic questioning?",
        "Who is your ideal tutor? (Einstein, Curie, Feynman, Hawking, Shakespeare?)"
    ]

    user_prefs = {}

    for q in questions:
        print(f"🤖 AI: {q}")
        user_input = input("👤 User: ")  # Replace with frontend integration
        user_prefs[q] = user_input

    # Convert responses into structured preferences
    user_preferences = {
        "learning_style": user_prefs[questions[0]].lower(),
        "personality_style": user_prefs[questions[1]].lower(),
        "explanation_length": user_prefs[questions[2]].lower(),
        "interaction_style": user_prefs[questions[3]].lower(),
        "presentation_style": user_prefs[questions[4]].lower(),
    }

    save_user_preferences(user_id, user_preferences)
    return "User preferences saved!"


# Function to load user data
def load_user_preferences():
    if not os.path.exists(USER_PREFS_FILE):
        return {}
    try:
        with open(USER_PREFS_FILE, "r") as file:
            data = json.load(file)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, ValueError):
        return {}

# Function to save user data
# Save user preferences
def save_user_preferences(user_id, preferences):
    user_data = load_user_preferences()
    user_data[user_id] = preferences
    with open(USER_PREFS_FILE, "w") as file:
        json.dump(user_data, file, indent=4)

# Get user preferences (loads defaults if missing)
def get_user_preferences(user_id):
    """ Retrieve user preferences, ensuring all default values exist """

    user_data = load_user_preferences()

    # Get existing preferences or create new ones
    existing_prefs = user_data.get(user_id, {})

    # Merge with defaults to ensure no missing fields
    updated_prefs = {**DEFAULT_USER_PREFERENCES, **existing_prefs}

    return updated_prefs


# Function to update user preference
def update_user_preference(user_id, updates):
    """ Update specific fields in user preferences without overwriting everything """

    # Load current user preferences
    user_prefs = get_user_preferences(user_id)

    # Merge updates into existing preferences
    for key, value in updates.items():
        if key in user_prefs:  # Only update valid keys
            user_prefs[key] = value

    # Save the updated preferences
    save_user_preferences(user_id, user_prefs)

    return user_prefs  # Return updated preferences for verification


# AI Mode: Local (Llama 2) or API (Gemini)
AI_MODE = os.getenv("AI_MODE", "api")

# Google Gemini API Config
GEMINI_API_KEY = "AIzaSyChup4-1Oy98eweQ_V1tKj2daB8YxeCFzE"
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

# Function to get AI response
def get_ai_response(user_id, question):
    """ Generate an AI response based on user preferences, supporting both Local LLM and Gemini API. """

    user_prefs = get_user_preferences(user_id)

    # Construct a personalized prompt based on user preferences
    full_prompt = f"""
    You are {user_prefs['presentation_style']}, a famous thinker.
    Your role model is {user_prefs['role_model']}.
    Your teaching style is {user_prefs['interaction_style']}.

    - Learning Style: {user_prefs['learning_style']}
    - Knowledge Level: {user_prefs['knowledge_level']}
    - Personality: {user_prefs['personality_style']}
    - Subject Interests: {", ".join(user_prefs['preferred_subjects'])}
    - Past Struggles: {", ".join(user_prefs['struggled_with'])}
    - Problem-Solving Approach: {user_prefs['problem_solving']}
    - Goal Orientation: {user_prefs['goal_orientation']}
    - Self-Efficacy Level: {user_prefs['self_efficacy']}
    - Motivation Type: {user_prefs['motivation_type']}
    - Personality Traits: {", ".join(user_prefs['personality_traits'])}
    - Feedback Preference: {user_prefs['feedback_preference']}
    - Social Learning Preference: {user_prefs['social_learning_preference']}
    - Expectancy: {user_prefs['expectancy_value']['expectancy']}
    - Value: {user_prefs['expectancy_value']['value']}

    Adjust your explanation accordingly.

    Question: {question}
    """

    print(f"🚀 Sending prompt to AI: {full_prompt}")  # Debugging Log

    # **Local LLM (Ollama) Option**
    if AI_MODE == "local":
        try:
            result = subprocess.run(["ollama", "run", "llama2:13b", full_prompt], capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            return f"❌ Local AI Model Error: {str(e)}"

    # **Google Gemini API Option**
    elif AI_MODE == "api":
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": full_prompt}]}]}

        try:
            response = requests.post(GEMINI_URL, headers=headers, json=data)
            if response.status_code != 200:
                return f"❌ Error: {response.status_code} - {response.text}"
            json_response = response.json()
            return json_response["candidates"][0]["content"]["parts"][0]["text"]
        except requests.exceptions.RequestException as e:
            return f"❌ API request failed: {str(e)}"

    return "❌ Error: Invalid AI mode selected."


@app.route("/ask", methods=["POST"])
def ask():
    """Handles AI question requests and generates personalized responses."""

    data = request.json
    user_id = data.get("user_id", "default_user")
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"answer": "❌ Error: No question provided."}), 400

    # Retrieve user preferences
    user_prefs = get_user_preferences(user_id)

    # Generate AI response using the get_ai_response() function
    response_text = get_ai_response(user_id, question)

    return jsonify({"answer": response_text})


@app.route("/update-preferences", methods=["POST"])
def update_preferences():
    """ API Endpoint to update user preferences dynamically """

    data = request.json
    user_id = data.get("user_id", "default_user")  # Default user if not provided

    # Update preferences based on user input
    updated_prefs = update_user_preference(user_id, data)

    return jsonify({"message": "User preferences updated successfully!", "updated_preferences": updated_prefs})



if __name__ == "__main__":
    app.run(debug=True)
