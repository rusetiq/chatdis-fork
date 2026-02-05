async function askQuestion() {
    const input = document.getElementById("question");
    const chat = document.getElementById("chat");

    const question = input.value.trim();
    if (!question) return;

    // 1. Clear input
    input.value = "";

    // 2. Add User Message Bubble
    chat.innerHTML += `
        <div class="message user-message">
            ${question}
        </div>
    `;

    // 3. Create a unique ID for the "Thinking" bubble
    const thinkingId = "think-" + Date.now();
    
    // 4. Add the "Thinking" placeholder bubble
    chat.innerHTML += `
        <div id="${thinkingId}" class="message bot-message thinking">
            ChatDIS is thinking...
        </div>
    `;

    // Scroll to bottom so user sees the "Thinking" state
    chat.scrollTop = chat.scrollHeight;

    // 5. Fetch from Backend
    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question })
        });

        const data = await response.json();

        // 6. Find the thinking bubble
        const thinkingBubble = document.getElementById(thinkingId);
        
        // Remove the 'thinking' class to stop the pulse animation
        thinkingBubble.classList.remove("thinking");
        
        // --- THE BIG CHANGE IS HERE ---
        // Instead of .replace(), we use marked.parse() to handle bold, tables, and lists properly
        thinkingBubble.innerHTML = marked.parse(data.answer);

    } catch (error) {
        // If it fails, update the thinking bubble with the error message
        const thinkingBubble = document.getElementById(thinkingId);
        if (thinkingBubble) {
            thinkingBubble.classList.remove("thinking");
            thinkingBubble.innerHTML = "Sorry, I'm having trouble connecting right now.";
        }
    }

    // Final scroll to bottom
    chat.scrollTop = chat.scrollHeight;
}

// Allow pressing "Enter" to send
document.getElementById("question").addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        askQuestion();
    }
});

// Function for Quick Action buttons
function quickAsk(text) {
    document.getElementById("question").value = text;
    askQuestion();
}
