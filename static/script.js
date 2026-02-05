async function askQuestion() {
    const input = document.getElementById("question");
    const chat = document.getElementById("chat");

    const question = input.value.trim();
    if (!question) return;

    input.value = "";

    chat.innerHTML += `<p><b>You:</b> ${question}</p>`;

    const response = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
    });

    const data = await response.json();

    chat.innerHTML += `<p><b>ChatDIS:</b> ${data.answer}</p>`;
}
