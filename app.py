"""
Maharashtrian Recipe Generator — Streamlit Frontend
=====================================================
A rich, interactive UI that lets users input ingredients, pick a dish category,
language, and regional style — then displays the generated recipe as a beautiful
Markdown card.
"""

import streamlit as st
import requests
import json

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="🍛 Maharashtrian Recipe Generator",
    page_icon="🍛",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS for a premium look
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

    /* ── Global font ── */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* ── Main app background ── */
    .stApp {
        background: #0E0C0A;
    }

    /* ── Hero header ── */
    .hero-header {
        background: linear-gradient(135deg, #78350F 0%, #92400E 40%, #B45309 100%);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(180, 83, 9, 0.35);
        border: 1px solid rgba(245, 158, 11, 0.2);
    }
    .hero-header h1 {
        color: #FEF3C7;
        font-size: 2.4rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .hero-header p {
        color: #FDE68A;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 300;
    }

    /* ── Recipe card ── */
    .recipe-card {
        background: linear-gradient(145deg, #1C1410 0%, #1A1714 100%);
        border: 1px solid rgba(245, 158, 11, 0.25);
        border-radius: 16px;
        padding: 2rem;
        margin-top: 1.5rem;
        box-shadow: 0 4px 24px rgba(180, 83, 9, 0.15);
    }
    .recipe-card h2 {
        color: #F59E0B !important;
        font-weight: 700;
        border-bottom: 2px solid #D97706;
        padding-bottom: 0.5rem;
    }
    .recipe-card h3 {
        color: #FBBF24 !important;
        font-weight: 600;
    }

    /* ── Chef note ── */
    .chef-note {
        background: linear-gradient(135deg, #1C1510, #221A10);
        border-left: 4px solid #F59E0B;
        padding: 1rem 1.25rem;
        border-radius: 0 12px 12px 0;
        margin-top: 1rem;
        font-style: italic;
        color: #FDE68A;
    }

    /* ── Style badge ── */
    .style-badge {
        display: inline-block;
        background: linear-gradient(135deg, #D97706, #B45309);
        color: #FEF3C7;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 1rem;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #151210 0%, #1A1510 100%);
        border-right: 1px solid rgba(245, 158, 11, 0.15);
    }
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] .stMarkdown h2 {
        color: #F59E0B !important;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] .stCaption p {
        color: #D4B896 !important;
    }

    /* ── Button overrides ── */
    .stButton > button {
        background: linear-gradient(135deg, #D97706 0%, #B45309 100%) !important;
        color: #FEF3C7 !important;
        font-weight: 600;
        border: none !important;
        border-radius: 12px;
        padding: 0.65rem 2rem;
        font-size: 1.05rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(217, 119, 6, 0.35);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(245, 158, 11, 0.5) !important;
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%) !important;
    }
    .stButton > button:disabled {
        background: #2A2520 !important;
        color: #6B5E50 !important;
        box-shadow: none !important;
    }

    /* ── Ingredient chips ── */
    .ingredient-chip {
        display: inline-block;
        background: rgba(245, 158, 11, 0.12);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.9rem;
        font-weight: 500;
    }

    /* ── Error box ── */
    .error-box {
        background: #1A1210;
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        color: #FCA5A5;
    }
    .error-box h3 {
        color: #F87171 !important;
    }
    .error-box a {
        color: #F59E0B;
    }
    .error-box code {
        background: #2A1F18;
        color: #FBBF24;
        padding: 0.15rem 0.4rem;
        border-radius: 4px;
    }

    /* ── Footer ── */
    .footer {
        text-align: center;
        color: #6B5E50;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(245, 158, 11, 0.1);
    }

    /* ── Streamlit element overrides for dark harmony ── */
    .stTextArea textarea {
        background: #1A1510 !important;
        border-color: rgba(245, 158, 11, 0.2) !important;
        color: #E8D5B5 !important;
    }
    .stTextArea textarea:focus {
        border-color: #F59E0B !important;
        box-shadow: 0 0 0 1px #F59E0B !important;
    }
    .stSelectbox > div > div {
        background: #1A1510 !important;
        border-color: rgba(245, 158, 11, 0.2) !important;
        color: #E8D5B5 !important;
    }

    /* ── Horizontal rules ── */
    hr {
        border-color: rgba(245, 158, 11, 0.15) !important;
    }

    /* ── Info/warning boxes ── */
    .stAlert {
        background: rgba(245, 158, 11, 0.08) !important;
        border-color: rgba(245, 158, 11, 0.2) !important;
        color: #FDE68A !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
API_URL = "http://localhost:8000/generate-recipe"
HEALTH_URL = "http://localhost:8000/health"

CATEGORY_EMOJIS = {
    "Breakfast": "🌅",
    "Main Course": "🍛",
    "Snack": "🍿",
    "Dessert": "🍮",
}

STYLE_DESCRIPTIONS = {
    "Auto (let AI decide)": "The AI picks the best regional style based on your ingredients.",
    "Puneri": "🏰 Mild, subtly sweet — Pune's refined flavours.",
    "Kolhapuri": "🌶️ Bold, fiery — Kolhapur's legendary spice.",
    "Malvani": "🐟 Coastal, coconut-rich — Konkan's treasure.",
    "Vidarbha": "🥜 Rustic, hearty — Nagpur & beyond.",
}

# ---------------------------------------------------------------------------
# Hero header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-header">
        <h1>🍛 Maharashtrian Recipe Generator</h1>
        <p>Turn your ingredients into authentic recipes from the heart of Maharashtra</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar — inputs
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🧂 Your Ingredients")

    ingredients_raw = st.text_area(
        "Enter ingredients (comma-separated)",
        placeholder="e.g. poha, peanuts, onions, turmeric, mustard seeds",
        height=120,
        help="Type the ingredients you have at hand. The AI will find the best Maharashtrian recipe for you!",
    )

    st.markdown("---")
    st.markdown("## ⚙️ Preferences")

    category = st.selectbox(
        "Dish Category",
        options=list(CATEGORY_EMOJIS.keys()),
        format_func=lambda x: f"{CATEGORY_EMOJIS[x]}  {x}",
    )

    language = st.selectbox(
        "Recipe Language",
        options=["English", "Marathi"],
        format_func=lambda x: f"🇬🇧 {x}" if x == "English" else f"🇮🇳 {x} (मराठी)",
    )

    style_choice = st.selectbox(
        "Regional Style",
        options=list(STYLE_DESCRIPTIONS.keys()),
    )
    st.caption(STYLE_DESCRIPTIONS[style_choice])

    st.markdown("---")

    # Health check
    with st.expander("🔌 Backend Status", expanded=False):
        if st.button("Check Connection", use_container_width=True):
            try:
                resp = requests.get(HEALTH_URL, timeout=15)
                data = resp.json()
                if data.get("status") == "ok":
                    st.success("✅ Backend is running!")
                    st.json(data)
                else:
                    st.warning("⚠️ Backend has issues:")
                    st.json(data)
            except requests.ConnectionError:
                st.error("❌ Cannot reach backend at localhost:8000")
            except Exception as e:
                st.error(f"❌ {e}")

# ---------------------------------------------------------------------------
# Main area — generate button & results
# ---------------------------------------------------------------------------

# Parse ingredients
ingredients = [i.strip() for i in ingredients_raw.split(",") if i.strip()] if ingredients_raw else []

# Show ingredient chips
if ingredients:
    chips_html = "".join(f'<span class="ingredient-chip">{ing}</span>' for ing in ingredients)
    st.markdown(f"**Your ingredients:** {chips_html}", unsafe_allow_html=True)

# Generate button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_clicked = st.button(
        "🔥 Generate Recipe",
        use_container_width=True,
        disabled=len(ingredients) == 0,
    )

if not ingredients and not generate_clicked:
    st.info("👈 Enter your ingredients in the sidebar to get started!")

# ---------------------------------------------------------------------------
# API call & display
# ---------------------------------------------------------------------------
if generate_clicked and ingredients:
    regional_style = None if style_choice == "Auto (let AI decide)" else style_choice

    payload = {
        "ingredients": ingredients,
        "category": category,
        "language": language,
    }
    if regional_style:
        payload["regional_style"] = regional_style

    with st.spinner("🧑‍🍳 Our Maharashtrian chef is cooking up a recipe for you…"):
        try:
            resp = requests.post(API_URL, json=payload, timeout=120)

            if resp.status_code == 200:
                recipe = resp.json()

                # --- Render recipe card ---
                st.markdown('<div class="recipe-card">', unsafe_allow_html=True)

                # Title and badge
                st.markdown(
                    f'<span class="style-badge">{recipe.get("regional_style", "Traditional")} Style</span>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"## {recipe.get('recipe_name', 'Your Recipe')}")
                st.markdown(
                    f"**{CATEGORY_EMOJIS.get(category, '')} {category}** · "
                    f"**{'🇮🇳 मराठी' if language == 'Marathi' else '🇬🇧 English'}**"
                )

                st.markdown("---")

                # Ingredients columns
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("### 🥘 Ingredients Used")
                    for ing in recipe.get("ingredients_used", []):
                        st.markdown(f"- ✅ {ing}")
                with col_b:
                    additional = recipe.get("additional_ingredients", [])
                    if additional:
                        st.markdown("### 🛒 You'll Also Need")
                        for ing in additional:
                            st.markdown(f"- 🔸 {ing}")

                st.markdown("---")

                # Instructions
                st.markdown("### 📝 Instructions")
                for i, step in enumerate(recipe.get("instructions", []), 1):
                    # Remove leading "Step N:" if the LLM already included it
                    step_text = step
                    if step.lower().startswith(f"step {i}"):
                        step_text = step.split(":", 1)[-1].strip() if ":" in step else step
                    st.markdown(f"**Step {i}.** {step_text}")

                st.markdown("---")

                # Chef Note
                chef_note = recipe.get("chef_note", "")
                if chef_note:
                    st.markdown(
                        f'<div class="chef-note">👨‍🍳 <strong>Chef\'s Note:</strong> {chef_note}</div>',
                        unsafe_allow_html=True,
                    )

                st.markdown("</div>", unsafe_allow_html=True)

                # Expandable raw JSON
                with st.expander("🔍 View raw API response"):
                    st.json(recipe)

            elif resp.status_code == 503:
                detail = resp.json().get("detail", "Service unavailable")
                st.markdown(
                    f"""
                    <div class="error-box">
                        <h3>⚡ Ollama Not Available</h3>
                        <p>{detail}</p>
                        <p style="font-size:0.9rem; color:#757575; margin-top:1rem;">
                            1. Install Ollama from <a href="https://ollama.com" target="_blank">ollama.com</a><br>
                            2. Run <code>ollama serve</code><br>
                            3. Pull the model: <code>ollama pull gemma2:2b</code>
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            elif resp.status_code == 502:
                detail = resp.json().get("detail", "Bad gateway")
                st.warning(f"🤖 The AI returned an unparseable response. Please try again.\n\n> {detail}")
            else:
                st.error(f"❌ API error {resp.status_code}: {resp.text}")

        except requests.ConnectionError:
            st.markdown(
                """
                <div class="error-box">
                    <h3>🔌 Backend Not Running</h3>
                    <p>Cannot connect to the FastAPI server at <code>localhost:8000</code>.</p>
                    <p style="font-size:0.9rem; color:#757575; margin-top:1rem;">
                        Start the backend with:<br>
                        <code>python main.py</code><br>
                        or<br>
                        <code>uvicorn main:app --reload --port 8000</code>
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        except requests.Timeout:
            st.warning(
                "⏱️ The request timed out. The LLM may be processing a complex recipe. "
                "Try again with fewer ingredients or a simpler category."
            )
        except Exception as exc:
            st.error(f"❌ Unexpected error: {exc}")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="footer">
        Made with ❤️ for Hacktoberfest 2026 · Powered by Ollama + Gemma 2B<br>
        <em>Authentic Maharashtrian recipes from Pune, Kolhapur, Konkan & Vidarbha</em>
    </div>
    """,
    unsafe_allow_html=True,
)
