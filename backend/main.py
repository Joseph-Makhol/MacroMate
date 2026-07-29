from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


app = FastAPI(
    title="MacroMate API",
    description="Calculates personalized calorie and macronutrient targets.",
    version="1.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MacroRequest(BaseModel):
    age: int = Field(ge=1, le=100)
    sex: str
    height_cm: float = Field(ge=40, le=250)
    weight_kg: float = Field(ge=2, le=300)
    activity_level: str
    goal: str


class CoachRequest(BaseModel):
    age: int = Field(ge=1, le=100)
    weight_kg: float = Field(ge=2, le=300)
    goal: str
    calories: int = Field(gt=0)
    protein_grams: int = Field(ge=0)
    carbs_grams: int = Field(ge=0)
    fat_grams: int = Field(ge=0)
    

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}


GOAL_ADJUSTMENTS = {
    "lose": -400,
    "maintain": 0,
    "gain": 300,
}


def calculate_bmr(
    weight_kg: float,
    height_cm: float,
    age: int,
    sex: str,
) -> float:
    """Estimate BMR using the Mifflin-St Jeor equation."""

    sex = sex.lower()

    if sex == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5

    if sex == "female":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    raise HTTPException(
        status_code=400,
        detail="Sex must be either 'male' or 'female'.",
    )


def generate_coach_advice(data: CoachRequest) -> list[str]:
    """
    Generate personalized nutrition guidance locally.

    This free local provider can later be replaced with an external
    AI provider without changing the frontend API request.
    """

    goal = data.goal.lower()

    if goal not in GOAL_ADJUSTMENTS:
        raise HTTPException(
            status_code=400,
            detail="Goal must be 'lose', 'maintain', or 'gain'.",
        )

    advice = []

    if goal == "lose":
        advice.append(
            "Build meals around lean protein and high-fiber foods to help "
            "control hunger while staying near your calorie target."
        )
        advice.append(
            "Track your weekly weight trend instead of reacting to normal "
            "day-to-day changes."
        )

    elif goal == "gain":
        advice.append(
            "Spread your calorie intake across several meals and include "
            "energy-dense foods when reaching your target feels difficult."
        )
        advice.append(
            "Combine your nutrition plan with progressive resistance training "
            "to support muscle growth."
        )

    else:
        advice.append(
            "Keep your meal portions and activity level reasonably consistent "
            "to remain close to your maintenance target."
        )
        advice.append(
            "Use changes in energy, performance, and weekly weight trends to "
            "decide whether small adjustments are needed."
        )

    protein_per_meal = max(round(data.protein_grams / 4), 1)

    advice.append(
        f"Aim for roughly {protein_per_meal} grams of protein across four "
        "meals, using foods such as chicken, fish, eggs, beans, tofu, "
        "cottage cheese, or Greek yogurt."
    )

    if data.carbs_grams >= 250:
        advice.append(
            "Use foods such as rice, oats, potatoes, fruit, and whole-grain "
            "bread to reach your carbohydrate target and support training."
        )
    else:
        advice.append(
            "Choose mostly fiber-rich carbohydrate sources such as fruit, "
            "vegetables, oats, beans, and whole grains."
        )

    advice.append(
        "Include healthy fat sources such as olive oil, nuts, seeds, avocado, "
        "and oily fish while staying near your daily fat target."
    )

    advice.append(
        "Treat these numbers as starting estimates and adjust them gradually "
        "based on your results over several weeks."
    )

    return advice


@app.get("/")
def home():
    return {
        "message": "MacroMate API is running",
        "status": "success",
    }


@app.post("/calculate")
def calculate_macros(data: MacroRequest):
    activity = data.activity_level.lower()
    goal = data.goal.lower()

    if activity not in ACTIVITY_MULTIPLIERS:
        raise HTTPException(
            status_code=400,
            detail="Invalid activity level.",
        )

    if goal not in GOAL_ADJUSTMENTS:
        raise HTTPException(
            status_code=400,
            detail="Goal must be 'lose', 'maintain', or 'gain'.",
        )

    bmr = calculate_bmr(
        weight_kg=data.weight_kg,
        height_cm=data.height_cm,
        age=data.age,
        sex=data.sex,
    )

    maintenance_calories = bmr * ACTIVITY_MULTIPLIERS[activity]
    target_calories = maintenance_calories + GOAL_ADJUSTMENTS[goal]

    protein_grams = data.weight_kg * 2
    fat_grams = data.weight_kg * 0.8

    protein_calories = protein_grams * 4
    fat_calories = fat_grams * 9
    remaining_calories = target_calories - protein_calories - fat_calories
    carbs_grams = max(remaining_calories / 4, 0)

    return {
        "status": "success",
        "calories": round(target_calories),
        "protein_grams": round(protein_grams),
        "carbs_grams": round(carbs_grams),
        "fat_grams": round(fat_grams),
        "bmr": round(bmr),
        "maintenance_calories": round(maintenance_calories),
        "goal": goal,
    }


@app.post("/ai-coach")
def get_ai_coach_advice(data: CoachRequest):
    advice = generate_coach_advice(data)

    return {
        "status": "success",
        "provider": "local",
        "title": "MacroMate Nutrition Coach",
        "summary": (
            f"Here is a practical plan for your {data.calories}-calorie "
            f"{data.goal.lower()} goal."
        ),
        "advice": advice,
        "disclaimer": (
            "This guidance is educational and is not a substitute for advice "
            "from a qualified medical or nutrition professional."
        ),
    }