import React, { useState, useEffect } from 'react';
import './Settings.css';

export default function Settings({ userId, onPreferenceChange }) {
    const [preferences, setPreferences] = useState({
        learning_style: "step_by_step",
        custom_learning_style: "",
        personality_style: "casual",
        explanation_length: "balanced",
        interaction_style: "tutor",
        presentation_style: "standard",
        custom_presentation_style: "",
        knowledge_level: "intermediate",
        custom_knowledge_level: "",
        problem_solving: "guided",
        role_model: "",
        custom_role_model: "",
        learning_deadline: "flexible",
        custom_deadline: "",
        time_dedication: "medium",
        custom_time_dedication: "",
        preferred_subjects: ["physics", "math"],
        custom_subject: ""
    });
    
    const [saveStatus, setSaveStatus] = useState("");

    useEffect(() => {
        // Fetch current preferences when component loads
        fetchUserPreferences();
    }, [userId]);

    const fetchUserPreferences = async () => {
        try {
            const response = await fetch(`http://127.0.0.1:5000/get-preferences?user_id=${userId}`);
            if (response.ok) {
                const data = await response.json();
                setPreferences(prev => ({
                    ...prev,
                    ...data.preferences
                }));
            }
        } catch (error) {
            console.error("Error fetching preferences:", error);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setPreferences(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleCustomOption = (field, customValue) => {
        if (customValue.trim()) {
            setPreferences(prev => ({
                ...prev,
                [field]: customValue
            }));
        }
    };

    const handleAddSubject = () => {
        if (preferences.custom_subject.trim()) {
            setPreferences(prev => ({
                ...prev,
                preferred_subjects: [...prev.preferred_subjects, prev.custom_subject],
                custom_subject: ""
            }));
        }
    };

    const handleRemoveSubject = (subject) => {
        setPreferences(prev => ({
            ...prev,
            preferred_subjects: prev.preferred_subjects.filter(s => s !== subject)
        }));
    };

    const savePreferences = async () => {
        try {
            const dataToSend = {
                user_id: userId,
                learning_style: preferences.learning_style === "custom" ? 
                    preferences.custom_learning_style : preferences.learning_style,
                personality_style: preferences.personality_style,
                explanation_length: preferences.explanation_length,
                interaction_style: preferences.interaction_style,
                presentation_style: preferences.presentation_style === "custom" ? 
                    preferences.custom_presentation_style : preferences.presentation_style,
                knowledge_level: preferences.knowledge_level === "custom" ? 
                    preferences.custom_knowledge_level : preferences.knowledge_level,
                problem_solving: preferences.problem_solving,
                role_model: preferences.role_model === "none" ? "" : 
                    (preferences.role_model === "custom" ? preferences.custom_role_model : preferences.role_model),
                preferred_subjects: preferences.preferred_subjects,
                learning_deadline: preferences.learning_deadline === "custom" ? 
                    preferences.custom_deadline : preferences.learning_deadline,
                time_dedication: preferences.time_dedication === "custom" ? 
                    preferences.custom_time_dedication : preferences.time_dedication
            };

            const response = await fetch("http://127.0.0.1:5000/update-preferences", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(dataToSend)
            });

            if (response.ok) {
                setSaveStatus("✅ Preferences saved successfully!");
                setTimeout(() => setSaveStatus(""), 3000);
                onPreferenceChange(preferences); // Notify parent component
            } else {
                setSaveStatus("❌ Error saving preferences");
            }
        } catch (error) {
            console.error("Error saving preferences:", error);
            setSaveStatus("❌ Error saving preferences");
        }
    };

    return (
        <div className="settings-container">
            <h2>🛠️ Customize Your Learning Experience</h2>
            
            <div className="settings-section">
                <h3>How You Learn</h3>
                
                <div className="preference-group">
                    <label>Learning Style:</label>
                    <select 
                        name="learning_style" 
                        value={preferences.learning_style} 
                        onChange={handleInputChange}
                    >
                        <option value="visual">Visual</option>
                        <option value="step_by_step">Step-by-Step</option>
                        <option value="storytelling">Storytelling</option>
                        <option value="interactive">Interactive</option>
                        <option value="custom">Custom...</option>
                    </select>
                    {preferences.learning_style === "custom" && (
                        <div className="custom-input">
                            <input 
                                type="text" 
                                name="custom_learning_style" 
                                value={preferences.custom_learning_style} 
                                onChange={handleInputChange}
                                placeholder="Describe your learning style"
                            />
                            <button onClick={() => handleCustomOption("learning_style", preferences.custom_learning_style)}>Apply</button>
                        </div>
                    )}
                </div>

                <div className="preference-group">
                    <label>Knowledge Level:</label>
                    <select 
                        name="knowledge_level" 
                        value={preferences.knowledge_level} 
                        onChange={handleInputChange}
                    >
                        <option value="beginner">Beginner</option>
                        <option value="intermediate">Intermediate</option>
                        <option value="advanced">Advanced</option>
                        <option value="expert">Expert</option>
                        <option value="custom">Custom...</option>
                    </select>
                    {preferences.knowledge_level === "custom" && (
                        <div className="custom-input">
                            <input 
                                type="text" 
                                name="custom_knowledge_level" 
                                value={preferences.custom_knowledge_level} 
                                onChange={handleInputChange}
                                placeholder="Describe your knowledge level"
                            />
                            <button onClick={() => handleCustomOption("knowledge_level", preferences.custom_knowledge_level)}>Apply</button>
                        </div>
                    )}
                </div>
                
                <div className="preference-group">
                    <label>Preferred Subjects:</label>
                    <div className="subjects-container">
                        {preferences.preferred_subjects.map((subject, index) => (
                            <div key={index} className="subject-tag">
                                {subject}
                                <span className="remove-subject" onClick={() => handleRemoveSubject(subject)}>×</span>
                            </div>
                        ))}
                    </div>
                    <div className="add-subject">
                        <input 
                            type="text" 
                            name="custom_subject" 
                            value={preferences.custom_subject} 
                            onChange={handleInputChange}
                            placeholder="Add a subject..."
                        />
                        <button onClick={handleAddSubject}>Add</button>
                    </div>
                </div>
            </div>

            <div className="settings-section">
                <h3>Time Management</h3>
                
                <div className="preference-group">
                    <label>Learning Deadline:</label>
                    <select 
                        name="learning_deadline" 
                        value={preferences.learning_deadline} 
                        onChange={handleInputChange}
                    >
                        <option value="flexible">Flexible (No deadline)</option>
                        <option value="1_day">1 Day</option>
                        <option value="1_week">1 Week</option>
                        <option value="1_month">1 Month</option>
                        <option value="custom">Custom...</option>
                    </select>
                    {preferences.learning_deadline === "custom" && (
                        <div className="custom-input">
                            <input 
                                type="text" 
                                name="custom_deadline" 
                                value={preferences.custom_deadline} 
                                onChange={handleInputChange}
                                placeholder="Specify your deadline"
                            />
                            <button onClick={() => handleCustomOption("learning_deadline", preferences.custom_deadline)}>Apply</button>
                        </div>
                    )}
                </div>
                
                <div className="preference-group">
                    <label>Time Dedication:</label>
                    <select 
                        name="time_dedication" 
                        value={preferences.time_dedication} 
                        onChange={handleInputChange}
                    >
                        <option value="low">Minimal (15-30 min/day)</option>
                        <option value="medium">Moderate (1-2 hours/day)</option>
                        <option value="high">Intensive (3+ hours/day)</option>
                        <option value="custom">Custom...</option>
                    </select>
                    {preferences.time_dedication === "custom" && (
                        <div className="custom-input">
                            <input 
                                type="text" 
                                name="custom_time_dedication" 
                                value={preferences.custom_time_dedication} 
                                onChange={handleInputChange}
                                placeholder="Specify your time dedication"
                            />
                            <button onClick={() => handleCustomOption("time_dedication", preferences.custom_time_dedication)}>Apply</button>
                        </div>
                    )}
                </div>
            </div>

            <div className="settings-section">
                <h3>Communication Style</h3>
                
                <div className="preference-group">
                    <label>Personality Style:</label>
                    <select 
                        name="personality_style" 
                        value={preferences.personality_style} 
                        onChange={handleInputChange}
                    >
                        <option value="formal">Formal</option>
                        <option value="casual">Casual</option>
                        <option value="humorous">Humorous</option>
                        <option value="inspirational">Inspirational</option>
                    </select>
                </div>
                
                <div className="preference-group">
                    <label>Explanation Length:</label>
                    <select 
                        name="explanation_length" 
                        value={preferences.explanation_length} 
                        onChange={handleInputChange}
                    >
                        <option value="brief">Brief Summaries</option>
                        <option value="balanced">Balanced</option>
                        <option value="detailed">Detailed Explanations</option>
                    </select>
                </div>
                
                <div className="preference-group">
                    <label>Interaction Style:</label>
                    <select 
                        name="interaction_style" 
                        value={preferences.interaction_style} 
                        onChange={handleInputChange}
                    >
                        <option value="direct">Direct Answers</option>
                        <option value="tutor">Interactive Tutor</option>
                        <option value="guided">Guided Hints</option>
                        <option value="socratic">Socratic Questioning</option>
                    </select>
                </div>
                
                <div className="preference-group">
                    <label>Presentation Style:</label>
                    <select 
                        name="presentation_style" 
                        value={preferences.presentation_style} 
                        onChange={handleInputChange}
                    >
                        <option value="standard">Standard Assistant</option>
                        <option value="einstein">Einstein</option>
                        <option value="feynman">Feynman</option>
                        <option value="hawking">Hawking</option>
                        <option value="curie">Curie</option>
                        <option value="custom">Custom...</option>
                    </select>
                    {preferences.presentation_style === "custom" && (
                        <div className="custom-input">
                            <input 
                                type="text" 
                                name="custom_presentation_style" 
                                value={preferences.custom_presentation_style} 
                                onChange={handleInputChange}
                                placeholder="Describe a presentation style"
                            />
                            <button onClick={() => handleCustomOption("presentation_style", preferences.custom_presentation_style)}>Apply</button>
                        </div>
                    )}
                </div>
                
                <div className="preference-group">
                    <label>Role Model:</label>
                    <select 
                        name="role_model" 
                        value={preferences.role_model} 
                        onChange={handleInputChange}
                    >
                        <option value="none">None (No role model needed)</option>
                        <option value="feynman">Richard Feynman</option>
                        <option value="einstein">Albert Einstein</option>
                        <option value="curie">Marie Curie</option>
                        <option value="hawking">Stephen Hawking</option>
                        <option value="custom">Custom...</option>
                    </select>
                    {preferences.role_model === "custom" && (
                        <div className="custom-input">
                            <input 
                                type="text" 
                                name="custom_role_model" 
                                value={preferences.custom_role_model} 
                                onChange={handleInputChange}
                                placeholder="Name your role model"
                            />
                            <button onClick={() => handleCustomOption("role_model", preferences.custom_role_model)}>Apply</button>
                        </div>
                    )}
                </div>
            </div>
            
            <div className="settings-actions">
                <button className="save-button" onClick={savePreferences}>Save Preferences</button>
                {saveStatus && <div className="save-status">{saveStatus}</div>}
            </div>
        </div>
    );
}