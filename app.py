import streamlit as st
import json
import time
import os
from agent.jd_parser import parse_jd
from agent.candidate_matcher import get_top_candidates, explain_match
from agent.outreach_agent import simulate_candidate_conversation

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TalentScout AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
/* Main background */
.stApp { background-color: #0f1117; }

/* Cards */
.candidate-card {
    background: linear-gradient(135deg, #1e2130 0%, #252840 100%);
    border: 1px solid #2e3250;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
    transition: box-shadow 0.2s;
}
.candidate-card:hover { box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3); }

/* Score badges */
.score-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.85rem;
}
.score-high { background: #064e3b; color: #34d399; border: 1px solid #34d399; }
.score-mid  { background: #451a03; color: #fbbf24; border: 1px solid #fbbf24; }
.score-low  { background: #450a0a; color: #f87171; border: 1px solid #f87171; }

/* Tag pills */
.skill-tag {
    display: inline-block;
    background: #1e3a5f;
    color: #60a5fa;
    border-radius: 12px;
    padding: 2px 10px;
    margin: 2px;
    font-size: 0.78rem;
}

/* Chat bubble */
.chat-bot {
    background: #1e2a3a;
    border-left: 3px solid #6366f1;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 6px 0;
    color: #e2e8f0;
}
.chat-candidate {
    background: #1a2e1a;
    border-left: 3px solid #34d399;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 6px 0;
    color: #e2e8f0;
}

/* Section headers */
.section-header {
    font-size: 1.4rem;
    font-weight: 700;
    color: #a5b4fc;
    border-bottom: 2px solid #3730a3;
    padding-bottom: 8px;
    margin-bottom: 16px;
}

/* Metric box */
.metric-box {
    background: #1e2130;
    border: 1px solid #2e3250;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}

/* Combined score */
.combined-score {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #6366f1, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
</style>
""",
    unsafe_allow_html=True,
)


# ── Auto-load API key from secrets or env ────────────────────────────────────
def load_api_key():
    if os.environ.get("GROQ_API_KEY"):
        return os.environ["GROQ_API_KEY"]
    try:
        key = st.secrets["GROQ_API_KEY"]
        if key:
            os.environ["GROQ_API_KEY"] = key
            return key
    except Exception:
        pass
    return None

auto_key = load_api_key()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎯 TalentScout AI")
    st.markdown("*AI-Powered Talent Scouting & Engagement Agent*")
    st.divider()

    if auto_key:
        st.success("✅ AI Engine Ready")
        api_key = auto_key
    else:
        manual_key = st.text_input(
            "🔑 Groq API Key (FREE)",
            type="password",
            placeholder="gsk_...",
            help="Get a FREE key at console.groq.com — no credit card needed",
        )
        if manual_key:
            os.environ["GROQ_API_KEY"] = manual_key
            api_key = manual_key
            st.success("✅ API Key set")
        else:
            api_key = None

    st.divider()
    st.markdown("### ⚙️ Settings")
    top_n = st.slider("Candidates to scout", min_value=3, max_value=10, value=5)
    run_outreach = st.toggle("Run Conversational Outreach", value=True)

    st.divider()
    st.markdown("### 📖 How it works")
    st.markdown(
        """
1. **Paste** your Job Description  
2. **AI parses** requirements & skills  
3. **Candidates matched** with explainable scores  
4. **AI simulates** outreach conversations  
5. **Ranked shortlist** with Match + Interest scores  
"""
    )

    st.divider()
    st.caption("Built for Catalyst Hackathon · Deccan AI")


# ── Main Content ──────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align:center; color:#a5b4fc; margin-bottom:4px;'>🎯 TalentScout AI</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:#6b7280; margin-bottom:32px;'>Paste a Job Description → Get a ranked, scored candidate shortlist in seconds</p>",
    unsafe_allow_html=True,
)

# ── Sample JDs ────────────────────────────────────────────────────────────────
SAMPLE_JDS = {
    "🐍 Python Backend Engineer": """
We are looking for a Senior Python Backend Engineer to join our growing engineering team.

Role: Senior Python Backend Engineer
Experience: 4-7 years
Location: Hyderabad, India (Hybrid)
Budget: ₹15–25 LPA

Required Skills:
- Python (FastAPI or Flask)
- PostgreSQL / MySQL
- Docker & containerization
- REST API design
- Microservices architecture

Preferred Skills:
- AWS or GCP
- Redis / Celery
- System design experience

Responsibilities:
- Design and build scalable backend services
- Lead API design and database architecture
- Mentor junior developers
- Collaborate with frontend and DevOps teams

We value fast learners who take ownership and move fast.
""",
    "🤖 ML / AI Engineer": """
Hiring a Machine Learning Engineer to build next-gen AI products.

Role: Machine Learning Engineer  
Experience: 3-6 years
Location: Bangalore or Remote (India)
Budget: ₹18–30 LPA

Required Skills:
- Python
- PyTorch or TensorFlow
- NLP / LLMs
- Model training and fine-tuning
- FastAPI for model serving

Preferred Skills:
- LangChain, Hugging Face
- RAG pipelines
- Vector databases
- AWS SageMaker

Responsibilities:
- Build and deploy ML models at scale
- Work on NLP and generative AI features
- Collaborate with product and data teams
""",
    "☁️ DevOps / SRE": """
Looking for a DevOps / Site Reliability Engineer for our cloud platform team.

Role: Senior DevOps / SRE
Experience: 5-9 years
Location: Bangalore, India
Budget: ₹20–35 LPA

Required Skills:
- Kubernetes & Docker
- AWS or GCP
- CI/CD pipelines (Jenkins / GitHub Actions)
- Infrastructure as Code (Terraform)
- Python scripting

Preferred Skills:
- Prometheus, Grafana, observability
- Incident management
- Security & compliance

Responsibilities:
- Manage cloud infrastructure for high-traffic services
- Build automation and deployment pipelines
- Own SLOs and uptime SLAs
""",
}

col_jd, col_sample = st.columns([3, 1])
with col_sample:
    st.markdown("**📋 Try a sample JD:**")
    for label in SAMPLE_JDS:
        if st.button(label, use_container_width=True):
            st.session_state["jd_text"] = SAMPLE_JDS[label]

with col_jd:
    jd_input = st.text_area(
        "📄 Paste your Job Description",
        value=st.session_state.get("jd_text", ""),
        height=260,
        placeholder="Paste the full job description here including role, required skills, experience, location, and budget...",
    )

st.markdown("<br>", unsafe_allow_html=True)

run_col, _ = st.columns([1, 3])
with run_col:
    run_button = st.button(
        "🚀 Scout Candidates",
        type="primary",
        use_container_width=True,
        disabled=not (api_key and jd_input.strip()),
    )

if not api_key:
    st.info("👈 Add your FREE Groq API key in the sidebar. Get one at [console.groq.com](https://console.groq.com) — no credit card, takes 1 minute!")

if not jd_input.strip() and api_key:
    st.info("📄 Paste a job description above or click a sample JD to begin.")

# ── Pipeline Execution ────────────────────────────────────────────────────────
if run_button and api_key and jd_input.strip():

    # ── Step 1: Parse JD ──
    st.divider()
    st.markdown('<div class="section-header">📋 Step 1 · Parsing Job Description</div>', unsafe_allow_html=True)

    with st.spinner("Claude is parsing the job description..."):
        try:
            parsed_jd = parse_jd(jd_input)
            st.success("✅ JD parsed successfully")
        except Exception as e:
            st.error(f"Failed to parse JD: {e}")
            st.stop()

    # Display parsed JD
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**🎯 Role:** {parsed_jd.get('role_title', 'N/A')}")
        st.markdown(f"**📍 Location:** {parsed_jd.get('location', 'Any')}")
        st.markdown(f"**💼 Type:** {parsed_jd.get('employment_type', 'Full-time')}")
    with col2:
        exp_min = parsed_jd.get("experience_min_years", 0)
        exp_max = parsed_jd.get("experience_max_years", 10)
        st.markdown(f"**⏱ Experience:** {exp_min}–{exp_max} years")
        b_min = parsed_jd.get("budget_min_lpa", "N/A")
        b_max = parsed_jd.get("budget_max_lpa", "N/A")
        st.markdown(f"**💰 Budget:** ₹{b_min}–{b_max} LPA")
        st.markdown(f"**🏷 Domain:** {parsed_jd.get('domain', 'Engineering')}")
    with col3:
        req_skills = parsed_jd.get("required_skills", [])
        skill_html = " ".join([f'<span class="skill-tag">{s}</span>' for s in req_skills[:8]])
        st.markdown(f"**🔧 Required Skills:**<br>{skill_html}", unsafe_allow_html=True)

    with st.expander("🔍 Full Parsed JD (JSON)"):
        st.json(parsed_jd)

    # ── Step 2: Match Candidates ──
    st.divider()
    st.markdown('<div class="section-header">🔍 Step 2 · Discovering & Matching Candidates</div>', unsafe_allow_html=True)

    with st.spinner(f"Scanning {20} candidate profiles..."):
        try:
            top_candidates = get_top_candidates(parsed_jd, top_n=top_n)
            st.success(f"✅ Found {len(top_candidates)} best-matched candidates")
        except Exception as e:
            st.error(f"Matching failed: {e}")
            st.stop()

    # ── Step 3: Outreach ──
    if run_outreach:
        st.divider()
        st.markdown('<div class="section-header">💬 Step 3 · Running Conversational Outreach</div>', unsafe_allow_html=True)

        outreach_results = {}
        progress = st.progress(0, text="Starting outreach simulations...")

        for i, candidate in enumerate(top_candidates):
            progress.progress((i + 1) / len(top_candidates), text=f"Engaging {candidate['name']}...")
            try:
                result = simulate_candidate_conversation(candidate, parsed_jd)
                outreach_results[candidate["id"]] = result
            except Exception as e:
                outreach_results[candidate["id"]] = {
                    "conversation": [],
                    "interest_score": 40,
                    "interest_signals": {},
                    "error": str(e),
                }
            time.sleep(0.3)

        progress.empty()
        st.success("✅ Outreach conversations completed")

    # ── Step 4: Final Ranked Shortlist ──
    st.divider()
    st.markdown('<div class="section-header">🏆 Step 4 · Ranked Candidate Shortlist</div>', unsafe_allow_html=True)

    # Add interest scores and compute combined score
    final_candidates = []
    for candidate in top_candidates:
        interest_data = outreach_results.get(candidate["id"], {}) if run_outreach else {}
        interest_score = interest_data.get("interest_score", 50)
        combined = round(0.6 * candidate["match_score"] + 0.4 * interest_score, 1)

        final_candidates.append(
            {
                **candidate,
                "interest_score": interest_score,
                "combined_score": combined,
                "conversation": interest_data.get("conversation", []),
                "interest_signals": interest_data.get("interest_signals", {}),
            }
        )

    # Sort by combined score
    final_candidates.sort(key=lambda x: x["combined_score"], reverse=True)

    # ── Summary metrics ──
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        avg_match = round(sum(c["match_score"] for c in final_candidates) / len(final_candidates), 1)
        st.metric("Avg Match Score", f"{avg_match}/100")
    with m2:
        if run_outreach:
            avg_interest = round(sum(c["interest_score"] for c in final_candidates) / len(final_candidates), 1)
            st.metric("Avg Interest Score", f"{avg_interest}/100")
        else:
            st.metric("Candidates Scouted", len(final_candidates))
    with m3:
        top_score = final_candidates[0]["combined_score"]
        st.metric("Top Combined Score", f"{top_score}/100")
    with m4:
        hot = sum(1 for c in final_candidates if c["combined_score"] >= 70)
        st.metric("🔥 Hot Candidates", hot)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Candidate Cards ──
    for rank, candidate in enumerate(final_candidates, 1):
        ms = candidate["match_score"]
        is_ = candidate["interest_score"]
        cs = candidate["combined_score"]

        def score_class(s):
            return "score-high" if s >= 70 else "score-mid" if s >= 45 else "score-low"

        # Card
        with st.container():
            st.markdown(
                f"""
<div class="candidate-card">
  <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
    <div>
      <span style="font-size:1.25rem; font-weight:700; color:#e2e8f0;">#{rank} · {candidate['name']}</span>
      <span style="color:#9ca3af; margin-left:12px;">{candidate['title']} · {candidate['experience_years']} yrs</span>
    </div>
    <div style="display:flex; gap:10px; align-items:center;">
      <span class="score-badge {score_class(ms)}">Match {ms}%</span>
      <span class="score-badge {score_class(is_)}">Interest {is_}%</span>
      <span style="font-size:1.1rem; font-weight:800; color:#a5b4fc;">⚡ {cs}% Combined</span>
    </div>
  </div>
  <div style="color:#9ca3af; margin-top:6px; font-size:0.85rem;">
    🏢 {candidate['current_company']} &nbsp;·&nbsp; 📍 {candidate['location']} &nbsp;·&nbsp; ⏱ {candidate['notice_period_days']}d notice &nbsp;·&nbsp; 💰 ₹{candidate['expected_ctc_lpa']}L
  </div>
</div>
""",
                unsafe_allow_html=True,
            )

            with st.expander(f"📊 Details · {candidate['name']}"):
                tab1, tab2, tab3 = st.tabs(["🔍 Match Breakdown", "💬 Outreach Conversation", "📝 Summary"])

                with tab1:
                    breakdown = candidate.get("match_breakdown", {})
                    cols = st.columns(5)
                    categories = [
                        ("skills", "🔧 Skills"),
                        ("experience", "⏱ Experience"),
                        ("location", "📍 Location"),
                        ("availability", "📅 Availability"),
                        ("budget", "💰 Budget"),
                    ]
                    for col, (key, label) in zip(cols, categories):
                        with col:
                            data = breakdown.get(key, {})
                            score = data.get("score", 0)
                            max_s = data.get("max", 0)
                            pct = round(score / max_s * 100) if max_s else 0
                            clr = "#34d399" if pct >= 70 else "#fbbf24" if pct >= 40 else "#f87171"
                            st.markdown(
                                f"<div style='text-align:center;'>"
                                f"<div style='font-size:0.8rem;color:#9ca3af;'>{label}</div>"
                                f"<div style='font-size:1.4rem;font-weight:800;color:{clr};'>{score}/{max_s}</div>"
                                f"<div style='font-size:0.75rem;color:#6b7280;'>{data.get('note','')}</div>"
                                f"</div>",
                                unsafe_allow_html=True,
                            )

                    # Skills detail
                    st.markdown("---")
                    skills_data = breakdown.get("skills", {})
                    if skills_data.get("required_matched"):
                        matched_html = " ".join(
                            [f'<span class="skill-tag" style="background:#064e3b;color:#34d399;">✓ {s}</span>' for s in skills_data["required_matched"]]
                        )
                        st.markdown(f"**✅ Required skills matched:** {matched_html}", unsafe_allow_html=True)
                    if skills_data.get("missing_required"):
                        missing_html = " ".join(
                            [f'<span class="skill-tag" style="background:#450a0a;color:#f87171;">✗ {s}</span>' for s in skills_data["missing_required"]]
                        )
                        st.markdown(f"**❌ Missing required skills:** {missing_html}", unsafe_allow_html=True)

                with tab2:
                    if run_outreach and candidate.get("conversation"):
                        for msg in candidate["conversation"]:
                            speaker = msg.get("speaker", "")
                            text = msg.get("message", "")
                            is_bot = "Bot" in speaker or "Recruiter" in speaker
                            css_class = "chat-bot" if is_bot else "chat-candidate"
                            icon = "🤖" if is_bot else "👤"
                            st.markdown(
                                f'<div class="{css_class}"><strong>{icon} {speaker}</strong><br>{text}</div>',
                                unsafe_allow_html=True,
                            )

                        signals = candidate.get("interest_signals", {})
                        if signals:
                            st.markdown("---")
                            st.markdown("**📡 Interest Signals Detected:**")
                            sc1, sc2, sc3, sc4 = st.columns(4)
                            with sc1:
                                v = signals.get("explicitly_interested", False)
                                st.markdown(f"{'✅' if v else '❌'} Explicitly interested")
                            with sc2:
                                v = signals.get("asked_for_more_info", False)
                                st.markdown(f"{'✅' if v else '❌'} Asked for more info")
                            with sc3:
                                v = signals.get("availability_confirmed", False)
                                st.markdown(f"{'✅' if v else '❌'} Availability confirmed")
                            with sc4:
                                enth = signals.get("enthusiasm_level", "low")
                                emoji = "🔥" if enth == "high" else "😐" if enth == "medium" else "❄️"
                                st.markdown(f"{emoji} Enthusiasm: **{enth}**")
                    else:
                        st.info("Outreach simulation was not run for this session.")

                with tab3:
                    # AI-generated explanation
                    with st.spinner("Generating recruiter note..."):
                        try:
                            note = explain_match(candidate, parsed_jd)
                            st.markdown(f"**🧠 Recruiter AI Note:**\n\n{note}")
                        except Exception:
                            st.info("Enable API key to see AI-generated recruiter notes.")

                    st.markdown("---")
                    st.markdown(f"**📖 Candidate Summary:**\n\n{candidate.get('summary', '')}")
                    st.markdown(f"**🎓 Education:** {candidate.get('education', 'N/A')}")
                    all_skills_html = " ".join([f'<span class="skill-tag">{s}</span>' for s in candidate.get("skills", [])])
                    st.markdown(f"**🔧 All Skills:** {all_skills_html}", unsafe_allow_html=True)

    # ── Export ──
    st.divider()
    st.markdown('<div class="section-header">📤 Export Shortlist</div>', unsafe_allow_html=True)

    export_data = [
        {
            "Rank": i + 1,
            "Name": c["name"],
            "Title": c["title"],
            "Experience (yrs)": c["experience_years"],
            "Match Score": c["match_score"],
            "Interest Score": c["interest_score"],
            "Combined Score": c["combined_score"],
            "Current Company": c["current_company"],
            "Location": c["location"],
            "Notice Period (days)": c["notice_period_days"],
            "Expected CTC (LPA)": c["expected_ctc_lpa"],
            "Open to Work": c["open_to_work"],
        }
        for i, c in enumerate(final_candidates)
    ]

    import pandas as pd

    df = pd.DataFrame(export_data)
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False)
    st.download_button(
        "⬇️ Download Shortlist CSV",
        data=csv,
        file_name=f"talent_shortlist_{parsed_jd.get('role_title','').replace(' ','_')}.csv",
        mime="text/csv",
    )
