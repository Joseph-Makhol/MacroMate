from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="MacroMate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MacroRequest(BaseModel):
    age: int = Field(gt=0, le=120)
    sex: str
    height_cm: float = Field(gt=0)
    weight_kg: float = Field(gt=0)
    activity_level: str
    goal: str


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
    sex: str
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