from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import requests
import os
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

DATA_DIR = "data/"
os.makedirs(DATA_DIR, exist_ok=True)

# **File Paths**
USER_PREFS_FILE = os.path.join(DATA_DIR, "user_preferences.json")
USER_KNOWLEDGE_FILE = os.path.join(DATA_DIR, "user_knowledge.json")
CONVERSATION_HISTORY_FILE = os.path.join(DATA_DIR, "conversation_history.json")

# **Load and Save Functions**
def load_json(file_path):
    """Loads a JSON file, returns empty dict if not found."""
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, ValueError):
        return {}

def save_json(file_path, data):
    """Saves a dictionary to a JSON file."""
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

#app = Flask(__name__)
#CORS(app)

# Define Default Preferences at the Top
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


# Load user preferences from a local JSON file
def get_user_preferences(user_id):
    """Retrieve user preferences, ensuring all default values exist."""
    user_data = load_json(USER_PREFS_FILE)
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
    existing_prefs = user_data.get(user_id, {})
    updated_prefs = {**DEFAULT_USER_PREFERENCES, **existing_prefs}
    return updated_prefs

def save_user_preferences(user_id, preferences):
    """Update and save user preferences."""
    user_data = load_json(USER_PREFS_FILE)
    user_data[user_id] = preferences
    save_json(USER_PREFS_FILE, user_data)

# **User Knowledge (Long-Term Memory)**
def get_user_knowledge(user_id):
    """Retrieve stored long-term knowledge of a user."""
    user_data = load_json(USER_KNOWLEDGE_FILE)
    return user_data.get(user_id, {"key_facts": []})

def save_user_knowledge(user_id, knowledge):
    """Save long-term knowledge about the user."""
    user_data = load_json(USER_KNOWLEDGE_FILE)
    user_data[user_id] = knowledge
    save_json(USER_KNOWLEDGE_FILE, user_data)

# **Conversation History (Session Memory)**
def get_conversation_history(user_id):
    """Retrieve past conversation history for a session."""
    history_data = load_json(CONVERSATION_HISTORY_FILE)
    return history_data.get(user_id, [])

def save_conversation_history(user_id, message):
    """Save chat history, keeping only the last 5 messages."""
    history_data = load_json(CONVERSATION_HISTORY_FILE)
    history_data.setdefault(user_id, []).append(message)
    history_data[user_id] = history_data[user_id][-5:]  # Keep only last 5 messages
    save_json(CONVERSATION_HISTORY_FILE, history_data)


