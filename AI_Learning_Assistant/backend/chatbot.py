from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import requests
import os
import json
import pandas as pd
import random

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

DATA_DIR = "../data/"


# **File Paths**
COURSE_CSV_FILE = os.path.join(DATA_DIR, "course_database.csv")
USER_PREFS_FILE = os.path.join(DATA_DIR, "user_preferences.json")
USER_KNOWLEDGE_FILE = os.path.join(DATA_DIR, "user_knowledge.json")
CONVERSATION_HISTORY_FILE = os.path.join(DATA_DIR, "conversation_history.json")


os.makedirs(DATA_DIR, exist_ok=True)

# **Load and Save Functions**
def load_json(file_path):
    """Load JSON data from a file."""
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {}

def save_json(file_path, data):
    """Save JSON data to a file."""
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
        "explanation_length": "balanced",
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
    return user_data.get(user_id, {"key_facts": [], "learned_topics": []}) 

def save_user_knowledge(user_id, knowledge):
    """Save long-term knowledge about the user."""
    user_data = load_json(USER_KNOWLEDGE_FILE)
    user_data[user_id] = knowledge
    save_json(USER_KNOWLEDGE_FILE, user_data)

# **🔹 Conversation History (Short-Term Session Memory)**
def get_conversation_history(user_id, full_history=False):
    """Retrieve chat history for a specific user. Optionally return full history."""
    history_data = load_json(CONVERSATION_HISTORY_FILE)
    user_history = history_data.get(user_id, [])

    if full_history:
        return user_history  # Return the entire conversation

    return user_history[-10:]  # Keep only the last 10 messages

def save_conversation_history(user_id, message):
    """Save chat history, keeping only recent messages per user."""
    history_data = load_json(CONVERSATION_HISTORY_FILE)
    history_data.setdefault(user_id, []).append(message)
    history_data[user_id] = history_data[user_id][-10:]  # Keep last 10 messages
    save_json(CONVERSATION_HISTORY_FILE, history_data)

# **Find Relevant Courses from CSV**

def find_relevant_courses_csv(query, num_results=3):
    """ Search for relevant courses directly from the CSV file using TF-IDF similarity. """
    try:
        df = pd.read_csv(COURSE_CSV_FILE)

        # **Ensure Required Columns Exist**
        required_columns = {"title", "description", "url", "search_text"}
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            print(f"❌ Error: CSV file is missing columns: {missing_columns}")
            return []

        # **Use TF-IDF to Find Relevant Courses**
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        tfidf = TfidfVectorizer(stop_words="english")
        tfidf_matrix = tfidf.fit_transform(df["search_text"].astype(str))

        query_vec = tfidf.transform([query])
        similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()

        sorted_indices = similarities.argsort()[::-1]
        relevant_courses = df.iloc[sorted_indices[:num_results]]

        return relevant_courses.to_dict(orient="records")

    except Exception as e:
        print(f"❌ Error searching courses: {str(e)}")
        return []
    


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

def extract_user_knowledge(user_id, user_input):
    """Extract useful details from user responses and store them in long-term memory."""
    key_topics = ["physics", "math", "biology", "chemistry", "coding", "history", "philosophy", "languages"]

    extracted_facts = []
    learned_topics = []

    for topic in key_topics:
        if topic in user_input.lower():
            extracted_facts.append(f"User is interested in {topic}.")
            learned_topics.append(topic)

    if extracted_facts:
        user_knowledge = get_user_knowledge(user_id)
        user_knowledge["key_facts"].extend(extracted_facts)
        user_knowledge["key_facts"] = list(set(user_knowledge["key_facts"]))  # Remove duplicates
        user_knowledge["learned_topics"].extend(learned_topics)  # NEW: Track topics they learned
        user_knowledge["learned_topics"] = list(set(user_knowledge["learned_topics"]))  # Remove duplicates
        save_user_knowledge(user_id, user_knowledge)


def clear_conversation_history():
    """Clear conversation history after each session."""
    save_json(CONVERSATION_HISTORY_FILE, {})  # Reset the file


# AI Mode: Local (Llama 2) or API (Gemini)
AI_MODE = os.getenv("AI_MODE", "api")

# Google Gemini API Config
GEMINI_API_KEY = "AIzaSyBzNR9eZqqGP-jELPxtLVcJRwnT7PSlsH4"
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"






