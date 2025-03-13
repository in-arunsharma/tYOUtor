import React, { useState } from "react";
import { askAI } from "./api";

function Chat() {
    const [question, setQuestion] = useState("");
    const [response, setResponse] = useState("");
    const [learningStyle, setLearningStyle] = useState("default");

    const handleSubmit = async () => {
        if (!question.trim()) return;
        setResponse("Thinking...");
        try {
            const answer = await askAI(question, learningStyle);
            setResponse(answer);
        } catch (error) {
            setResponse("Error fetching response.");
        }
    };

    return (
        <div>
            <h1>AI Learning Assistant</h1>
            <select value={learningStyle} onChange={(e) => setLearningStyle(e.target.value)}>
                <option value="default">Default</option>
                <option value="Einstein">Einstein-style</option>
                <option value="Step-by-step">Step-by-step</option>
                <option value="Storytelling">Storytelling</option>
            </select>
            <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask me a question..."
            />
            <button onClick={handleSubmit}>Ask</button>
            <p><strong>AI:</strong> {response}</p>
        </div>
    );
}

export default Chat;
