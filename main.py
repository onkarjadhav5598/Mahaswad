"""
Maharashtrian Recipe Generator — FastAPI Backend
=================================================
Serves a /generate-recipe POST endpoint that calls a local Ollama instance
running gemma2:2b to produce authentic Maharashtrian recipes.
"""

import re
import json
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    import ollama
except ImportError:
    ollama = None  # handled at request time

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("recipe-api")

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Maharashtrian Recipe Generator",
    description="Generate authentic Maharashtrian recipes from your ingredients using a local LLM.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------
VALID_CATEGORIES = {"Breakfast", "Main Course", "Snack", "Dessert"}
VALID_LANGUAGES = {"English", "Marathi"}

REGIONAL_STYLES = {
    "Puneri": "Known for mild yet flavourful preparations with a subtle sweetness; uses kokum, jaggery, and minimal oil. Famous for Puneri Misal, Mastani, and Bhakarwadi.",
    "Kolhapuri": "Bold, fiery, and intensely spiced. Relies on Kolhapuri masala, dry coconut, and red chillies. Signature dishes include Kolhapuri Tambda-Pandhra Rassa and spicy Misal.",
    "Malvani": "Coastal cuisine heavy on coconut, kokum, and fresh seafood spices. Uses freshly ground masalas with a balance of heat and tanginess. Known for Malvani fish curry and Sol Kadhi.",
    "Vidarbha": "Hearty, rustic cuisine featuring saoji masala, peanuts, sesame, and dry coconut. Known for Saoji chicken/mutton, Varhadi cuisine, and Zunka Bhakar.",
}


class RecipeRequest(BaseModel):
    ingredients: list[str] = Field(
        ...,
        min_length=1,
        description="List of available ingredients (e.g. ['poha', 'peanuts', 'onions']).",
    )
    category: str = Field(
        default="Main Course",
        description="Dish category: Breakfast, Main Course, Snack, or Dessert.",
    )
    language: str = Field(
        default="English",
        description="Output language: English or Marathi (Devanagari script).",
    )
    regional_style: Optional[str] = Field(
        default=None,
        description="Optional regional style: Puneri, Kolhapuri, Malvani, or Vidarbha.",
    )


class RecipeResponse(BaseModel):
    recipe_name: str
    regional_style: str
    category: str
    language: str
    ingredients_used: list[str]
    additional_ingredients: list[str]
    instructions: list[str]
    chef_note: str
    raw_text: str  # full LLM output for debugging / display


# ---------------------------------------------------------------------------
# Prompt engineering
# ---------------------------------------------------------------------------

def _build_prompt(req: RecipeRequest) -> str:
    """Construct a detailed prompt tailored for Maharashtrian cuisine."""

    style = req.regional_style
    if style and style in REGIONAL_STYLES:
        style_hint = f"\nRegional style to follow: **{style}** — {REGIONAL_STYLES[style]}"
    else:
        style_hint = (
            "\nChoose the most appropriate regional Maharashtrian style (Puneri, Kolhapuri, Malvani, or Vidarbha) "
            "based on the ingredients provided."
        )

    lang_instruction = ""
    if req.language == "Marathi":
        lang_instruction = (
            "\n\n**IMPORTANT — Write the ENTIRE recipe output in Marathi using Devanagari script (मराठी).**"
            " Do NOT use English anywhere in the recipe body. Only the JSON keys may remain in English."
        )

    prompt = f"""You are an expert Maharashtrian home chef and culinary historian.

Given the following ingredients, create ONE authentic Maharashtrian {req.category.lower()} recipe.
{style_hint}
{lang_instruction}

### Available Ingredients
{', '.join(req.ingredients)}

### Output Format (respond ONLY with this JSON — no extra text)
{{
  "recipe_name": "<Name of the dish>",
  "regional_style": "<Puneri | Kolhapuri | Malvani | Vidarbha>",
  "ingredients_used": ["<ingredient from the user list>", ...],
  "additional_ingredients": ["<any extra pantry staple needed>", ...],
  "instructions": [
    "Step 1: ...",
    "Step 2: ...",
    "..."
  ],
  "chef_note": "<A short cultural or regional note about this dish — 1-2 sentences>"
}}

Rules:
- Use ONLY real, traditional Maharashtrian recipes. Do NOT invent fusion dishes.
- If the ingredients strongly suggest a well-known dish (e.g. poha + peanuts + onions → Kanda Poha), use that dish.
- Keep instructions concise (6-12 steps).
- The chef_note should mention the region and any cultural context.
- Respond with valid JSON only. No markdown fences, no explanation outside the JSON.
"""
    return prompt.strip()