'''
# Function to get AI response
def get_ai_response(user_id, question, course_mode="eciu"):
    """ Generate an AI response that adapts to personas, interaction style, user preferences, and learning history. """

    user_prefs = get_user_preferences(user_id)
    user_knowledge = get_user_knowledge(user_id)
    conversation_history = get_conversation_history(user_id, full_history=False)

    # ✅ **Determine if the user already learned about this topic**
    relevant_past_topics = [topic for topic in user_knowledge.get("learned_topics", []) if topic in question.lower()]
    if relevant_past_topics:
        knowledge_reference = f"\n\n**Note:** The user has previously learned about {', '.join(relevant_past_topics)}. The response should build on their existing knowledge."
    else:
        knowledge_reference = ""

    # **Step 1: If ECIU Mode, Generate Personalized Course Introduction**
    if course_mode == "eciu":
        relevant_courses = find_relevant_courses_csv(question)

        if relevant_courses:
            intro_prompt = f"""
            You are an AI Learning Assistant with a distinct **personality and tutoring style**.

            **User Preferences:**
            - Learning Style: {user_prefs['learning_style']}
            - Interaction Style: {user_prefs['interaction_style']}
            - Preferred Subjects: {", ".join(user_prefs['preferred_subjects'])}
            - Problem-Solving Style: {user_prefs['problem_solving']}
            - Persona: {user_prefs['presentation_style']}
            - Role Model: {user_prefs['role_model']}
            - Chat History (last 5 messages): {conversation_history}
            - {knowledge_reference}  # ✅ AI now remembers past learning!

            **User's Question:** "{question}"

            **Instructions for AI:**
            - **Before listing courses, explain WHY they are relevant based on user preferences.**
            - **Ensure a smooth transition from explanation to course listing.**
            - **If Socratic mode, guide the user to discover why these courses might be useful.**
            - **For Guided Hints, introduce hints before listing full course details.**
            - **Make the response engaging, natural, and structured.**

            Generate the response below:
            """

            intro_text = get_ai_summary(intro_prompt)

            course_recommendations = []
            for course in relevant_courses:
                course_summary_prompt = f"""
                Summarize the course **"{course['title']}"** in a way that is relevant to the user's learning style and goals.
                **Course Details:**
                - **Title:** {course['title']}
                - **Description:** {course.get('description', '')}
                - **Link:** {course['url']}
                
                **Instructions:**
                - Keep it **concise** yet **engaging**.
                - Highlight why **this course specifically** is useful based on the user’s subject interests.
                - Relate it to their **problem-solving and learning style**.
                - Avoid being too generic – personalize it to the user!

                Generate the response below:
                """

                ai_summary = get_ai_summary(course_summary_prompt)

                course_recommendations.append({
                    "title": course["title"],
                    "url": f"https://{course['url']}",
                    "description": ai_summary
                })

            # **🔹 Save Conversation & Extract Long-Term Memory**
            save_conversation_history(user_id, {"user": question, "ai": intro_text})  
            extract_user_knowledge(user_id, question)  

            return {
                "answer": intro_text,
                "recommended_courses": course_recommendations
            }

    # **Step 2: If Global Mode, Generate AI Response**
    full_prompt = f"""
    You are an AI Learning Mentor with an **interactive personality and adaptive tutoring style**.

    **User Preferences:**
    - Learning Style: {user_prefs['learning_style']}
    - Interaction Style: {user_prefs['interaction_style']}
    - Preferred Subjects: {", ".join(user_prefs['preferred_subjects'])}
    - Problem-Solving Style: {user_prefs['problem_solving']}
    - Personality Style: {user_prefs['personality_style']}
    - Persona: {user_prefs['presentation_style']}
    - Role Model: {user_prefs['role_model']}
    - Chat History (last 5 messages): {conversation_history}
    - {knowledge_reference}  # ✅ AI now builds on what the user has learned!

    **User's Question:** "{question}"

    **Instructions for AI:**
    - **Ensure responses match the user's personality settings.**
    - **If the user has already learned about this topic, build on their prior knowledge.**
    - **If Socratic mode, avoid direct answers and keep leading with questions.**
    - **For Guided Hints, provide hints first before the full explanation.**
    - **Explain new concepts progressively, making sure to connect them to what the user already knows.**

    Generate the response below:
    """

    if AI_MODE == "local":
        result = subprocess.run(["ollama", "run", "llama2:13b", full_prompt], capture_output=True, text=True)
        save_conversation_history(user_id, {"user": question, "ai": result.stdout.strip()})  
        extract_user_knowledge(user_id, question)
        return {"answer": result.stdout.strip(), "recommended_courses": []}

    elif AI_MODE == "api":
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": full_prompt}]}]}

        response = requests.post(GEMINI_URL, headers=headers, json=data)
        ai_response = response.json()["candidates"][0]["content"]["parts"][0]["text"] if response.status_code == 200 else f"❌ Error: {response.text}"

        save_conversation_history(user_id, {"user": question, "ai": ai_response})  
        extract_user_knowledge(user_id, question)
        return {"answer": ai_response, "recommended_courses": []}

    return {"answer": "❌ Error: Invalid AI mode selected.", "recommended_courses": []}

'''


