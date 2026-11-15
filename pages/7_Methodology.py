"""
Page 7: Methodology — Detailed statistical documentation and formulas for PRESSURE IQ.
"""
import streamlit as st
import os

st.set_page_config(page_title="Methodology — PRESSURE IQ", page_icon="📖", layout="wide")

st.markdown("# 📖 Methodology & Analytical Architecture")
st.markdown("*A Statistically Defensible Framework for Pressure-Performance Intelligence*")
st.markdown("---")

st.markdown("""
### 1. The Core Objective
The mandate is to identify **who performs better when the situation becomes difficult**, and **how consistently they deliver compared with their normal performance**.

Conventional cricket metrics (Strike Rate, Economy Rate, Average) are fundamentally confounded by match context:
- Scoring 24 runs off 12 balls in an already-won match is trivial.
- Scoring 24 runs off 12 balls needing 28 to win with 2 wickets remaining in the final over is extraordinary.
- Bowling 4 overs for 28 runs when defending 220 is standard.
- Defending 9 runs in the 20th over is peak clutch bowling.

PRESSURE IQ addresses this through an end-to-end context-aware, empirical shrinkage architecture.
""")

st.markdown("---")

st.markdown("### 2. The Pressure Index (PI) Formulation")

st.markdown(r"""
Every delivery $t$ in every match is evaluated independently based on pre-delivery match state. 
The Pressure Index $\text{PI}_t \in [0, 1]$ represents the difficulty and leverage of that specific delivery.

#### A. Second Innings (Run Chases)
In run chases, pressure is driven by urgency, remaining batting resources, and match closeness:

$$\text{PI}_{\text{chase}} = w_1 \cdot U_{\text{chase}} + w_2 \cdot R_{\text{resource}} + w_3 \cdot P_{\text{phase}} + w_4 \cdot C_{\text{comp}}$$

Where default calibrated weights are:
- $w_1 = 0.35$ (Chase Urgency)
- $w_2 = 0.25$ (Batting Resource Depletion)
- $w_3 = 0.15$ (Innings Phase Pressure)
- $w_4 = 0.25$ (Match Competitiveness / Closeness)

1. **Chase Urgency ($U_{\text{chase}}$)**:
   $$U_{\text{chase}} = 0.50 \cdot \sigma\left(0.5 \cdot (\text{RRR} - 9.0)\right) + 0.30 \cdot \left(1 - \frac{W_{\text{rem}} - 1}{9}\right) + 0.20 \cdot \left(1 - \frac{B_{\text{rem}}}{120}\right)$$
   where $\sigma(z) = \frac{1}{1 + e^{-z}}$ is a logistic sigmoid centered at a par required run rate of 9.0 RPO.

2. **Resource Pressure ($R_{\text{resource}}$)**:
   Measures wickets lost relative to balls bowled. If a side has lost $\ge 7$ wickets, pressure spikes sharply regardless of stage:
   $$R_{\text{resource}} = 0.6 \cdot \left(\frac{W_{\text{lost}}}{10}\right) + 0.4 \cdot \max\left(0, \frac{W_{\text{lost}} - E[W]}{10}\right)$$

3. **Innings Phase ($P_{\text{phase}}$)**:
   - Powerplay (Overs 1–6): $0.25 + 0.05 \cdot (\text{over} / 5)$
   - Middle Overs (Overs 7–15): $0.15 + 0.15 \cdot ((\text{over} - 6) / 8)$
   - Death Overs (Overs 16–20): $0.50 + 0.40 \cdot ((\text{over} - 15) / 4)$

4. **Match Competitiveness ($C_{\text{comp}}$)**:
   Using win-probability estimation, competitiveness peaks when the match outcome is balanced:
   $$C_{\text{comp}} = 1.0 - 2.0 \cdot |\hat{P}(\text{Win}) - 0.5|$$

#### B. First Innings (Setting a Target)
In the first innings, there is no fixed target, but pressure arises from resource loss, death acceleration, and par-score deficits:

$$\text{PI}_{\text{1st}} = 0.45 \cdot R_{\text{resource}} + 0.35 \cdot P_{\text{phase}} + 0.20 \cdot \Delta_{\text{par}}$$

where $\Delta_{\text{par}}$ captures whether the batting side is falling behind the benchmark expected scoring curve.
""")

st.markdown("---")

st.markdown("### 3. Context-Adjusted Expected Performance Models")

st.markdown(r"""
To calculate true player impact, we predict expected baseline runs for every delivery using **Gradient Boosted Decision Trees** strictly evaluated using **Match-Grouped 5-Fold Cross-Validation** (to prevent data leakage across deliveries of the same match):

- **Expected Batting Runs** $\hat{y}_{\text{bat}} = f(\text{Context})$
- **Expected Bowling Runs** $\hat{y}_{\text{bowl}} = g(\text{Context})$

**Context Features**:
- Balls remaining, Wickets remaining, Cumulative runs
- Over number, Innings phase (Powerplay, Middle, Death)
- Match format (IPL vs T20I), Innings number
- Required run rate, Run rate differential, Target
- Pressure Index ($\text{PI}$)

The delivery impact is the surplus or deficit relative to this expectation:
- $\text{Batting Impact} = y_{\text{actual}} - \hat{y}_{\text{bat}}$ (positive is superior)
- $\text{Bowling Impact} = \hat{y}_{\text{bowl}} - y_{\text{actual}}$ (positive is superior)
""")

