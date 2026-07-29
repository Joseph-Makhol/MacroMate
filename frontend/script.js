const form = document.getElementById("macro-form");
const resultsSection = document.getElementById("results");
const errorMessage = document.getElementById("error-message");

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    errorMessage.textContent = "";
    resultsSection.classList.add("hidden");

    const userData = {
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
            body: JSON.stringify(userData)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Unable to calculate your macros.");
        }

        document.getElementById("calories").textContent = data.calories;
        document.getElementById("protein").textContent = data.protein_grams;
        document.getElementById("carbs").textContent = data.carbs_grams;
        document.getElementById("fat").textContent = data.fat_grams;

        resultsSection.classList.remove("hidden");
    } catch (error) {
        errorMessage.textContent =
            "Could not connect to the MacroMate backend. Make sure the server is running.";
        console.error(error);
    }
});