def get_ai_response(user_id, question, course_mode="eciu"):
    """ Generate an AI response that adapts to personas, interaction style, user preferences, and learning history. """

    user_prefs = get_user_preferences(user_id)
    user_knowledge = get_user_knowledge(user_id)
    conversation_history = get_conversation_history(user_id, full_history=False)

    # ✅ **Determine if the user already learned about this topic**
    relevant_past_topics = [topic for topic in user_knowledge.get("learned_topics", []) if topic in question.lower()]
    if relevant_past_topics:
        knowledge_reference = f"\n\nIt appears the user has previously explored {', '.join(relevant_past_topics)}. The response should build upon this knowledge rather than repeating basic concepts."
    else:
        knowledge_reference = ""

    # **Step 1: If ECIU Mode, Generate Personalized Course Introduction**
    if course_mode == "eciu":
        relevant_courses = find_relevant_courses_csv(question)

        if relevant_courses:
            intro_prompt = f"""
            You are an AI Learning Assistant, offering personalized and engaging explanations.

            The user is interested in learning about "{question}" and has the following preferences:
            - Learning Style: {user_prefs['learning_style']}
            - Interaction Style: {user_prefs['interaction_style']}
            - Preferred Subjects: {", ".join(user_prefs['preferred_subjects'])}
            - Problem-Solving Approach: {user_prefs['problem_solving']}
            - Personality Style: {user_prefs['personality_style']}
            - Persona: {user_prefs['presentation_style']}
            - Role Model: {user_prefs['role_model']}
            - Chat History: {conversation_history}
            {knowledge_reference}

            Based on these preferences, generate a conversational and **engaging** explanation about why these ECIU courses would be beneficial for the user. 
            
            Do **not** list the courses yet. Instead, introduce why these particular courses are valuable in a way that fits their personality and learning approach.
            
            **Important Instructions:**
            - Avoid bullet points. Structure responses in natural flowing text.
            - If the user has previously struggled with similar topics, acknowledge that and adjust the tone accordingly.
            - If the user prefers guided hints, provide a thought-provoking statement before explaining outright.
            - Maintain the conversational tone of the chosen role model (e.g., if Einstein, use analogies and thought experiments).
            - Avoid being robotic—make it feel like an engaging discussion.
            - Keep the summary concise but engaging.
            - Ensure the transition between explanation and course listing is smooth—avoid abrupt changes like "Here are some courses:"
            - DO NOT use bullet points.

            Generate a response below:
            """

            intro_text = get_ai_summary(intro_prompt)

            # ✅ **Generate Course Summaries Without Repeating WHY They're Important**
            course_recommendations = []
            for course in relevant_courses:
                course_summary_prompt = f"""
                Summarize the course titled "{course['title']}" in a way that is engaging and tailored to the user's learning preferences.

                **Course Information:**
                - Title: {course['title']}
                - Description: {course.get('description', '')}
                - Link: {course['url']}

                **Instructions:**
                - Before listing courses, explain very briefly why these courses are relevant based on the user’s learning style, interests, and past discussions.
                - Avoid generic course listings—instead, introduce courses in a story-driven or contextual way that connects to the user's goals.
                - DO NOT use bullet points or lists—instead, weave course recommendations naturally into a conversational response.
                - If the user is in Socratic mode, do not immediately list courses. Instead, ask guiding questions to help them explore their learning path.
                - Keep the summary concise but engaging.
                - If the user has struggled with similar topics before, acknowledge this and adjust the tone accordingly.
                - Ensure the transition between explanation and course listing is smooth—avoid abrupt changes like "Here are some courses:"
                - For Guided Hints, introduce hints first before revealing full course details.
                - Relate it to the user’s subject interests and learning style.
                - Avoid repetition—each course should feel uniquely valuable.
                - If no relevant courses exist, suggest alternative strategies (such as searching within ECIU partner universities or recommending similar global courses).
                - DO NOT use bullet points.

                Generate the response below:
                """

                ai_summary = get_ai_summary(course_summary_prompt)

                course_recommendations.append({
                    "title": course["title"],
                    "url": f"https://{course['url']}",
                    "description": ai_summary
                })

            # ✅ **Save Chat History & Extract User Knowledge**
            save_conversation_history(user_id, {"user": question, "ai": intro_text})
            extract_user_knowledge(user_id, question)

            return {
                "answer": intro_text,
                "recommended_courses": course_recommendations
            }

    # **Step 2: If Global Mode, Generate AI Response**
    full_prompt = f"""
    You are an AI Learning Mentor with an engaging and adaptive personality and personalized recomendations.

    The user is asking: "{question}"

    **User Preferences:**
    - Learning Style: {user_prefs['learning_style']}
    - Interaction Style: {user_prefs['interaction_style']}
    - Preferred Subjects: {", ".join(user_prefs['preferred_subjects'])}
    - Problem-Solving Style: {user_prefs['problem_solving']}
    - Personality Style: {user_prefs['personality_style']}
    - Persona: {user_prefs['presentation_style']}
    - Role Model: {user_prefs['role_model']}
    - Chat History: {conversation_history}
    {knowledge_reference}

    **Instructions for AI:**
    - **Write responses as if speaking naturally** to the user. The text should feel **engaging, fluid, and conversational**—NOT robotic or overly structured.
    - **DO NOT use bullet points, lists, or rigid formatting.** Structure responses like an engaging discussion where ideas flow naturally.
    - **If the user asks for course recommendations, ALWAYS provide specific course names and summaries.** Do NOT just talk about learning methods—include real courses.
    - **Ensure course recommendations feel personal** by explaining why they are relevant based on the user’s background, interests, and learning preferences.
    - **Build on the user’s prior knowledge** if they have previously learned about this topic. Do not repeat what they already know.
    - **If Socratic mode is selected, do NOT give direct answers.** Instead, keep guiding the user with thought-provoking questions until they arrive at an answer.
    - **For Guided Hints, provide a hint first before revealing the full explanation.** Make it interactive like a real tutor.
    - **Use contractions, relatable examples, and an interactive tone** to make the response feel warm, engaging, and enjoyable to read.
    - **Make responses concise but rich.** Avoid overly long, exhausting paragraphs—keep explanations clear, dynamic, and engaging.
    - **Ensure the personality style is reflected in the response.** If the user selected “Humorous,” make it witty. If they prefer “Formal,” keep it structured.
    - **If the user asks about a course but no direct match is found, suggest closely related alternatives.** Do NOT leave them without a suggestion.
    - **Avoid repetitive or filler phrases.** Keep responses fresh, insightful, and to the point.

    Generate the response below:
    """

    if AI_MODE == "local":
        result = subprocess.run(["ollama", "run", "llama2:13b", full_prompt], capture_output=True, text=True)
        save_conversation_history(user_id, {"user": question, "ai": result.stdout.strip()})
        extract_user_knowledge(user_id, question)
        return {"answer": result.stdout.strip(), "recommended_courses": []}

    elif AI_MODE == "api":
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": full_prompt}]}]}

        response = requests.post(GEMINI_URL, headers=headers, json=data)
        ai_response = response.json()["candidates"][0]["content"]["parts"][0]["text"] if response.status_code == 200 else f"❌ Error: {response.text}"

        save_conversation_history(user_id, {"user": question, "ai": ai_response})
        extract_user_knowledge(user_id, question)
        return {"answer": ai_response, "recommended_courses": []}

    return {"answer": "❌ Error: Invalid AI mode selected.", "recommended_courses": []}






