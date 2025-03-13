import React, { useState } from "react";
import Chat from "./components/Chat";
import Settings from "./components/Settings";

export default function App() {
    const [userId] = useState("test_user_123");  // Example user ID
    const [preferences, setPreferences] = useState({});  // Store user settings

    return (
        <div className="app">
            <h1>🚀 AI Learning Assistant</h1>
            <Settings userId={userId} onPreferenceChange={setPreferences} />
            <Chat userId={userId} preferences={preferences} />
        </div>
    );
}
