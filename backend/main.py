import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI(title="Pathfinder AI")

# -------------------------
# DATA MODELS
# -------------------------

class UserProfile(BaseModel):
    role: str
    interests: str
    goals: str
    risk_tolerance: str


class PathSelection(BaseModel):
    path_title: str


class DecisionChoice(BaseModel):
    choice: str
    risk_change: int
    income_change: int
    impact_change: int


# -------------------------
# GAME STATE
# -------------------------

game_state = {
    "risk": 0,
    "income": 0,
    "impact": 0,
    "life_satisfaction": 50
}


# -------------------------
# ROOT
# -------------------------

@app.get("/")
def home():
    return {"message": "Pathfinder AI agent is running 🚀"}


# -------------------------
# GENERATE LIFE PATHS
# -------------------------

@app.post("/generate-paths")
def generate_paths(profile: UserProfile):

    prompt = f"""
You are Pathfinder AI, a life simulation agent.

User Profile:
Role: {profile.role}
Interests: {profile.interests}
Goals: {profile.goals}
Risk tolerance: {profile.risk_tolerance}

Generate exactly 4 realistic future career paths.

Each path must include:
- title
- description (max 40 words)
- risk_level
- potential_income
- societal_impact
- first_decision_event

Return JSON format only:

{{
 "paths":[
  {{
   "title":"",
   "description":"",
   "risk_level":"",
   "potential_income":"",
   "societal_impact":"",
   "first_decision_event":""
  }}
 ]
}}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "max_output_tokens": 500,
            "temperature": 0.7
        }
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    try:
        return json.loads(text)
    except:
        return {"raw_output": text}


# -------------------------
# SELECT PATH
# -------------------------

@app.post("/select-path")
def select_path(selection: PathSelection):

    prompt = f"""
You are simulating the life path: {selection.path_title}

Generate the first major life decision event.

Return JSON:

{{
 "event":"",
 "options":[
   {{
    "choice":"",
    "risk_change":10,
    "income_change":20,
    "impact_change":15
   }},
   {{
    "choice":"",
    "risk_change":-5,
    "income_change":10,
    "impact_change":5
   }}
 ]
}}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "max_output_tokens": 300,
            "temperature": 0.7
        }
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    try:
        return json.loads(text)
    except:
        return {"raw_output": text}


# -------------------------
# APPLY DECISION
# -------------------------

@app.post("/apply-decision")
def apply_decision(choice: DecisionChoice):

    game_state["risk"] += choice.risk_change
    game_state["income"] += choice.income_change
    game_state["impact"] += choice.impact_change

    game_state["life_satisfaction"] = max(
        0,
        min(
            100,
            50
            + game_state["impact"] * 0.2
            + game_state["income"] * 0.2
            - game_state["risk"] * 0.1,
        ),
    )

    return {
        "updated_state": game_state
    }


# -------------------------
# VIEW CURRENT LIFE STATE
# -------------------------

@app.get("/life-state")
def get_life_state():
    return game_state


# -------------------------
# GENERATE VISUAL SCENE
# -------------------------

@app.post("/generate-path-visual")
def generate_path_visual(selection: PathSelection):

    prompt = f"""
Create a cinematic illustration representing this life path:

{selection.path_title}

Style: futuristic, inspirational, professional.
Show the person working in their environment and making global impact.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=prompt
    )

    return {
        "visual_prompt": prompt,
        "message": "Visual scene prompt generated"
    }


# -------------------------
# GENERATE FUTURE TIMELINE
# -------------------------

@app.post("/generate-future-timeline")
def generate_future_timeline(selection: PathSelection):

    prompt = f"""
Simulate the future life trajectory for this career path:

{selection.path_title}

Return JSON format:

{{
 "timeline":[
   {{"year":"Year 1","event":""}},
   {{"year":"Year 3","event":""}},
   {{"year":"Year 7","event":""}},
   {{"year":"Year 15","event":""}}
 ]
}}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "max_output_tokens": 300,
            "temperature": 0.7
        }
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    try:
        return json.loads(text)
    except:
        return {"raw_output": text}
    

    # -------------------------
# FULL LIFE SIMULATION
# -------------------------

@app.post("/play-life")
def play_life(profile: UserProfile):

    # Step 1: generate life paths
    paths = generate_paths(profile)

    first_path = paths["paths"][0]["title"]

    # Step 2: select first path automatically
    selection = PathSelection(path_title=first_path)

    # Step 3: generate timeline
    timeline = generate_future_timeline(selection)

    # Step 4: generate visual scene
    visual = generate_path_visual(selection)

    # Step 5: simulate decision automatically
    decision = DecisionChoice(
        choice="Take the opportunity",
        risk_change=15,
        income_change=25,
        impact_change=20
    )

    result = apply_decision(decision)

    return {
        "chosen_path": first_path,
        "timeline": timeline,
        "visual_scene": visual,
        "life_state": result
    }