def initial_user_assessment(user_id):
    """ Determines user preferences through a fun chat instead of MCQs. """

    print("🤖 Let's set up your AI Learning Assistant preferences! Answer these simple questions.")

    questions = {
        "learning_style": "How do you like to learn? (Visual, Step-by-Step, Storytelling, Interactive)",
        "personality_style": "How do you want responses? (Formal, Casual, Humorous, Inspirational)",
        "explanation_length": "Do you prefer short summaries, detailed explanations, or interactive learning?",
        "interaction_style": "Do you want direct answers, guided hints, or Socratic questioning?",
        "presentation_style": "Who is your ideal tutor? (Einstein, Curie, Feynman, Hawking, Shakespeare?)",
        "goal_orientation": "What motivates you more? (Mastery-Approach, Performance-Approach, Mastery-Avoidance, Performance-Avoidance)",
        "motivation_type": "Are you more driven by internal interest (Intrinsic) or external rewards (Extrinsic)?",
        "feedback_preference": "Do you prefer immediate feedback or delayed feedback?",
        "social_learning_preference": "Do you like learning alone (Individual) or with a group (Group)?"
    }

    user_prefs = {}

    for key, question in questions.items():
        print(f"🤖 AI: {question}")
        user_input = input("👤 User: ").strip().lower()  # Replace with frontend integration
        user_prefs[key] = user_input

    # Set up default preferences for missing fields
    user_preferences = {
        "learning_style": user_prefs.get("learning_style", "step_by_step"),
        "personality_style": user_prefs.get("personality_style", "casual"),
        "explanation_length": user_prefs.get("explanation_length", "detailed"),
        "interaction_style": user_prefs.get("interaction_style", "tutor"),
        "presentation_style": user_prefs.get("presentation_style", "einstein"),
        "goal_orientation": user_prefs.get("goal_orientation", "mastery-approach"),
        "motivation_type": user_prefs.get("motivation_type", "intrinsic"),
        "feedback_preference": user_prefs.get("feedback_preference", "immediate"),
        "social_learning_preference": user_prefs.get("social_learning_preference", "individual"),
        "preferred_subjects": ["physics", "math"],  # Default subjects
        "knowledge_level": "intermediate",  # Default level
        "problem_solving": "guided",
        "learning_speed": "medium",
        "role_model": "feynman",
        "struggled_with": [],
        "expectancy_value": {"expectancy": "high", "value": "high"},
        "personality_traits": ["openness", "conscientiousness"]
    }

    save_user_preferences(user_id, user_preferences)
    return "✅ User preferences saved!"


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
    """ Generate an AI response using user preferences, knowledge, and past conversations. """

    user_prefs = get_user_preferences(user_id)
    user_knowledge = get_user_knowledge(user_id)
    conversation_history = get_conversation_history(user_id)

    # Format past conversation history (keep last 5 messages)
    formatted_history = "\n".join(conversation_history)

    # **Generate AI prompt with full personalization**
    full_prompt = f"""
    Here is the past conversation with the user:
    {formatted_history}

    User's Learning Preferences:
    - Learning Style: {user_prefs['learning_style']}
    - Knowledge Level: {user_prefs['knowledge_level']}
    - Personality Style: {user_prefs['personality_style']}
    - Preferred Subjects: {", ".join(user_prefs['preferred_subjects'])}
    - Problem-Solving Approach: {user_prefs['problem_solving']}
    - Explanation Length: {user_prefs['explanation_length']}
    - Learning Speed: {user_prefs['learning_speed']}
    - Role Model: {user_prefs['role_model']}
    - Struggled Topics: {", ".join(user_prefs['struggled_with'])}
    - Goal Orientation: {user_prefs['goal_orientation']}
    - Self-Efficacy Level: {user_prefs['self_efficacy']}
    - Motivation Type: {user_prefs['motivation_type']}
    - Personality Traits: {", ".join(user_prefs['personality_traits'])}
    - Feedback Preference: {user_prefs['feedback_preference']}
    - Social Learning Preference: {user_prefs['social_learning_preference']}
    - Expectancy-Value Belief: Expectancy = {user_prefs['expectancy_value']['expectancy']}, Value = {user_prefs['expectancy_value']['value']}

    Long-Term Knowledge:
    - {", ".join(user_knowledge["key_facts"])}

    Now answer the latest question:
    {question}
    """

    print(f"🚀 AI Prompt Generated: {full_prompt}")  # Debugging log

    # **Detect if User Shares Important Information**
    if "I am working on" in question or "My project is about" in question:
        new_fact = question.replace("I am working on", "").replace("My project is about", "").strip()
        if new_fact not in user_knowledge["key_facts"]:
            user_knowledge["key_facts"].append(new_fact)
            save_user_knowledge(user_id, user_knowledge)  # **Update permanent knowledge**

    # **Send to AI Model**
    if AI_MODE == "local":
        try:
            result = subprocess.run(["ollama", "run", "llama2:13b", full_prompt], capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            return f"❌ Local AI Model Error: {str(e)}"

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
    """Handles AI question requests, remembers session context, and updates long-term knowledge."""

    data = request.json
    user_id = data.get("user_id", "default_user")
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"answer": "❌ Error: No question provided."}), 400

    # **Get AI response**
    response_text = get_ai_response(user_id, question)

    # **Save conversation history**
    save_conversation_history(user_id, f"User: {question}")
    save_conversation_history(user_id, f"AI: {response_text}")

    return jsonify({"answer": response_text})


@app.route("/update-preferences", methods=["POST"])
def update_preferences():
    """API Endpoint to update user preferences dynamically."""

    data = request.json
    user_id = data.get("user_id", "default_user")

    # Get current preferences and update only specified fields
    user_prefs = get_user_preferences(user_id)
    for key, value in data.items():
        if key in user_prefs:
            user_prefs[key] = value  # Update only valid fields

    save_user_preferences(user_id, user_prefs)

    return jsonify({"message": "✅ Preferences updated successfully!", "updated_preferences": user_prefs})


if __name__ == "__main__":
    app.run(debug=True)
