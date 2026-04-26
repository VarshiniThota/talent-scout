import json
import re
import os
from groq import Groq


def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set. Get a FREE key at https://console.groq.com")
    return Groq(api_key=api_key)


def parse_jd(jd_text: str) -> dict:
    """
    Uses Groq (FREE - Llama 3) to parse a Job Description into structured data.
    """
    client = get_groq_client()

    prompt = f"""You are an expert HR analyst. Parse the following Job Description into structured JSON.

Job Description:
{jd_text}

Return ONLY a valid JSON object (no markdown, no explanation) with these exact fields:
{{
  "role_title": "string",
  "required_skills": ["list of must-have technical skills"],
  "preferred_skills": ["list of nice-to-have skills"],
  "experience_min_years": 0,
  "experience_max_years": 10,
  "location": "string or Remote or Any",
  "education_requirement": "string",
  "key_responsibilities": ["list of main responsibilities"],
  "budget_min_lpa": null,
  "budget_max_lpa": null,
  "employment_type": "Full-time",
  "domain": "string e.g. Backend, ML/AI, DevOps, Data, Frontend"
}}

If a field is not mentioned use sensible defaults. Return ONLY raw JSON, no code fences."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.1,
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)
