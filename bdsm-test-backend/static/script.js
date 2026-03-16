window.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("testForm");
  const questionsContainer = document.getElementById("questionsContainer");

  fetch("http://192.168.0.218:5000/questions")
    .then(response => response.json())
    .then(questions => {
      console.log(questions);
      questions.forEach(question => {
        const div = document.createElement("div");
        div.className = "question-block";
        const optionsDiv = document.createElement("div");
        optionsDiv.className = "options";
        optionsDiv.innerHTML = ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"].map((label, i) => `
          <label><input type="radio" name="q${question.id}" value="${(i + 1) * 0.25}"> ${label}</label>
        `).join("");
        
        div.innerHTML = `<p>${question.text}</p>`;
        div.appendChild(optionsDiv);
        questionsContainer.appendChild(div);
      });
    })
    .catch(error => {
      console.error('Error loading questions:', error);
    });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const questions = await fetch("https://www.fazbdsmtest.co.uk/questions").then(r => r.json());
    const answers = questions.map(q => {
      const checked = document.querySelector(`input[name="q${q.id}"]:checked`);
      return {
        id: q.id,
        answer: checked ? parseFloat(checked.value) : 0
      };
    });

    try {
      const response = await fetch("https://www.fazbdsmtest.co.uk/submit", {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(answers)
      });
      const results = await response.json();
      displayResults(results);
    } catch (error) {
      console.error('Error submitting answers:', error);
    }
  });

  function displayResults(traits) {
    const traitsContainer = document.getElementById('traitsContainer');
    traitsContainer.innerHTML = '';
    
    const sortedTraits = Object.entries(traits)
      .sort((a, b) => b[1] - a[1]);
    
    sortedTraits.forEach(([trait, score]) => {
      const div = document.createElement('div');
      div.innerHTML = `<p><strong>${trait}:</strong> ${score.toFixed(2)}</p>`;
      traitsContainer.appendChild(div);
    });
    
    document.getElementById('results').style.display = 'block';
  }
});
