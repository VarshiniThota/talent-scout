import json
import re
import os
from groq import Groq


def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set")
    return Groq(api_key=api_key)


def simulate_candidate_conversation(candidate: dict, parsed_jd: dict) -> dict:
    """
    Simulates a realistic outreach conversation using Groq (free Llama 3).
    Returns conversation log + interest_score + signals.
    """
    client = get_groq_client()

    prompt = f"""Simulate a realistic 6-message outreach conversation between an AI Recruiter Bot and a job candidate.

Candidate Profile:
- Name: {candidate['name']}
- Title: {candidate['title']}, {candidate['experience_years']} years exp
- Current Company: {candidate['current_company']}
- Open to Work: {candidate['open_to_work']}
- Last Active: {candidate['last_active_days_ago']} days ago
- Expected CTC: Rs {candidate['expected_ctc_lpa']} LPA
- Notice Period: {candidate['notice_period_days']} days
- Summary: {candidate['summary']}

Job Being Offered:
- Role: {parsed_jd.get('role_title', 'Software Engineer')}
- Budget: Rs {parsed_jd.get('budget_min_lpa', 'N/A')} to {parsed_jd.get('budget_max_lpa', 'N/A')} LPA
- Location: {parsed_jd.get('location', 'Bangalore')}

Rules:
- If open_to_work is True and last active <= 7 days: candidate is enthusiastic
- If open_to_work is False or last active > 14 days: candidate is hesitant/passive
- Make responses sound natural and human

Return ONLY this JSON (no markdown, no extra text):
{{
  "conversation": [
    {{"speaker": "Recruiter Bot", "message": "..."}},
    {{"speaker": "{candidate['name']}", "message": "..."}},
    {{"speaker": "Recruiter Bot", "message": "..."}},
    {{"speaker": "{candidate['name']}", "message": "..."}},
    {{"speaker": "Recruiter Bot", "message": "..."}},
    {{"speaker": "{candidate['name']}", "message": "..."}}
  ],
  "interest_signals": {{
    "explicitly_interested": true or false,
    "asked_for_more_info": true or false,
    "mentioned_constraints": true or false,
    "availability_confirmed": true or false,
    "enthusiasm_level": "high or medium or low"
  }}
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1200,
        temperature=0.7,
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    # Find JSON object in response robustly
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        raw = match.group(0)

    result = json.loads(raw)
    result["interest_score"] = compute_interest_score(candidate, result.get("interest_signals", {}))
    return result


def compute_interest_score(candidate: dict, signals: dict) -> float:
    score = 0

    # Open to work (30 pts)
    if candidate.get("open_to_work", False):
        score += 30

    # Recency (20 pts)
    days_ago = candidate.get("last_active_days_ago", 30)
    if days_ago <= 3:    score += 20
    elif days_ago <= 7:  score += 14
    elif days_ago <= 14: score += 8
    else:                score += 2

    # Conversation signals (50 pts)
    enthusiasm = signals.get("enthusiasm_level", "low")
    if enthusiasm == "high":   score += 20
    elif enthusiasm == "medium": score += 12
    else:                        score += 4

    if signals.get("explicitly_interested"):  score += 15
    if signals.get("asked_for_more_info"):    score += 8
    if signals.get("availability_confirmed"): score += 7
    if signals.get("mentioned_constraints"):  score -= 5

    return round(min(max(score, 0), 100), 1)
