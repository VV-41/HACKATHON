const askBtn = document.getElementById("askBtn");
const queryInput = document.getElementById("queryInput");
const loading = document.getElementById("loading");
const responseBox = document.getElementById("responseBox");
const answerText = document.getElementById("answerText");
const categoryText = document.getElementById("categoryText");
const similarityText = document.getElementById("similarityText");
const topMatches = document.getElementById("topMatches");

askBtn.addEventListener("click", async () => {
    const query = queryInput.value.trim();

    if (!query) {
        alert("Please enter a legal question.");
        return;
    }

    loading.classList.remove("hidden");
    responseBox.classList.add("hidden");
    topMatches.innerHTML = "";

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ query: query })
        });

        const data = await response.json();
        loading.classList.add("hidden");

        if (data.error) {
            alert(data.error);
            return;
        }

        answerText.textContent = data.answer;
        categoryText.textContent = data.category;
        similarityText.textContent = data.similarity;

        if (data.top_matches && data.top_matches.length > 0) {
            data.top_matches.forEach(match => {
                const div = document.createElement("div");
                div.className = "match-card";
                div.innerHTML = `
                    <p><strong>Question:</strong> ${match.question}</p>
                    <p><strong>Category:</strong> ${match.category}</p>
                    <p><strong>Similarity:</strong> ${match.similarity}</p>
                `;
                topMatches.appendChild(div);
            });
        }

        responseBox.classList.remove("hidden");

    } catch (error) {
        loading.classList.add("hidden");
        alert("Something went wrong while contacting the server.");
        console.error(error);
    }
});