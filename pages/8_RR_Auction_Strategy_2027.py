"""
Page 8: Rajasthan Royals IPL 2027 Auction Strategy & Player Fits — PRESSURE IQ
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="RR IPL 2027 Auction Strategy — PRESSURE IQ", page_icon="👑", layout="wide")
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_dir = os.path.join(project_root, "outputs")

# Custom CSS for Rajasthan Royals aesthetic
st.markdown("""
<style>
    .rr-header {
        background: linear-gradient(135deg, #0B1B3D 0%, #1E3A8A 50%, #D81B60 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
        border-left: 6px solid #FFB703;
    }
    .rr-title {
        font-size: 28px;
        font-weight: 800;
        letter-spacing: 0.5px;
        margin: 0;
        color: #FFFFFF;
    }
    .rr-subtitle {
        font-size: 15px;
        color: #E2E8F0;
        margin-top: 6px;
    }
    .stat-pill {
        background: rgba(216, 27, 96, 0.15);
        border: 1px solid #D81B60;
        color: #FFB703;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 13px;
    }
    .fit-card {
        background: #18264D;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="rr-header">
    <div class="rr-title">👑 RAJASTHAN ROYALS — IPL 2027 AUCTION INTELLIGENCE</div>
    <div class="rr-subtitle">Pressure Performance Intelligence (PRESSURE IQ) | Squad Construction & Target Acquisition Strategy</div>
</div>
""", unsafe_allow_html=True)

# Download and generation buttons row
col_d1, col_d2, col_d3, col_d4 = st.columns([1.8, 1.8, 1.8, 1.6])
pdf_master = os.path.join(output_dir, "Rajasthan_Royals_IPL_2027_Master_Intelligence_Report.pdf")
pdf_exec = os.path.join(output_dir, "Rajasthan_Royals_IPL_2027_Auction_Intelligence_Report.pdf")
pptx_file = os.path.join(output_dir, "Rajasthan_Royals_IPL_2027_Auction_Strategy.pptx")

with col_d1:
    if os.path.exists(pdf_master):
        with open(pdf_master, "rb") as f:
            st.download_button(
                label="📄 Download Master PDF (with Charts)",
                data=f.read(),
                file_name="Rajasthan_Royals_IPL_2027_Master_Intelligence_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.button("📄 Master PDF (Not Generated)", disabled=True, use_container_width=True)

with col_d2:
    if os.path.exists(pptx_file):
        with open(pptx_file, "rb") as f:
            st.download_button(
                label="📊 Download Presentation (.pptx)",
                data=f.read(),
                file_name="Rajasthan_Royals_IPL_2027_Auction_Strategy.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True
            )
    else:
        st.button("📊 PPTX (Not Generated)", disabled=True, use_container_width=True)

with col_d3:
    if st.button("⚡ Re-Generate PDF via Engine", use_container_width=True):
        with st.spinner("Generating publication-grade charts & compiling 8-page PDF..."):
            try:
                from scripts.generate_master_report_pdf import generate_master_report
                generate_master_report()
                st.success("Master PDF with embedded dashboard charts compiled successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Generation error: {e}")

with col_d4:
    if os.path.exists(pdf_exec):
        with open(pdf_exec, "rb") as f:
            st.download_button(
                label="📑 Executive Brief PDF",
                data=f.read(),
                file_name="Rajasthan_Royals_IPL_2027_Auction_Intelligence_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

st.markdown("---")

@st.cache_data
def load_data():
    bat = pd.read_csv(os.path.join(output_dir, "batter_rankings.csv")).head(10)
    bowl = pd.read_csv(os.path.join(output_dir, "bowler_rankings.csv")).head(10)
    return bat, bowl

bat_df, bowl_df = load_data()

tabs = st.tabs([
    "🎯 Tactical Imperatives",
    "🏏 Top 10 Batters for RR",
    "🎯 Top 10 Bowlers for RR",
    "💰 Auction Purse Strategy & Tiers",
    "🛡️ Recommended Starting XII"
])

# -------------------------------------------------------------
# TAB 1: Tactical Imperatives
# -------------------------------------------------------------
with tabs[0]:
    st.markdown("### 🔍 Rajasthan Royals: Core Foundation & Tactical Gaps")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        #### 🏰 Current Core Strengths
        - **Elite Indian Top-Order:** Yashasvi Jaiswal, Captain Sanju Samson, and Riyan Parag form one of the highest-scoring top 4s in T20 cricket.
        - **Death Swing Specialist:** Sandeep Sharma's wide yorkers and knuckleballs are elite in low-to-medium scoring defense.
        - **Indian WK/Finisher Evolution:** Dhruv Jurel's calm temperament provides domestic stability.
        """)
        
    with col2:
        st.markdown("""
        #### ⚠️ High-Pressure Playoff Vulnerabilities
        1. **Middle-Order Spin Stagnation:** When early wickets fall chasing 180+, RR over-relies on Samson. Lacks an anchor-aggressor who crushes spin.
        2. **Death-Overs Chase Collapses:** When Hetmyer or Jurel fall early, RR's scoring drops precipitously. Needs an elite finisher striking at 180+ in overs 17–20.
        3. **Jaipur SMS Stadium Nuances:** Expansive square boundaries require defensive mystery spin (<6.50 RPO) and 145+ km/h express death enforcers.
        """)

    st.markdown("---")
    st.markdown("#### 📊 Pressure IQ Evaluation: How We Screen Targets for RR")
    st.markdown("""
    Every delivery in our 200,999-ball historical database (IPL & T20I, 2022–2026) is evaluated on:
    - **Chase Urgency (45%):** RRR escalation, balls left, wickets down.
    - **Context-Adjusted ML Model:** Out-of-sample `HistGradientBoosting` predicting expected runs per ball.
    - **Baseline Normalization:** Evaluating players against *all non-pressure balls* to eliminate small-sample finisher distortions.
    - **Empirical Bayes Shrinkage (N₀ = 75):** Ensuring emerging domestic talents are weighted fairly against veteran internationals.
    """)

# -------------------------------------------------------------
# TAB 2: Top 10 Batters for RR
# -------------------------------------------------------------
with tabs[1]:
    st.markdown("### 🏏 Top 10 Batters Under Pressure: Strategic Fit for Rajasthan Royals")
    
    bat_fits = {
        "Shreyas Iyer": {
            "tier": "Tier 1 Marquee Target",
            "pos": "No. 3/4 Anchor-Aggressor & Spin Destroyer",
            "fit": "Shreyas is the missing link in RR's top 5. When early wickets fall, RR becomes over-reliant on Samson. Iyer brings proven IPL-winning captaincy, strikes at an astonishing 198.6 in high-pressure chases (+53.7 uplift), and completely neutralizes spin at Jaipur's large boundaries.",
            "stat": "Pressure SR: 198.6 | Uplift: +53.7 | 287 Pressure Balls"
        },
        "Dinesh Karthik": {
            "tier": "Tier 2 / Veteran Impact",
            "pos": "Specialist Death Finisher & Strategic Mentor",
            "fit": "DK's 194.1 pressure strike rate across 321 balls reflects supreme 360° boundary execution in overs 17–20. Acquiring a finisher of this profile creates the ideal mentor-partner for Dhruv Jurel.",
            "stat": "Pressure SR: 194.1 | Uplift: +53.8 | 321 Pressure Balls"
        },
        "Rinku Singh": {
            "tier": "Tier 1 HIGHEST PRIORITY TARGET",
            "pos": "The Ultimate Clutch Finisher (No. 5/6)",
            "fit": "Rinku is the crown jewel of pressure batting: 480 pressure balls across 38 matches striking at 185.2 (+52.2 uplift). Slotting Rinku at No. 5 alongside Shimron Hetmyer gives RR the most devastating left-hand/right-hand death-overs combination in IPL history, directly eliminating playoff chase collapses.",
            "stat": "Pressure SR: 185.2 | Uplift: +52.2 | 480 Pressure Balls"
        },
        "Ashutosh Sharma": {
            "tier": "Tier 2 High-Value Target",
            "pos": "High-Impact Domestic Finisher (No. 7 / Impact Sub)",
            "fit": "Boasts the highest strike rate uplift in elite cricket (+67.5 over normal overs). Ashutosh specializes in scoring against 145+ km/h express pace and reverse-sweeping death bowlers. He solves RR's lower-order tail issue.",
            "stat": "Pressure SR: 179.6 | Uplift: +67.5 | 280 Pressure Balls"
        },
        "Suryakumar Yadav": {
            "tier": "Tier 1 Transformative Target",
            "pos": "360° Match Winner (No. 3/4)",
            "fit": "540 pressure deliveries with +175.2 runs above expectation. On Jaipur's large square boundaries, his ramp shots and backward-point access exploit field gaps that conventional hitters cannot breach.",
            "stat": "Pressure SR: 184.3 | Uplift: +22.3 | 540 Pressure Balls"
        },
        "Mahendra Singh Dhoni": {
            "tier": "Strategic Benchmark",
            "pos": "Tactical Death Ball Striker & Crisis Strategist",
            "fit": "333 pressure balls at 168.5 SR (+66.9 uplift). Represents the gold standard for game awareness, pacing chases down to the final over and manipulating opposition death bowlers' field sets.",
            "stat": "Pressure SR: 168.5 | Uplift: +66.9 | 333 Pressure Balls"
        },
        "Tim David": {
            "tier": "Tier 1 Overseas Finisher",
            "pos": "Overseas Power Monster (No. 6)",
            "fit": "520 pressure balls striking at 191.7 (+170.9 runs above context). David effortlessly clears Jaipur's longest 85m straight boundaries against both spin and pace, providing direct cover/rotation for Hetmyer.",
            "stat": "Pressure SR: 191.7 | Uplift: +24.5 | 520 Pressure Balls"
        },
        "Shashank Singh": {
            "tier": "Tier 2 High Purse Efficiency",
            "pos": "Middle-Order Domestic Firepower (No. 5/6)",
            "fit": "342 pressure balls at 179.8 SR across 24 matches. Shashank possesses exceptional composure when rebuilding from 40/3 and accelerating to 180+. He adds immense domestic bench depth without consuming an overseas slot.",
            "stat": "Pressure SR: 179.8 | Uplift: +46.8 | 342 Pressure Balls"
        },
        "Romario Shepherd": {
            "tier": "Tier 2 Tactical Balance",
            "pos": "Fast-Bowling All-Rounder (No. 7/8)",
            "fit": "473 pressure balls at 161.9 SR. Gives RR the multi-dimensional seam-bowling all-rounder they have lacked: 2 overs of heavy back-of-a-length pace and explosive lower-order hitting.",
            "stat": "Pressure SR: 161.9 | Uplift: +25.0 | 473 Pressure Balls"
        },
        "Andre Russell": {
            "tier": "Tier 1 Match Winner",
            "pos": "Game-Breaking All-Rounder",
            "fit": "377 pressure balls with +123.2 runs above expectation. Russell's intimidating presence completely distorts bowler plans at the death, creating boundary opportunities for his batting partners.",
            "stat": "Pressure SR: 178.5 | Uplift: +15.3 | 377 Pressure Balls"
        }
    }
    
    for idx, r in bat_df.iterrows():
        pname = r["player_name"]
        meta = bat_fits.get(pname, {
            "tier": "Target Candidate",
            "pos": "Middle Order",
            "fit": "High-pressure execution.",
            "stat": f"Rating: {r['shrunk_rating']:.4f}"
        })
        with st.expander(f"#{idx+1} {pname} — {meta['tier']} ({r['shrunk_rating']:.4f} Rating)", expanded=(idx < 3)):
            col_a, col_b = st.columns([1, 2])
            with col_a:
                st.markdown(f"**Target Role:** {meta['pos']}")
                st.markdown(f"**Key Stat:** `{meta['stat']}`")
                st.metric("Pressure SR", f"{r['strike_rate_pressure']:.1f}", f"{r['sr_uplift']:+.1f} Uplift")
            with col_b:
                st.markdown(f"**How He Strengthens RR:**\n\n{meta['fit']}")

# -------------------------------------------------------------
# TAB 3: Top 10 Bowlers for RR
# -------------------------------------------------------------
with tabs[2]:
    st.markdown("### 🎯 Top 10 Bowlers Under Pressure: Strategic Fit for Rajasthan Royals")
    
    bowl_fits = {
        "Sunil Narine": {
            "tier": "Tier 1 Highest Marquee Target",
            "pos": "Elite Mystery Spinner & Multi-Phase Suffocator",
            "fit": "Narine is the ultimate cheat code in T20 bowling: 318 pressure balls at an unbelievable 6.36 economy rate in high-leverage situations. On Sawai Mansingh Stadium's gripping tracks, Narine gives RR an impenetrable 4-over spin choke, completely eliminating opposition middle-over assaults.",
            "stat": "Pressure Econ: 6.36 | Improvement: +0.64 RPO | 20 Wickets"
        },
        "Sufiyan Muqeem": {
            "tier": "Tier 2 High-Value Target",
            "pos": "Mystery Left-Arm Wrist Spinner",
            "fit": "Concedes a microscopic 5.02 RPO across 203 pressure balls (+1.60 RPO improvement). Left-arm wrist spin is the rarest commodity in world cricket; his deceptive wrong'un turns away from right-handers, providing RR an unpickable wicket weapon.",
            "stat": "Pressure Econ: 5.02 | Improvement: +1.60 RPO | 20 Wickets"
        },
        "Jofra Archer": {
            "tier": "Tier 1 SQUAD SPEARHEAD (Homecoming)",
            "pos": "Express Enforcer & Death Bowling Spearhead",
            "fit": "The prodigal son's return to Rajasthan Royals! 291 pressure balls at 7.90 economy (+1.30 improvement over normal 9.20 economy). Archer provides the 148+ km/h hostility, hard-length bouncers, and searing yorkers that RR desperately needs to close out tight 10-run margin games.",
            "stat": "Pressure Econ: 7.90 | Improvement: +1.30 RPO | 25 Wickets"
        },
        "Mitchell Santner": {
            "tier": "Tier 2 Tactical Value",
            "pos": "Precision Finger Spinner & Lower-Order Batter",
            "fit": "404 pressure balls at 6.85 economy. Santner's trajectory changes and pinpoint stump-to-stump accuracy are tailor-made for Jaipur's big boundaries. He offers 4 economical overs and genuine No. 8 batting value.",
            "stat": "Pressure Econ: 6.85 | Improvement: +0.71 RPO | 26 Wickets"
        },
        "Matheesha Pathirana": {
            "tier": "Tier 1 ESSENTIAL TARGET",
            "pos": "Slingshot Death Wicket Machine",
            "fit": "The single most lethal death-over wicket taker in T20 cricket with a staggering 46 pressure wickets across 526 balls. Pairing Pathirana's 145 km/h dipping yorkers with Sandeep Sharma's wide slower-ball variations gives RR the most complete and unhittable death-overs bowling attack in the IPL.",
            "stat": "46 Pressure Wickets | 8.57 Pressure Econ | 526 Balls"
        },
        "Abrar Ahmed": {
            "tier": "Tier 2 Tactical Value",
            "pos": "Attacking Leg-Break / Googly Mystery Spinner",
            "fit": "229 pressure balls at 5.37 economy (+1.84 improvement). Bowls with rapid pace through the air, preventing batters from stepping out, perfectly suited to squeeze opposition teams at SMS Jaipur.",
            "stat": "Pressure Econ: 5.37 | Improvement: +1.84 RPO | 15 Wickets"
        },
        "Maheesh Theekshana": {
            "tier": "Tier 1 Powerplay/Death Spinner",
            "pos": "Multi-Phase Carrom-Ball Spinner",
            "fit": "474 pressure balls with 29 wickets. Can open the bowling in overs 1–6 and return for over 18, giving Sanju Samson immense bowling rotation flexibility.",
            "stat": "Pressure Econ: 7.46 | Improvement: +0.33 RPO | 29 Wickets"
        },
        "Mohammad Nawaz": {
            "tier": "Tier 3 Tactical Depth",
            "pos": "Experienced Left-Arm Finger Spinner & Pinch Hitter",
            "fit": "184 pressure balls at 5.58 economy. Highly disciplined line and length under intense pressure.",
            "stat": "Pressure Econ: 5.58 | Improvement: +1.89 RPO | 20 Wickets"
        },
        "Jamie Overton": {
            "tier": "Tier 2 Squad Impact",
            "pos": "Tall Hit-the-Deck Heavy Ball Pacer",
            "fit": "Outstanding +2.24 RPO economy improvement in pressure overs. Hits the splice of the bat on spicy pitches and provides genuine boundary hitting at No. 8.",
            "stat": "Pressure Econ: 7.10 | Improvement: +2.24 RPO | 17 Wickets"
        },
        "Sakib Hussain": {
            "tier": "Tier 3 Smart Money Buy",
            "pos": "Domestic Emerging Death Pacer",
            "fit": "Highest economy improvement in the entire bowling cohort (+3.08 RPO). An uncapped Indian bowler who thrives under pressure, freeing up valuable auction purse.",
            "stat": "Pressure Econ: 7.64 | Improvement: +3.08 RPO | 8 Wickets"
        }
    }
    
    for idx, r in bowl_df.iterrows():
        pname = r["player_name"]
        meta = bowl_fits.get(pname, {
            "tier": "Target Candidate",
            "pos": "Bowler",
            "fit": "Defensive control.",
            "stat": f"Rating: {r['shrunk_rating']:.4f}"
        })
        with st.expander(f"#{idx+1} {pname} — {meta['tier']} ({r['shrunk_rating']:.4f} Rating)", expanded=(idx < 3)):
            col_a, col_b = st.columns([1, 2])
            with col_a:
                st.markdown(f"**Target Role:** {meta['pos']}")
                st.markdown(f"**Key Stat:** `{meta['stat']}`")
                st.metric("Pressure Econ", f"{r['economy_pressure']:.2f}", f"{r['economy_improvement']:+.2f} Imprv")
            with col_b:
                st.markdown(f"**How He Strengthens RR:**\n\n{meta['fit']}")

# -------------------------------------------------------------
# TAB 4: Auction Purse Strategy & Tiers
# -------------------------------------------------------------
with tabs[3]:
    st.markdown("### 💰 IPL 2027 Auction Target Priority Matrix & Purse Tiers")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        #### 🥇 TIER 1: MARQUEE CORE
        *Allocation: 35% – 45% of Available Purse*
        - **Primary Batting Target:** **Rinku Singh** (Top Choice) or **Shreyas Iyer**
        - **Primary Bowling Target:** **Matheesha Pathirana** or **Jofra Archer**
        - **Tactical Rationale:** Must secure one elite death-overs finisher and one express 145+ km/h death bowler.
        """)
    with col2:
        st.markdown("""
        #### 🥈 TIER 2: HIGH-VALUE CORE
        *Allocation: 20% – 25% of Available Purse*
        - **Batting Targets:** **Ashutosh Sharma** / **Tim David**
        - **Bowling Targets:** **Sufiyan Muqeem** / **Mitchell Santner**
        - **Tactical Rationale:** Middle-overs spin strangulation at SMS Jaipur and dynamic power-hitting against express pace.
        """)
    with col3:
        st.markdown("""
        #### 🥉 TIER 3: SMART MONEY DEPTH
        *Allocation: 10% – 15% of Available Purse*
        - **Batting Target:** **Shashank Singh**
        - **Bowling Target:** **Sakib Hussain** / **Jamie Overton**
        - **Tactical Rationale:** High-upside uncapped Indian clutch performers who deliver elite pressure numbers at budget valuations.
        """)

    st.markdown("---")
    st.markdown("#### 🎯 Visual Target Allocation Framework")
    matrix_df = pd.DataFrame([
        {"Tier": "Tier 1: Marquee", "Purse %": 40, "Key Targets": "Rinku Singh, Matheesha Pathirana, Jofra Archer", "Role": "Elite Finishers & Death Enforcers"},
        {"Tier": "Tier 2: Value", "Purse %": 25, "Key Targets": "Ashutosh Sharma, Sufiyan Muqeem, Mitchell Santner", "Role": "Jaipur Spin Choke & Dynamic Impact Power"},
        {"Tier": "Tier 3: Depth", "Purse %": 15, "Key Targets": "Shashank Singh, Sakib Hussain, Jamie Overton", "Role": "Domestic Bench & Tactical Variations"},
        {"Tier": "Unallocated Reserve", "Purse %": 20, "Key Targets": "Tactical In-Auction Bidding Flexibility", "Role": "Backup Contingency"},
    ])
    fig_pie = px.pie(matrix_df, names="Tier", values="Purse %", title="Recommended Auction Purse Distribution", color_discrete_sequence=["#D81B60", "#FFB703", "#3B82F6", "#64748B"])
    st.plotly_chart(fig_pie, use_container_width=True)

# -------------------------------------------------------------
# TAB 5: Recommended Starting XII
# -------------------------------------------------------------
with tabs[4]:
    st.markdown("### 🛡️ Recommended Rajasthan Royals 'Pressure-Engineered' Starting XII")
    st.info("Constructed using empirical Pressure IQ ratings to maximize clutch conversion in playoff & high-stakes matches.")
    
    xi_data = [
        {"Batting Order": "1", "Player": "Yashasvi Jaiswal", "Role": "Aggressive Indian Opener", "Pressure Profile": "Attacking Powerplay Anchor"},
        {"Batting Order": "2", "Player": "Overseas Explosive Opener", "Role": "Powerplay Enforcer", "Pressure Profile": "Boundary Maximizer"},
        {"Batting Order": "3", "Player": "Sanju Samson (C/WK)", "Role": "Captain / Anchor-Attacker", "Pressure Profile": "Middle-Overs Stabilizer"},
        {"Batting Order": "4", "Player": "Shreyas Iyer / Riyan Parag", "Role": "Middle-Order Spin Destroyer", "Pressure Profile": "0.7522 Rating | 198.6 Pressure SR"},
        {"Batting Order": "5", "Player": "RINKU SINGH", "Role": "Elite High-Leverage Finisher #1", "Pressure Profile": "0.7369 Rating | 185.2 Pressure SR | +52.2 Uplift"},
        {"Batting Order": "6", "Player": "Shimron Hetmyer", "Role": "Overseas Power Finisher", "Pressure Profile": "Death Overs Boundary Hitter"},
        {"Batting Order": "7", "Player": "Dhruv Jurel", "Role": "Indian WK / Clutch Finisher", "Pressure Profile": "Calm Temperament at the Death"},
        {"Batting Order": "8", "Player": "Mitchell Santner / Romario Shepherd", "Role": "Multi-Phase Bowling All-Rounder", "Pressure Profile": "6.85 Pressure Econ / 161.9 SR"},
        {"Batting Order": "9", "Player": "Sandeep Sharma", "Role": "Death Swing & Wide Yorker Specialist", "Pressure Profile": "Knuckleball & Wide Line Mastery"},
        {"Batting Order": "10", "Player": "MATHEESHA PATHIRANA / JOFRA ARCHER", "Role": "Express 145+ km/h Death Spearhead", "Pressure Profile": "0.7212 Rating | 46 Pressure Wickets"},
        {"Batting Order": "11", "Player": "Sufiyan Muqeem / Indian Spinner", "Role": "Jaipur Mystery Spin Choke", "Pressure Profile": "0.7323 Rating | 5.02 Pressure Econ"},
        {"Batting Order": "IMPACT SUB", "Player": "Ashutosh Sharma / Sakib Hussain", "Role": "Dynamic Specialist Sub", "Pressure Profile": "0.7248 Rating (+67.5 SR) / +3.08 Econ Imprv"},
    ]
    st.table(pd.DataFrame(xi_data))
    
    st.success("""
    **🏆 STRATEGIC VERDICT:**
    By pairing **Rinku Singh** (or Shreyas Iyer) with Shimron Hetmyer in the middle-to-death overs and deploying **Matheesha Pathirana** (or Jofra Archer) alongside Sandeep Sharma at the death, Rajasthan Royals will possess statistically the most pressure-resilient squad in IPL history, perfectly engineered to capture the 2027 Trophy!
    """)
