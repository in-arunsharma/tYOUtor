import React, { useState } from "react";
import Chat from "./components/Chat";
import Settings from "./components/Settings";

export default function App() {
    const [userId] = useState("test_user_123"); // Temporary hardcoded user ID
    const [preferences, setPreferences] = useState({});

    return (
        <div className="app-container">
            <Settings userId={userId} onPreferenceChange={setPreferences} />
            <Chat userId={userId} preferences={preferences} />
        </div>
    );
}
