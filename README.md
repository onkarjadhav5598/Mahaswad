# 🍛 Mahaswad — Maharashtrian Recipe Generator

> **Hacktoberfest 2026** · Powered by [Ollama](https://ollama.com) + Gemma 2B · Built with FastAPI + Streamlit

Turn your available ingredients into **authentic Maharashtrian recipes** — in English or Marathi — using a fully local, privacy-friendly AI running on your own machine.

---

## ✨ Features

- 🤖 **100% Local AI** — Uses `gemma2:2b` via Ollama. No API keys, no cloud, no cost.
- 🗺️ **4 Regional Styles** — Puneri, Kolhapuri, Malvani, and Vidarbha cuisine
- 🍽️ **4 Dish Categories** — Breakfast, Main Course, Snack, Dessert
- 🇮🇳 **Bilingual** — Recipes in English or Marathi (Devanagari script)
- ⚡ **Real-time generation** — FastAPI backend + interactive Streamlit UI
- 🔍 **Smart ingredient matching** — AI identifies the closest traditional dish

---

## 🏗️ Architecture

```
┌─────────────────────┐        HTTP POST        ┌──────────────────────┐
│   Streamlit UI      │ ──────────────────────► │   FastAPI Backend    │
│   (app.py)          │   /generate-recipe       │   (main.py)          │
│   localhost:8501    │ ◄──────────────────────  │   localhost:8000     │
└─────────────────────┘     RecipeResponse       └──────────┬───────────┘
                                                            │ ollama.chat()
                                                            ▼
                                                 ┌──────────────────────┐
                                                 │   Ollama (local)     │
                                                 │   gemma2:2b          │
                                                 │   localhost:11434    │
                                                 └──────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

| Tool | Purpose | Install |
|---|---|---|
| Python 3.10+ | Runtime | [python.org](https://python.org) |
| Ollama | Local LLM server | [ollama.com](https://ollama.com) |
| Git | Version control | [git-scm.com](https://git-scm.com) |

### 1. Clone the repository

```bash
git clone https://github.com/onkarjadhav5598/Mahaswad.git
cd Mahaswad
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up Ollama

```bash
# Pull the Gemma 2B model (one-time, ~1.6 GB)
ollama pull gemma2:2b
```

> If `ollama serve` is already running in the background (port 11434), skip that step.

### 4. Run the project

**Linux / macOS / Git Bash:**
```bash
bash run.sh
```

**Windows (Command Prompt):**
```bat
run.bat
```

**Manual (two terminals):**

```bash
# Terminal 1 — FastAPI backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — Streamlit frontend
streamlit run app.py --server.port 8501
```

### 5. Open the app

| Service | URL |
|---|---|
| 🎨 **Streamlit UI** | http://localhost:8501 |
| 📖 **API Docs (Swagger)** | http://localhost:8000/docs |
| ❤️ **Health Check** | http://localhost:8000/health |

---

## 📡 API Reference

### `POST /generate-recipe`

Generate a Maharashtrian recipe from a list of ingredients.

**Request Body:**
```json
{
  "ingredients": ["poha", "peanuts", "onions", "turmeric"],
  "category": "Breakfast",
  "language": "English",
  "regional_style": "Puneri"
}
```

| Field | Type | Required | Options |
|---|---|---|---|
| `ingredients` | `list[str]` | ✅ | Any ingredients |
| `category` | `str` | ❌ | `Breakfast`, `Main Course`, `Snack`, `Dessert` |
| `language` | `str` | ❌ | `English`, `Marathi` |
| `regional_style` | `str` | ❌ | `Puneri`, `Kolhapuri`, `Malvani`, `Vidarbha` |

**Response:**
```json
{
  "recipe_name": "Kanda Poha",
  "regional_style": "Puneri",
  "category": "Breakfast",
  "language": "English",
  "ingredients_used": ["poha", "peanuts", "onions", "turmeric"],
  "additional_ingredients": ["mustard seeds", "curry leaves", "green chilli", "salt", "oil"],
  "instructions": ["Step 1: ...", "Step 2: ...", "..."],
  "chef_note": "Kanda Poha is a beloved Pune breakfast...",
  "raw_text": "..."
}
```

### `GET /health`

Check backend and Ollama connectivity.

---

## 🗺️ Regional Styles

| Style | Character | Famous Dishes |
|---|---|---|
| 🏰 **Puneri** | Mild, subtly sweet, kokum & jaggery | Puneri Misal, Mastani, Bhakarwadi |
| 🌶️ **Kolhapuri** | Bold, fiery, intensely spiced | Tambda Rassa, Pandhra Rassa, Spicy Misal |
| 🐟 **Malvani** | Coastal, coconut-rich, tangy | Fish Curry, Sol Kadhi, Malvani Chicken |
| 🥜 **Vidarbha** | Rustic, hearty, saoji masala | Saoji Chicken, Zunka Bhakar, Varhadi dishes |

---

## 📦 Tech Stack

| Layer | Technology | Version |
|---|---|---|
| **Frontend** | Streamlit | 1.38.0 |
| **Backend** | FastAPI | 0.115.0 |
| **Server** | Uvicorn | 0.30.6 |
| **LLM Runtime** | Ollama | — |
| **Model** | Gemma 2B | gemma2:2b |
| **HTTP Client** | Requests | 2.32.3 |
| **Data Validation** | Pydantic | 2.9.2 |

---

## 📁 Project Structure

```
Mahaswad/
├── app.py              # Streamlit frontend UI
├── main.py             # FastAPI backend & Ollama integration
├── requirements.txt    # Python dependencies
├── run.sh              # Launch script (Linux/macOS/Bash)
└── run.bat             # Launch script (Windows)
```

---

## 🤝 Contributing

Contributions are welcome! This project was built for **Hacktoberfest 2026**.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">
  Made with ❤️ for Hacktoberfest 2026<br>
  <em>Authentic Maharashtrian recipes from Pune, Kolhapur, Konkan & Vidarbha</em>
</div>
