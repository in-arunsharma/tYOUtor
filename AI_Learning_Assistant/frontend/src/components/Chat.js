import React, { useState, useEffect, useRef } from 'react';
import { askAI } from '../api';
import './Chat.css';

export default function Chat({ userId }) {
    const [question, setQuestion] = useState("");
    const [conversation, setConversation] = useState([]);  
    const [courseMode, setCourseMode] = useState("eciu");
    const chatContainerRef = useRef(null);

    // Auto-scroll to bottom of chat when conversation updates
    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [conversation]);

    const askAI = async () => {
        if (!question.trim()) return;

        // Add user question to conversation with highlighted styling
        setConversation(prev => [...prev, { role: "user", text: question }]);

        const res = await fetch("http://127.0.0.1:5000/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: userId, question, course_mode: courseMode })
        });

        const data = await res.json();

        const aiResponse = data.answer?.answer || data.answer || "Error: No response received.";
        const recommendedCourses = data.answer?.recommended_courses || [];

        const formattedResponse = aiResponse
            .replace(/\*\*(.*?)\*\*/g, "<b>$1</b>")  
            .replace(/\n/g, "<br>"); 

        if (aiResponse) {
            setConversation(prev => [...prev, { role: "ai", text: formattedResponse, isHTML: true }]);
        }

        if (recommendedCourses.length > 0) {
            setConversation(prev => [
                ...prev,
                { role: "ai", text: "<b>Here are some recommended courses:</b>", isHTML: true },
                { role: "courses", content: recommendedCourses.map((course, index) => (
                    <div key={index} className="course-card">
                        <h4>{course.title}</h4>
                        <p>{course.description}</p>
                        <a href={course.url} target="_blank" rel="noopener noreferrer">🔗 Course Link</a>
                    </div>
                )) }
            ]);
        }

        setQuestion("");
    };

    return (
        <div className="chat-container">
            <h2>💬 AI Learning Assistant</h2>

            <div className="mode-selector">
                <label>Course Mode: </label>
                <button 
                    className={`mode-button ${courseMode === "eciu" ? "active" : ""}`}
                    onClick={() => setCourseMode("eciu")}>
                    ECIU Courses <small>(default)</small>
                </button>
                <button 
                    className={`mode-button ${courseMode === "global" ? "active" : ""}`}
                    onClick={() => setCourseMode("global")}>
                    Global Courses
                </button>
            </div>

            <div className="chat-messages" ref={chatContainerRef}>
                {conversation.map((msg, index) => {
                    if (msg.role === "user") {
                        return (
                            <div key={index} className="user-message">
                                <div className="message-bubble user">
                                    <span className="user-label">You</span>
                                    <p>{msg.text}</p>
                                </div>
                            </div>
                        );
                    } else if (msg.role === "ai") {
                        return (
                            <div key={index} className="ai-message">
                                <div className="message-bubble ai">
                                    <span className="ai-label">AI Assistant</span>
                                    {msg.isHTML ? (
                                        <p dangerouslySetInnerHTML={{ __html: msg.text }} />
                                    ) : (
                                        <p>{msg.text}</p>
                                    )}
                                </div>
                            </div>
                        );
                    } else if (msg.role === "courses") {
                        return (
                            <div key={index} className="courses-container">
                                {msg.content}
                            </div>
                        );
                    }
                    return null;
                })}
            </div>

            <div className="chat-input">
                <input 
                    type="text" 
                    value={question} 
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Ask something..."
                    onKeyDown={(e) => e.key === 'Enter' && askAI()}
                />
                <button onClick={askAI}>Ask</button>
            </div>
        </div>
    );
}