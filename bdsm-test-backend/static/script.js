document.addEventListener("DOMContentLoaded", () => {
  console.log("Script loaded");

  const questionsContainer = document.getElementById("questionsContainer");
  const form = document.getElementById("testForm");

  fetch("/questions")
    .then(res => {
      console.log("Fetch /questions status:", res.status);
      return res.json();
    })
    .then(questions => {
      console.log("Questions loaded:", questions);

      if (!Array.isArray(questions)) {
        console.error("Questions is not an array!");
        return;
      }

      questionsContainer.innerHTML = "";

      questions.forEach(q => {
        const div = document.createElement("div");
        div.className = "question-block";

        const p = document.createElement("p");
        p.textContent = q.question;

        const optionsDiv = document.createElement("div");
        optionsDiv.className = "options";

        [
          "Strongly Disagree",
          "Disagree",
          "Neutral",
          "Agree",
          "Strongly Agree"
        ].forEach((label, i) => {
          const optionLabel = document.createElement("label");

          const input = document.createElement("input");
          input.type = "radio";
          input.name = `q_${q.id}`;
          input.value = String(i + 1);

          optionLabel.appendChild(input);
          optionLabel.append(` ${label}`);
          optionsDiv.appendChild(optionLabel);
        });

        div.appendChild(p);
        div.appendChild(optionsDiv);
        questionsContainer.appendChild(div);
      });
    })
    .catch(err => console.error("Error loading questions:", err));

  form.addEventListener("submit", e => {
    e.preventDefault();

    const answers = [];

    document.querySelectorAll(".question-block").forEach(block => {
      const checked = block.querySelector('input[type="radio"]:checked');
      if (!checked) return;

      const id = parseInt(checked.name.replace("q_", ""));
      const answer = parseInt(checked.value);

      answers.push({ id, answer });
    });

    fetch("/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(answers)
    })
      .then(res => res.json())
      .then(result => {
        console.log("Results:", result);

        const results = document.getElementById("results");
        const traitsContainer = document.getElementById("traitsContainer");
        traitsContainer.innerHTML = "";

        const sortedTraits = Object.entries(result.trait_percentages || {})
          .sort((a, b) => b[1] - a[1]); // highest → lowest

        sortedTraits.forEach(([trait, value]) => {
          const p = document.createElement("p");
          p.className = "trait";

          p.innerHTML = `
            <span class="trait-name">${trait}</span>
            <span class="score">${Math.round(value)}%</span>
          `;

          traitsContainer.appendChild(p);
        });

        results.style.display = "block";
        results.scrollIntoView({ behavior: "smooth" });
      })
      .catch(err => console.error("Error submitting answers:", err));
  });
});