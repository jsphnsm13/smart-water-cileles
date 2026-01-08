function sendChat() {
    const input = document.getElementById("userInput");
    const msg = input.value.trim();
    if (!msg) return;

    const box = document.getElementById("chat-box");

    box.innerHTML += `
        <div class="chat user">
            <span>🧑</span><p>${msg}</p>
        </div>
    `;

    input.value = "";
    box.scrollTop = box.scrollHeight;

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg })
    })
    .then(res => res.json())
    .then(data => {
        box.innerHTML += `
            <div class="chat ai">
                <span>🤖</span><p>${data.reply}</p>
            </div>
        `;
        box.scrollTop = box.scrollHeight;
    })
    .catch(() => {
        box.innerHTML += `
            <div class="chat ai">
                <span>🤖</span><p>⚠️ AI tidak tersedia.</p>
            </div>
        `;
    });
}
