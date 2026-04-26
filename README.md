# 🎯 TalentScout AI

> AI-Powered Talent Scouting & Engagement Agent — Catalyst Hackathon · Deccan AI

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)

---

## 🚀 What It Does

TalentScout AI takes a **Job Description as input** and automatically:

1. **Parses the JD** — extracts skills, experience range, location, budget using Claude AI
2. **Discovers matching candidates** — scores 20+ profiles across 5 dimensions with full explainability
3. **Engages candidates conversationally** — simulates realistic AI outreach and detects interest signals
4. **Outputs a ranked shortlist** — scored on both **Match Score** and **Interest Score**

---

## 🖥️ Live Demo

🔗 **[Try it live →](https://your-app.streamlit.app)**  
📹 **[Demo Video →](https://your-video-link)**

---

## 🏗️ Project Structure

```
talent-scout/
├── app.py                    # Main Streamlit application
├── agent/
│   ├── jd_parser.py          # Claude-powered JD parsing
│   ├── candidate_matcher.py  # Rule-based + AI matching & scoring
│   └── outreach_agent.py     # Conversational outreach simulation
├── data/
│   └── candidates.py         # 20 mock candidate profiles
├── .streamlit/
│   ├── config.toml           # Streamlit theme config
│   └── secrets.toml          # API keys (not committed)
├── requirements.txt
├── ARCHITECTURE.md           # Scoring logic & architecture diagram
└── README.md
```

---

## ⚡ Local Setup

### Prerequisites
- Python 3.9+
- Anthropic API key ([get one here](https://console.anthropic.com))

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/talent-scout-ai.git
cd talent-scout-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your API key
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
# OR add it in the app's sidebar at runtime

# 4. Run the app
streamlit run app.py
```

App opens at: `http://localhost:8501`

---

## ☁️ Deploy to Streamlit Cloud

1. Push this repo to GitHub (make sure `.streamlit/secrets.toml` is in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo → set `app.py` as main file
4. In **Secrets**, add:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-your-key-here"
   ```
5. Click **Deploy** ✅

---

## 🧠 Scoring Logic

### Match Score (0–100)
| Dimension | Max | How |
|-----------|-----|-----|
| Skills Match | 40 | Required (30) + Preferred (10) skill overlap |
| Experience | 25 | Perfect range = 25; penalized per year gap |
| Location | 10 | Exact match = 10; mismatch = 4 |
| Availability | 10 | ≤30d notice = 10; >60d = 4 |
| Budget Fit | 15 | Within budget = 15; over budget = 2 |

### Interest Score (0–100)
Derived from simulated conversation signals:
- Open-to-work status, profile recency
- Enthusiasm level, explicit interest, questions asked, availability confirmed

### Combined Score
```
Combined = 0.6 × Match Score + 0.4 × Interest Score
```

---

## 📋 Sample Input

```
Role: Senior Python Backend Engineer
Experience: 4-7 years | Location: Hyderabad | Budget: ₹15–25 LPA

Required: Python, FastAPI, PostgreSQL, Docker, REST APIs
Preferred: AWS, Redis, Microservices
```

## 📤 Sample Output

| Rank | Candidate | Match | Interest | Combined |
|------|-----------|-------|----------|----------|
| #1 | Arjun Mehta | 88% | 82% | 86% |
| #2 | Kavitha Nambiar | 80% | 91% | 84% |
| #3 | Siddharth Joshi | 71% | 78% | 74% |

---

## 🛠️ Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | Streamlit |
| AI Engine | Anthropic Claude (claude-sonnet-4) |
| Language | Python 3.9+ |
| Deployment | Streamlit Cloud |
| Data | Mock profiles (20 candidates) |

---

## 📐 Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for full pipeline diagram and scoring breakdown.

---

## 👩‍💻 Author

Built for **Catalyst Hackathon · Deccan AI**  
Submitted by: **Thota Varshini**

---

## 📄 License

MIT