# AI function to generate course explanations
def get_ai_summary(prompt):
    """ Generate a short, engaging AI-generated course summary. """

    # 🔹 Fine-tuned AI Instructions
    refined_prompt = f"""
    You are an AI tutor recommending a course. **Keep the summary short (3-4 sentences max), engaging, and conversational**. 

    **Instructions:**
    - Explain why this course is interesting, **without making it sound like a formal description.**
    - *do not start like "Hey there ..." just jump to the point*
    - If possible, **relate it to the user’s learning style and interests.**
    - **Avoid overly technical jargon**—make it **relatable and easy to understand.**
    - **Use a human tone** (as if a passionate mentor were recommending the course).
    - **DO NOT list details like course length, syllabus, or requirements**—just highlight why it’s exciting!
    
    **Now, summarize this course in a natural, engaging way:**
    {prompt}
    """

    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": refined_prompt}]}]}

    try:
        response = requests.post(GEMINI_URL, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "❌ AI Summary Error."
    except requests.exceptions.RequestException as e:
        return f"❌ AI Request Failed: {str(e)}"



@app.route("/ask", methods=["POST"])
def ask():
    """Handles AI question requests, remembers session context, and updates long-term knowledge."""

    data = request.json
    user_id = data.get("user_id", "default_user")
    question = data.get("question", "").strip()
    course_mode = data.get("course_mode", "eciu")

    response_text = get_ai_response(user_id, question, course_mode)
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