# ---------------------------------------------------------------------------
# Response cleaning
# ---------------------------------------------------------------------------

def _clean_llm_output(raw: str) -> str:
    """Strip <think> scratchpad tags, markdown fences, and other noise."""
    # Remove <think>...</think> blocks (greedy, multiline)
    cleaned = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
    # Remove markdown JSON fences
    cleaned = re.sub(r"```json\s*", "", cleaned)
    cleaned = re.sub(r"```\s*", "", cleaned)
    # Trim whitespace
    cleaned = cleaned.strip()
    return cleaned


def _parse_recipe_json(cleaned: str, raw: str, req: RecipeRequest) -> RecipeResponse:
    """Attempt to parse the LLM output as JSON and return a RecipeResponse."""
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to extract a JSON object with regex
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                raise ValueError("Could not parse JSON from LLM output.")
        else:
            raise ValueError("No JSON object found in LLM output.")

    return RecipeResponse(
        recipe_name=data.get("recipe_name", "Unnamed Dish"),
        regional_style=data.get("regional_style", req.regional_style or "Traditional"),
        category=req.category,
        language=req.language,
        ingredients_used=data.get("ingredients_used", req.ingredients),
        additional_ingredients=data.get("additional_ingredients", []),
        instructions=data.get("instructions", []),
        chef_note=data.get("chef_note", ""),
        raw_text=raw,
    )


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    """Basic health check — also verifies Ollama connectivity."""
    if ollama is None:
        return {"status": "error", "detail": "ollama Python package is not installed."}
    try:
        models = ollama.list()
        model_names = [m.model for m in models.models] if hasattr(models, "models") else []
        gemma_available = any("gemma2:2b" in n for n in model_names)
        return {
            "status": "ok",
            "ollama": "connected",
            "gemma2_2b": "available" if gemma_available else "not pulled — run `ollama pull gemma2:2b`",
            "models": model_names,
        }
    except Exception as exc:
        return {
            "status": "error",
            "ollama": "unreachable",
            "detail": str(exc),
            "hint": "Make sure Ollama is running (`ollama serve`).",
        }


# ---------------------------------------------------------------------------
# Main endpoint
# ---------------------------------------------------------------------------

@app.post("/generate-recipe", response_model=RecipeResponse)
async def generate_recipe(req: RecipeRequest):
    """Generate a Maharashtrian recipe from a list of ingredients."""

    # --- Validate inputs ---
    if req.category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid category '{req.category}'. Must be one of {VALID_CATEGORIES}.",
        )
    if req.language not in VALID_LANGUAGES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid language '{req.language}'. Must be one of {VALID_LANGUAGES}.",
        )
    if req.regional_style and req.regional_style not in REGIONAL_STYLES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid regional style '{req.regional_style}'. Must be one of {set(REGIONAL_STYLES.keys())}.",
        )

    # --- Verify Ollama availability ---
    if ollama is None:
        raise HTTPException(
            status_code=503,
            detail="The `ollama` Python package is not installed. Run `pip install ollama`.",
        )

    try:
        ollama.list()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail=(
                "Cannot connect to Ollama. Make sure Ollama is running locally. "
                "Start it with `ollama serve` and pull the model with `ollama pull gemma2:2b`."
            ),
        )

    # --- Build prompt and call LLM ---
    prompt = _build_prompt(req)
    logger.info("Prompt built (%d chars) for ingredients: %s", len(prompt), req.ingredients)

    try:
        response = ollama.chat(
            model="gemma2:2b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Maharashtrian cuisine expert. "
                        "Always respond with valid JSON only, no extra commentary."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            options={
                "num_predict": 1024,
                "temperature": 0.6,
            },
        )
    except Exception as exc:
        error_msg = str(exc).lower()
        if "not found" in error_msg or "pull" in error_msg:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Model `gemma2:2b` is not available. "
                    "Please pull it first: `ollama pull gemma2:2b`."
                ),
            )
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {exc}")

    raw_text = response["message"]["content"]
    logger.info("LLM responded with %d chars", len(raw_text))

    # --- Clean and parse ---
    cleaned = _clean_llm_output(raw_text)

    try:
        recipe = _parse_recipe_json(cleaned, raw_text, req)
    except ValueError as exc:
        logger.warning("JSON parse failed. Raw output:\n%s", raw_text)
        raise HTTPException(
            status_code=502,
            detail=f"The LLM returned an unparseable response. {exc}. Try again.",
        )

    return recipe


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
