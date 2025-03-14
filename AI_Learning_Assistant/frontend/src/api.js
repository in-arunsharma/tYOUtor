export async function askAI(userId, question, courseMode) {
    const response = await fetch("http://127.0.0.1:5000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, question, course_mode: courseMode })
    });

    if (response.ok) {
        return await response.json();
    } else {
        return "❌ Error fetching AI response.";
    }
}
