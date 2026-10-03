document.addEventListener("DOMContentLoaded", () => {
    const question = document.getElementById("question");
    const ask = document.getElementById("askButton");
    const clear = document.getElementById("clearButton");
    const response = document.getElementById("response");

    ask.addEventListener("click", async () => {
        const text = question.value.trim();

        if (!text) {
            response.innerHTML = '<div class="error">Please enter a question.</div>';
            return;
        }

        ask.disabled = true;
        ask.textContent = "Thinking...";
        response.innerHTML = '<div class="ai-response">🤖 EduGenie is thinking...</div>';

        try {
            const res = await fetch("/api/ask", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({question: text, history: []})
            });

            const data = await res.json();

            if (!res.ok || !data.success) {
                throw new Error(data.error || "Unable to get answer.");
            }

            response.innerHTML = `<div class="ai-response">${formatAnswer(data.answer)}</div>`;
        } catch (error) {
            response.innerHTML = `<div class="error">❌ ${escapeHtml(error.message)}</div>`;
        } finally {
            ask.disabled = false;
            ask.textContent = "Ask EduGenie";
        }
    });

    clear.addEventListener("click", () => {
        question.value = "";
        response.innerHTML = '<p class="placeholder">Your answer will appear here...</p>';
        question.focus();
    });

    question.addEventListener("keydown", event => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            ask.click();
        }
    });

    function escapeHtml(value) {
        const div = document.createElement("div");
        div.textContent = value;
        return div.innerHTML;
    }

    function formatAnswer(value) {
        let html = escapeHtml(value);
        html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
        html = html.replace(/^### (.*)$/gm, "<h4>$1</h4>");
        html = html.replace(/^## (.*)$/gm, "<h3>$1</h3>");
        html = html.replace(/^# (.*)$/gm, "<h2>$1</h2>");
        html = html.replace(/\n/g, "<br>");
        return html;
    }
});