st.markdown("---")

st.markdown("### 4. Batting Pressure Rating Formula")

st.markdown(r"""
The final Batting Pressure Rating combines four orthogonal pillars:

$$\text{Rating}_{\text{bat}} = 0.35 \cdot Q_{\text{context}} + 0.30 \cdot U_{\text{uplift}} + 0.20 \cdot C_{\text{consistency}} + 0.15 \cdot S_{\text{reliability}}$$

1. **Context Quality ($Q_{\text{context}}$)**: Percentile rank of average context-adjusted impact per ball in high-pressure deliveries.
2. **Pressure Resilience Uplift ($U_{\text{uplift}}$)**: The differential between pressure strike rate/impact vs normal strike rate/impact:
   $$\text{Uplift} = \text{Impact}_{\text{pressure}} - \text{Impact}_{\text{normal}}$$
3. **Consistency ($C_{\text{consistency}}$)**: Inverse coefficient of variation ($1 / (1 + \text{CV})$) of match-level pressure performance.
4. **Sample Reliability ($S_{\text{reliability}}$)**: S-curve transformation based on qualifying volume.
""")

st.markdown("---")

st.markdown("### 5. Bowling Pressure Rating Formula")

st.markdown(r"""
$$\text{Rating}_{\text{bowl}} = 0.35 \cdot Q_{\text{context}} + 0.30 \cdot U_{\text{uplift}} + 0.15 \cdot W_{\text{wicket}} + 0.10 \cdot C_{\text{consistency}} + 0.10 \cdot S_{\text{reliability}}$$

1. **Context Run Prevention ($Q_{\text{context}}$)**: Runs saved relative to situation expectation per legal delivery.
2. **Economy Uplift ($U_{\text{uplift}}$)**: Improvement in economy rate under pressure relative to normal overs ($\text{Econ}_{\text{normal}} - \text{Econ}_{\text{pressure}}$).
3. **Wicket Impact ($W_{\text{wicket}}$)**: Legitimate bowler wickets (caught, bowled, LBW, stumped, hit wicket) scaled by leverage and resource depletion value.
4. **Consistency ($C_{\text{consistency}}$)**: Match-to-match stability of economy and impact under pressure.
5. **Reliability ($S_{\text{reliability}}$)**: S-curve exposure weight based on qualifying legal deliveries.
""")

st.markdown("---")

st.markdown("### 6. Empirical Bayes Shrinkage")

st.markdown(r"""
To eliminate small-sample bias without arbitrarily cutting off valuable emergent performers:

$$R_{\text{shrunk}} = (1 - B) \cdot R_{\text{raw}} + B \cdot \mu_{\text{population}}$$

where the shrinkage coefficient $B$ is derived from individual standard error and population variance:

$$B = \frac{\sigma^2_i}{\sigma^2_i + \tau^2}$$

A player with 35 balls faced will have their rating shrunk significantly toward the population mean ($0.50$), whereas a veteran with 250+ balls faced retains their observed raw rating.
""")

st.markdown("---")

st.markdown("### 7. Eligibility & Minimum Thresholds")

st.markdown("""
To guarantee statistical significance:
- **Batters**: Minimum 30 balls faced in high-pressure situations, 100 total balls faced, 5 matches played, and at least 3 distinct pressure matches.
- **Bowlers**: Minimum 24 legal balls (4 overs) bowled under high pressure, 80 total legal balls, 5 matches, and at least 3 distinct pressure matches.
""")

st.markdown("---")

st.markdown("### 8. Analytical Limitations & Edge Cases")

st.markdown("""
1. **DLS Shortened Innings**: Shortened matches have fewer total balls. Handled via `first_inn_revised_overs` and `revised_target` in the matches dataset.
2. **Extreme Tails**: Run chases needing 50 off 6 balls have technically infinite required run rate; capped gracefully via the logistic sigmoid.
3. **Extras Attribution**: Wides and no-balls are not counted as legal deliveries faced or bowled, but runs are charged to bowler and team score.
4. **Super Overs**: Separate mini-matches with unique mechanics; analyzed separately from 20-over totals.
""")

st.markdown("---")
st.markdown("### 📥 Official Report Downloads & PDF Generator")
col_m1, col_m2 = st.columns(2)
master_pdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "Rajasthan_Royals_IPL_2027_Master_Intelligence_Report.pdf")

with col_m1:
    if os.path.exists(master_pdf_path):
        with open(master_pdf_path, "rb") as f:
            st.download_button(
                label="📄 Download Master Methodology & Auction PDF (with Charts)",
                data=f.read(),
                file_name="Rajasthan_Royals_IPL_2027_Master_Intelligence_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

with col_m2:
    if st.button("⚡ Re-Generate Master PDF Report", use_container_width=True):
        with st.spinner("Compiling charts and generating 8-page PDF..."):
            try:
                from scripts.generate_master_report_pdf import generate_master_report
                generate_master_report()
                st.success("Report successfully generated!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")


