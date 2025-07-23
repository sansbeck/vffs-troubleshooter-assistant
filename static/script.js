document.addEventListener("DOMContentLoaded", () => {
  const select = document.getElementById("issue-select");
  const guideText = document.getElementById("guide-text");
  const factList = document.getElementById("fact-list");
  const askBox = document.getElementById("ask-box");
  const solution = document.getElementById("solution");
  const queryInput = document.getElementById("query-input");
  const askBtn = document.getElementById("ask-btn");
  const aiResponse = document.getElementById("ai-response");

  select.addEventListener("change", () => {
    const issue = select.value;
    fetch("/get_solution", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ issue })
    })
    .then(res => res.json())
    .then(data => {
      guideText.innerHTML = "";
      factList.innerHTML = "";
      aiResponse.textContent = "";

      data.guide?.forEach(step => {
        const li = document.createElement("li");
        li.textContent = step;
        guideText.appendChild(li);
      });

      data.facts?.forEach(fact => {
        const li = document.createElement("li");
        li.textContent = fact;
        factList.appendChild(li);
      });

      solution.classList.remove("hidden");
      askBox.classList.remove("hidden");
    });
  });

  askBtn.addEventListener("click", () => {
    const query = queryInput.value.trim();
    const issue = select.value;
    if (!query) return;

    aiResponse.innerHTML = "<em>Thinking...</em>";

    fetch("/ask_ai", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, issue })
    })
    .then(res => res.json())
    .then(data => {
      aiResponse.innerHTML = data.response
  ? `<div style="white-space: pre-line; line-height: 1.7">${data.response}</div>`
  : "<span style='color:red'>❌ No answer.</span>";

    })
    .catch(() => {
      aiResponse.innerHTML = "<span style='color:red'>⚠️ API Error</span>";
    });
  });
});