import React, { useState } from "react";

export default function Chat({ userId }) {
    const [question, setQuestion] = useState("");
    const [conversation, setConversation] = useState([]);  // Store chat history

    const askAI = async () => {
        if (!question.trim()) return;  // Ignore empty questions

        // Add user's question to conversation
        setConversation(prev => [...prev, { role: "user", text: question }]);

        // Send request to backend
        const res = await fetch("http://127.0.0.1:5000/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: userId, question })
        });

        const data = await res.json();

        // Add AI response to conversation
        setConversation(prev => [...prev, { role: "ai", text: data.answer }]);
        
        // Clear input field
        setQuestion("");
    };

    return (
        <div className="chat-container">
            <h2>💬 AI Learning Assistant</h2>
            
            {/* Chat History */}
            <div className="chat-history">
                {conversation.map((msg, index) => (
                    <p key={index} className={msg.role === "user" ? "user-message" : "ai-message"}>
                        <b>{msg.role === "user" ? "👤 You:" : "🤖 AI:"}</b> {msg.text}
                    </p>
                ))}
            </div>

            {/* Input Field */}
            <input 
                type="text" 
                value={question} 
                onChange={(e) => setQuestion(e.target.value)} 
                placeholder="Ask something..."
            />
            <button onClick={askAI}>Ask</button>
        </div>
    );
}
