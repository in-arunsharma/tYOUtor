import React, { useState } from "react";

export default function Chat({ userId }) {
    const [question, setQuestion] = useState("");
    const [conversation, setConversation] = useState([]);  
    const [courseMode, setCourseMode] = useState("eciu");

    const askAI = async () => {
        if (!question.trim()) return;

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
                <label>Choose Course Mode: </label>
                <button 
                    className={courseMode === "eciu" ? "selected" : ""}
                    onClick={() => setCourseMode("eciu")}
                >
                    🎓 ECIU Courses Only
                </button>
                <button 
                    className={courseMode === "global" ? "selected" : ""}
                    onClick={() => setCourseMode("global")}
                >
                    🌍 Global Courses
                </button>
            </div>

            <div className="chat-history">
                {conversation.map((msg, index) => (
                    msg.role === "courses" ? (
                        <div key={index} className="course-recommendations">
                            {msg.content}
                        </div>
                    ) : (
                        <p key={index} className={msg.role === "user" ? "user-message" : "ai-message"}
                            dangerouslySetInnerHTML={{ __html: msg.text }}>
                        </p>
                    )
                ))}
            </div>

            <input type="text" value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask something..." />
            <button onClick={askAI}>Ask</button>
        </div>
    );
}