import React, { useState } from "react";

import "../settings.css";


export default function Settings({ userId, onPreferenceChange }) {
    const [preferences, setPreferences] = useState({
        learning_style: "step_by_step",
        presentation_style: "standard",
        knowledge_level: "intermediate",
        interaction_style: "tutor",
        problem_solving: "guided",
        personality_style: "casual",
        role_model: "feynman",
        learning_speed: "medium",
        explanation_length: "detailed"
    });

    // Handle form input changes
    const handleChange = (event) => {
        const { name, value } = event.target;
        setPreferences(prev => ({ ...prev, [name]: value }));
    };

    // Send updated preferences to backend
    const updatePreferences = async () => {
        const response = await fetch("http://127.0.0.1:5000/update-preferences", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: userId, ...preferences })
        });

        if (response.ok) {
            console.log("✅ Preferences updated successfully!");
            onPreferenceChange(preferences); // Notify parent component
        } else {
            console.error("❌ Failed to update preferences.");
        }
    };

    return (
        <div className="settings">
            <h2>🛠️ Customize Your Learning Experience</h2>

            <label>🎓 Learning Style:</label>
            <select name="learning_style" value={preferences.learning_style} onChange={handleChange}>
                <option value="visual">Visual</option>
                <option value="step_by_step">Step-by-Step</option>
                <option value="textual">Textual</option>
                <option value="storytelling">Storytelling</option>
                <option value="interactive">Interactive</option>
            </select>

            <label>🧑‍🏫 Presentation Style:</label>
            <select name="presentation_style" value={preferences.presentation_style} onChange={handleChange}>
                <option value="standard">Standard</option>
                <option value="einstein">Einstein</option>
                <option value="curie">Curie</option>
                <option value="feynman">Feynman</option>
                <option value="hawking">Hawking</option>
                <option value="shakespeare">Shakespeare</option>
                
            </select>

            <label>📚 Knowledge Level:</label>
            <select name="knowledge_level" value={preferences.knowledge_level} onChange={handleChange}>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
            </select>

            <label>💡 Interaction Style:</label>
            <select name="interaction_style" value={preferences.interaction_style} onChange={handleChange}>
                <option value="tutor">Tutor</option>
                <option value="socratic">Socratic Questioning</option>
                <option value="direct">Direct Answers</option>
            </select>

            <label>🧠 Problem-Solving Style:</label>
            <select name="problem_solving" value={preferences.problem_solving} onChange={handleChange}>
                <option value="guided">Guided Hints</option>
                <option value="direct">Direct Answer</option>
            </select>

            <label>🎭 Personality Style:</label>
            <select name="personality_style" value={preferences.personality_style} onChange={handleChange}>
                <option value="formal">Formal</option>
                <option value="casual">Casual</option>
                <option value="humorous">Humorous</option>
                <option value="inspirational">Inspirational</option>
                <option value="socratic">Socratic</option>
            </select>

            <label>🚀 Role Model:</label>
            <select name="role_model" value={preferences.role_model} onChange={handleChange}>
                <option value="feynman">Feynman</option>
                <option value="da_vinci">Da Vinci</option>
                <option value="hawking">Hawking</option>
                <option value="einstein">Einstein</option>
                <option value="curie">Curie</option>
            </select>

            <button onClick={updatePreferences}>Save Preferences</button>
        </div>
    );
}