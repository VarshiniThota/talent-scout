import os
import re
from groq import Groq
from data.candidates import CANDIDATES


def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set")
    return Groq(api_key=api_key)


def compute_match_score(candidate: dict, parsed_jd: dict) -> dict:
    """
    Rule-based matching across 5 dimensions.
    Returns match_score (0-100) with full breakdown.
    """
    breakdown = {}
    total_score = 0

    # 1. Skills Match (40 pts)
    required = [s.lower() for s in parsed_jd.get("required_skills", [])]
    preferred = [s.lower() for s in parsed_jd.get("preferred_skills", [])]
    candidate_skills = [s.lower() for s in candidate.get("skills", [])]

    req_matched = [s for s in required if any(s in cs or cs in s for cs in candidate_skills)]
    pref_matched = [s for s in preferred if any(s in cs or cs in s for cs in candidate_skills)]

    req_score  = (len(req_matched) / len(required) * 30) if required else 30
    pref_score = (len(pref_matched) / len(preferred) * 10) if preferred else 10
    skills_score = min(req_score + pref_score, 40)
    total_score += skills_score
    breakdown["skills"] = {
        "score": round(skills_score, 1), "max": 40,
        "required_matched": req_matched,
        "preferred_matched": pref_matched,
        "missing_required": [s for s in required if s not in req_matched],
    }

    # 2. Experience Match (25 pts)
    exp     = candidate.get("experience_years", 0)
    exp_min = parsed_jd.get("experience_min_years", 0)
    exp_max = parsed_jd.get("experience_max_years", 99)

    if exp_min <= exp <= exp_max:
        exp_score, exp_note = 25, "Perfect fit"
    elif exp < exp_min:
        gap = exp_min - exp
        exp_score, exp_note = max(0, 25 - gap * 5), f"Underqualified by {gap} yr(s)"
    else:
        gap = exp - exp_max
        exp_score, exp_note = max(15, 25 - gap * 2), f"Overqualified by {gap} yr(s)"

    total_score += exp_score
    breakdown["experience"] = {
        "score": round(exp_score, 1), "max": 25,
        "candidate_years": exp,
        "required_range": f"{exp_min}–{exp_max} yrs",
        "note": exp_note,
    }

    # 3. Location Match (10 pts)
    jd_loc   = parsed_jd.get("location", "Any").lower()
    cand_loc = candidate.get("location", "").lower()
    if jd_loc in ["any", "remote", "pan india"]:
        loc_score, loc_note = 10, "No restriction"
    elif any(w in cand_loc for w in jd_loc.split(",")):
        loc_score, loc_note = 10, "Location match"
    else:
        loc_score, loc_note = 4, "Different location (relocation possible)"
    total_score += loc_score
    breakdown["location"] = {"score": loc_score, "max": 10, "note": loc_note}

    # 4. Availability (10 pts)
    notice = candidate.get("notice_period_days", 60)
    if notice <= 30:
        avail_score, avail_note = 10, f"Quick joiner ({notice}d notice)"
    elif notice <= 60:
        avail_score, avail_note = 7, f"Standard notice ({notice}d)"
    else:
        avail_score, avail_note = 4, f"Long notice ({notice}d)"
    total_score += avail_score
    breakdown["availability"] = {"score": avail_score, "max": 10, "note": avail_note}

    # 5. Budget Fit (15 pts)
    budget_max = parsed_jd.get("budget_max_lpa")
    expected   = candidate.get("expected_ctc_lpa", 0)
    if budget_max is None:
        budget_score, budget_note = 10, "Budget not specified"
    elif expected <= budget_max:
        budget_score, budget_note = 15, f"Within budget (expects ₹{expected}L)"
    elif expected <= budget_max * 1.2:
        budget_score, budget_note = 8, f"Slightly above budget (expects ₹{expected}L)"
    else:
        budget_score, budget_note = 2, f"Over budget (expects ₹{expected}L)"
    total_score += budget_score
    breakdown["budget"] = {"score": budget_score, "max": 15, "note": budget_note}

    return {"match_score": round(min(total_score, 100), 1), "breakdown": breakdown}


def get_top_candidates(parsed_jd: dict, top_n: int = 8) -> list:
    scored = []
    for candidate in CANDIDATES:
        result = compute_match_score(candidate, parsed_jd)
        scored.append({**candidate,
                       "match_score": result["match_score"],
                       "match_breakdown": result["breakdown"]})
    scored.sort(key=lambda x: (x["open_to_work"], x["match_score"]), reverse=True)
    return scored[:top_n]


def explain_match(candidate: dict, parsed_jd: dict) -> str:
    """AI-generated recruiter note using Groq (free)."""
    client = get_groq_client()

    prompt = f"""You are a recruiter assistant. Write a concise 2-3 sentence honest note about why this candidate is or isn't a strong match. Be specific.

Candidate: {candidate['name']}, {candidate['title']}, {candidate['experience_years']} yrs experience
Skills: {', '.join(candidate['skills'][:6])}
Summary: {candidate['summary']}

Job Role: {parsed_jd.get('role_title', 'N/A')}
Required Skills: {', '.join(parsed_jd.get('required_skills', [])[:6])}
Experience needed: {parsed_jd.get('experience_min_years', 0)}-{parsed_jd.get('experience_max_years', 10)} years
Match Score: {candidate.get('match_score', 0)}/100

Recruiter note (2-3 sentences only):"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()
