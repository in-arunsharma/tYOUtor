import React, { useState } from "react";

export default function Chat({ userId, preferences }) {
    const [question, setQuestion] = useState("");
    const [response, setResponse] = useState("");

    const askAI = async () => {
        try {
            const res = await fetch("http://127.0.0.1:5000/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_id: userId, question })
            });
    
            if (!res.ok) {
                throw new Error(`Server error: ${res.status}`);
            }
    
            const data = await res.json();
            setResponse(data.answer);
        } catch (error) {
            console.error("❌ Failed to fetch:", error);
            setResponse("❌ Error: Unable to reach AI server.");
        }
    };
    

    return (
        <div>
            <h2>💬 Chat</h2>
            <input value={question} onChange={(e) => setQuestion(e.target.value)} />
            <button onClick={askAI}>Ask</button>
            <p>🎙 AI Response: {response}</p>
        </div>
    );
}
