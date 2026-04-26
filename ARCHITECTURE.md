# TalentScout AI — Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      STREAMLIT FRONTEND                         │
│   JD Input  →  Parsed Preview  →  Candidate Cards  →  Export   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
          ┌────────────────▼────────────────┐
          │         AGENT PIPELINE          │
          │                                 │
          │  1. JD Parser (Groq API)      │
          │     • Extracts skills, exp,     │
          │       location, budget, domain  │
          │                                 │
          │  2. Candidate Matcher           │
          │     • Rule-based scoring        │
          │     • 5-dimension breakdown     │
          │     • Top-N selection           │
          │                                 │
          │  3. Outreach Agent (Groq API) │
          │     • Simulates conversation    │
          │     • Detects interest signals  │
          │     • Computes Interest Score   │
          │                                 │
          │  4. Ranked Shortlist Builder    │
          │     • Combined Score formula    │
          │     • CSV export                │
          └────────────────┬────────────────┘
                           │
          ┌────────────────▼────────────────┐
          │      MOCK CANDIDATE DATABASE    │
          │      20 profiles across roles   │
          └─────────────────────────────────┘
```

## Scoring Logic

### Match Score (0–100)
| Dimension       | Weight | Logic |
|----------------|--------|-------|
| Skills Match    | 40 pts | Required skills (30) + Preferred skills (10) |
| Experience      | 25 pts | Perfect fit = 25; penalized per year gap |
| Location        | 10 pts | Exact match = 10; mismatch = 4 |
| Availability    | 10 pts | ≤30d notice = 10; 31–60d = 7; >60d = 4 |
| Budget Fit      | 15 pts | Within budget = 15; over budget = 2 |

### Interest Score (0–100)
| Signal                  | Weight |
|------------------------|--------|
| Open to Work flag       | 30 pts |
| Profile recency (days ago) | 20 pts |
| Enthusiasm level (high/med/low) | 20 pts |
| Explicitly interested   | 15 pts |
| Asked for more info     | 8 pts  |
| Availability confirmed  | 7 pts  |
| Constraints mentioned   | −5 pts |

### Combined Score
```
Combined = 0.6 × Match Score + 0.4 × Interest Score
```
