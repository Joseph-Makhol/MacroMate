const form = document.getElementById("macro-form");
const resultsSection = document.getElementById("results");
const errorMessage = document.getElementById("error-message");

const calculateButton = document.getElementById("calculate-btn");
const coachButton = document.getElementById("coach-btn");

const coachSection = document.getElementById("coach-section");
const coachTitle = document.getElementById("coach-title");
const coachSummary = document.getElementById("coach-summary");
const coachAdvice = document.getElementById("coach-advice");
const coachDisclaimer = document.getElementById("coach-disclaimer");

let latestResults = null;
let latestUser = null;

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    errorMessage.textContent = "";
    resultsSection.classList.add("hidden");
    coachSection.classList.add("hidden");

    calculateButton.disabled = true;
    calculateButton.textContent = "Calculating...";

    latestUser = {
        age: Number(document.getElementById("age").value),
        sex: document.getElementById("sex").value,
        height_cm: Number(document.getElementById("height").value),
        weight_kg: Number(document.getElementById("weight").value),
        activity_level: document.getElementById("activity").value,
        goal: document.getElementById("goal").value
    };

    try {
        const response = await fetch("http://127.0.0.1:8000/calculate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(latestUser)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Unable to calculate.");
        }

        latestResults = data;

        document.getElementById("calories").textContent = data.calories;
        document.getElementById("protein").textContent = data.protein_grams;
        document.getElementById("carbs").textContent = data.carbs_grams;
        document.getElementById("fat").textContent = data.fat_grams;

        resultsSection.classList.remove("hidden");
    }
    catch (error) {
        console.error(error);

        errorMessage.textContent =
            "Could not connect to the MacroMate backend.";
    }
    finally {
        calculateButton.disabled = false;
        calculateButton.textContent = "Calculate Macros";
    }
});


coachButton.addEventListener("click", async () => {

    if (!latestResults || !latestUser) {
        return;
    }

    coachButton.disabled = true;
    coachButton.textContent = "Generating Advice...";

    try {

        const response = await fetch("http://127.0.0.1:8000/ai-coach", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                age: latestUser.age,
                weight_kg: latestUser.weight_kg,
                goal: latestUser.goal,
                calories: latestResults.calories,
                protein_grams: latestResults.protein_grams,
                carbs_grams: latestResults.carbs_grams,
                fat_grams: latestResults.fat_grams
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error("Unable to generate advice.");
        }

        coachTitle.textContent = data.title;
        coachSummary.textContent = data.summary;
        coachDisclaimer.textContent = data.disclaimer;

        coachAdvice.innerHTML = "";

        data.advice.forEach(item => {
            const li = document.createElement("li");
            li.textContent = item;
            coachAdvice.appendChild(li);
        });

        coachSection.classList.remove("hidden");

        coachSection.scrollIntoView({
            behavior: "smooth"
        });

    }
    catch (error) {

        console.error(error);

        errorMessage.textContent =
            "Unable to generate nutrition advice.";

    }
    finally {

        coachButton.disabled = false;
        coachButton.textContent = "✨ Get Nutrition Advice";

    }

});