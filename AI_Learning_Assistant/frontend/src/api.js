export async function askAI(question) {
    const response = await fetch("http://127.0.0.1:5000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({question })
    });

    if (!response.ok) {
        throw new Error("Failed to fetch AI response");
    }

    const data = await response.json();
    return data.answer;
}
