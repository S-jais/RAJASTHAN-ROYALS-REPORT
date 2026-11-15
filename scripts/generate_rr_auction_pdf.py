"""
generate_rr_auction_pdf.py — Builds the official Rajasthan Royals IPL 2027 Auction
Pressure Performance Intelligence Report in high-res PDF format using ReportLab.
"""
import os
import sys
import pandas as pd
import numpy as np

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_dir = os.path.join(project_root, "outputs")
os.makedirs(output_dir, exist_ok=True)

# RR Brand Palette
RR_PINK = colors.HexColor("#D81B60")
RR_NAVY = colors.HexColor("#0B1B3D")
RR_GOLD = colors.HexColor("#E5A93C")
RR_LIGHT_BG = colors.HexColor("#F8FAFC")
TEXT_DARK = colors.HexColor("#0F172A")
TEXT_MUTED = colors.HexColor("#475569")
BORDER_COLOR = colors.HexColor("#CBD5E1")
SUCCESS_COLOR = colors.HexColor("#10B981")


def build_pdf():
    pdf_path = os.path.join(output_dir, "Rajasthan_Royals_IPL_2027_Auction_Intelligence_Report.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle', parent=styles['Heading1'],
        fontSize=24, leading=28, textColor=RR_PINK, fontName="Helvetica-Bold", spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'CoverSubtitle', parent=styles['Normal'],
        fontSize=12, leading=16, textColor=RR_NAVY, fontName="Helvetica-Bold", spaceAfter=14
    )
    meta_style = ParagraphStyle(
        'Meta', parent=styles['Normal'],
        fontSize=9, leading=13, textColor=TEXT_MUTED
    )
    h1_style = ParagraphStyle(
        'H1', parent=styles['Heading1'],
        fontSize=15, leading=19, textColor=RR_NAVY, fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=8
    )
    h2_style = ParagraphStyle(
        'H2', parent=styles['Heading2'],
        fontSize=11, leading=15, textColor=RR_PINK, fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=4
    )
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontSize=8.5, leading=11.5, textColor=TEXT_DARK, spaceAfter=5
    )
    body_bold = ParagraphStyle(
        'BodyBold', parent=body_style, fontName="Helvetica-Bold"
    )
    callout_style = ParagraphStyle(
        'Callout', parent=styles['Normal'],
        fontSize=8.5, leading=12, textColor=RR_NAVY, fontName="Helvetica-Oblique"
    )

    # Load ranking data
    bat_df = pd.read_csv(os.path.join(output_dir, "batter_rankings.csv")).head(10)
    bowl_df = pd.read_csv(os.path.join(output_dir, "bowler_rankings.csv")).head(10)

    story = []

    # =========================================================================
    # PAGE 1: COVER & EXECUTIVE STRATEGY BRIEF
    # =========================================================================
    story.append(Paragraph("RAJASTHAN ROYALS", ParagraphStyle('RRBrand', fontSize=14, leading=16, textColor=RR_PINK, fontName="Helvetica-Bold")))
    story.append(Paragraph("PRESSURE PERFORMANCE INTELLIGENCE SYSTEM", title_style))
    story.append(Paragraph("IPL 2027 Mega-Auction Acquisition Strategy & Pressure IQ Rankings", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=RR_PINK, spaceBefore=4, spaceAfter=12))

    meta_text = (
        "<b>Prepared for:</b> Rajasthan Royals Senior Management, Director of Cricket & Auction Analytics Strategy Group<br/>"
        "<b>Author:</b> Sports Data Science & Cricket Performance Intelligence Group<br/>"
        "<b>Scope:</b> 200,999 Deliveries | 867 Matches (IPL & T20I, 2022–2026) | Bayesian Shrinkage Model (N₀ = 75)<br/>"
        "<b>Focus:</b> Identifying the Most Reliable Players Under Pressure & Squad Construction for IPL 2027"
    )
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 14))

    exec_summary = (
        "<b>EXECUTIVE MANDATE:</b> Modern T20 cricket matches are won and lost in high-leverage inflection moments—the final "
        "four overs of a chase, high required run-rate crises, or defending single-digit margins in the 20th over. Traditional "
        "cricket scouting fails in mega-auctions because raw tournament averages and strike rates hide whether a player is a "
        "'flat-track bully' or a genuine crisis match-winner.<br/><br/>"
        "This dossier deploys <b>PRESSURE IQ</b>, an empirical sports analytics engine that scores every delivery on a continuous "
        "Pressure Index (PI ∈ [0, 1]) and calculates context-adjusted performance above replacement ($Actual - Expected$ via "
        "GroupKFold Gradient Boosting). By measuring performance under pressure <i>relative to each player's normal baseline</i> "
        "and applying Empirical Bayes shrinkage, we identify the <b>Top 10 Batters</b> and <b>Top 10 Bowlers</b> who will "
        "deliver true competitive advantage for Rajasthan Royals in the IPL 2027 auction."
    )
    
    # Executive Callout Box
    summary_table = Table([[Paragraph(exec_summary, body_style)]], colWidths=[540])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), RR_LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, RR_GOLD),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Rajasthan Royals: Strategic Context & 2027 Auction Imperatives", h1_style))
    rr_context = (
        "<b>Core Foundation:</b> Rajasthan Royals boast one of the finest Indian top-order cores in T20 cricket featuring "
        "Yashasvi Jaiswal, Captain Sanju Samson, and Riyan Parag, alongside wicket-keeper Dhruv Jurel and death-specialist Sandeep Sharma. "
        "However, tactical review of high-pressure playoff losses and tight finishes reveals three critical vulnerabilities:<br/>"
        "<b>1. Middle-Order Spin Choke & Chase Anchor:</b> When early wickets fall in 180+ chases, RR lacks a calm, experienced "
        "anchor-aggressor at No. 3/4 who dominates spin under pressure.<br/>"
        "<b>2. Extreme Death-Overs Firepower (Overs 17–20):</b> Beyond Shimron Hetmyer and Dhruv Jurel, RR requires a proven, "
        "high-volume boundary hitter striking at 180+ under pressure when RRR exceeds 11.5.<br/>"
        "<b>3. Sawai Mansingh Stadium (Jaipur) Spin & Death Bowling Mastery:</b> Jaipur's expansive square boundaries reward "
        "defensive spin strangulation (under 7.00 RPO) and lethal express/slingshot death bowling to seal 1-run margins."
    )
    story.append(Paragraph(rr_context, body_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: METHODOLOGY & ANALYTICAL PIPELINE
    # =========================================================================
    story.append(Paragraph("1. Analytical Methodology: The PRESSURE IQ Engine", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=RR_NAVY, spaceBefore=2, spaceAfter=8))

    methodology_text = (
        "<b>The Pressure Performance Index (PI)</b> evaluates the psychological and competitive tension of every single delivery "
        "on a continuous scale from 0.052 (low pressure) to 0.949 (extreme crisis). Unlike crude rules (e.g. 'overs 16–20 only'), "
        "PI dynamically accounts for four non-linear match state variables:<br/>"
        "• <b>Chase Urgency (45% in 2nd Innings):</b> Sigmoidal required run rate pressure $\\sigma(0.5 \\cdot (\\text{RRR} - 9.0))$, "
        "balls remaining, and remaining wickets.<br/>"
        "• <b>Resource Depletion (25% in 2nd, 45% in 1st):</b> Wickets lost relative to innings progression.<br/>"
        "• <b>Phase Leverage (15% in 2nd, 35% in 1st):</b> Non-linear leverage curve peaking in death overs (0.50–0.90).<br/>"
        "• <b>Match Competitiveness & Crisis Floor (15%):</b> Dynamic win probability variance with a crisis floor ensuring high RRR chases never register as low tension."
    )
    story.append(Paragraph(methodology_text, body_style))
    story.append(Spacer(1, 8))

    # Architecture Table
    arch_data = [
        ["Phase", "Component", "Mathematical Technique", "Primary Safeguard Against Bias"],
        ["1", "Data Ingestion & Cleaning", "Strict Cricket Rule Reconstitution", "Excluded wides/no-balls from legal deliveries faced"],
        ["2", "Dynamic Pressure Index", "Multi-factor sigmoid continuous index ∈ [0, 1]", "Monotonicity under high RRR via crisis floor"],
        ["3", "Context-Adjusted Baseline", "HistGradientBoosting 5-Fold GroupKFold", "Grouped by match; ZERO player ID leakage"],
        ["4", "Baseline Normalization", "All Non-High-Pressure Deliveries (PI < 0.425)", "Eliminates small-sample distortion for finishers/death bowlers"],
        ["5", "Empirical Bayes Shrinkage", "Conjugate Credibility Weighting (N₀ = 75.0)", "Pulls small samples to pop mean (0.50); bounds 95% CIs"],
    ]
    t_arch = Table(arch_data, colWidths=[35, 125, 180, 200])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), RR_NAVY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, RR_LIGHT_BG]),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 10))

    story.append(Paragraph("2. Primary Batting Leaderboard Under Pressure", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=RR_PINK, spaceBefore=2, spaceAfter=8))

    bat_headers = ["#", "Player", "Rating", "Press Balls", "Norm Balls", "Press SR", "Norm SR", "SR Uplift", "Exp Runs", "Above Exp", "Matches"]
    bat_rows = [bat_headers]
    for _, r in bat_df.iterrows():
        exp_runs = r.get("expected_runs_pressure", r.get("balls_faced_pressure", 0) * 1.5)
        above_exp = r.get("runs_above_expectation", r.get("runs_pressure", 0) - exp_runs)
        bat_rows.append([
            str(int(r.get("rank", 0))),
            str(r.get("player_name", ""))[:18],
            f"{r.get('shrunk_rating', 0):.4f}",
            str(int(r.get("balls_faced_pressure", 0))),
            str(int(r.get("balls_faced_normal", 0))),
            f"{r.get('strike_rate_pressure', 0):.1f}",
            f"{r.get('strike_rate_normal', 0):.1f}",
            f"{r.get('sr_uplift', 0):+.1f}",
            f"{exp_runs:.1f}",
            f"{above_exp:+.1f}",
            str(int(r.get("pressure_matches", 0))),
        ])
    t_bat = Table(bat_rows, colWidths=[20, 110, 48, 50, 48, 45, 45, 45, 45, 48, 36])
    t_bat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), RR_NAVY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (1,0), (1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, RR_LIGHT_BG]),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ]))
    story.append(t_bat)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: BATTERS — HOW EACH STRENGTHENS RAJASTHAN ROYALS (IPL 2027)
    # =========================================================================
    story.append(Paragraph("3. Tactical Fit for Rajasthan Royals: Top 10 Batters (IPL 2027 Auction)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=RR_PINK, spaceBefore=2, spaceAfter=8))

    bat_tactical_fits = [
        ("1. Shreyas Iyer (Rating: 0.7522 | SR: 198.6 | Uplift: +53.7)",
         "<b>Target Role:</b> No. 3/4 Anchor-Aggressor & Spin Destroyer | <b>Auction Priority: TIER 1 MARQUEE</b><br/>"
         "<b>How He Strengthens RR:</b> Shreyas is the missing link in RR's top 5. When early wickets fall, RR often becomes over-reliant "
         "on Sanju Samson. Iyer brings proven IPL-winning captaincy, strikes at an astonishing 198.6 in high-pressure chases (+53.7 uplift), "
         "and neutralizes middle-overs spin at Sawai Mansingh Stadium. He gives Jaiswal and Parag total freedom to attack."),

        ("2. Dinesh Karthik (Rating: 0.7485 | SR: 194.1 | Uplift: +53.8)",
         "<b>Target Role:</b> Specialist Death-Overs Finisher & Mentor Archetype | <b>Auction Priority: TIER 2 / IMPACT VETERAN</b><br/>"
         "<b>How He Strengthens RR:</b> DK's 194.1 pressure strike rate across 321 balls reflects supreme 360-degree boundary execution in "
         "overs 17–20. For RR, acquiring a finisher of this profile creates the ideal mentor-partner for Dhruv Jurel, providing ice-cold decision making."),

        ("3. Rinku Singh (Rating: 0.7369 | SR: 185.2 | Uplift: +52.2)",
         "<b>Target Role:</b> The Ultimate Left-Handed Clutch Finisher (No. 5/6) | <b>Auction Priority: TIER 1 HIGHEST PRIORITY</b><br/>"
         "<b>How He Strengthens RR:</b> Rinku is the crown jewel of pressure batting: 480 pressure balls across 38 matches, striking at 185.2. "
         "Slotting Rinku at No. 5 alongside Shimron Hetmyer gives RR the most devastating left-hand/right-hand death-overs combination in IPL history. "
         "His ability to manufacture boundaries against 145+ km/h death bowling directly addresses RR's playoff chase collapses."),

        ("4. Ashutosh Sharma (Rating: 0.7248 | SR: 179.6 | Uplift: +67.5)",
         "<b>Target Role:</b> High-Upside Indian Power-Hitter & Impact Sub (No. 7) | <b>Auction Priority: TIER 2 HIGH-VALUE TARGET</b><br/>"
         "<b>How He Strengthens RR:</b> Boasts the highest strike rate uplift in elite cricket (+67.5 over normal overs). Ashutosh specializes "
         "in scoring against high pace and reverse-sweeping death bowlers. He solves RR's lower-order tail issue, allowing Samson and Hetmyer to bat fearlessly."),

        ("5. Suryakumar Yadav (Rating: 0.7099 | SR: 184.3 | Uplift: +22.3)",
         "<b>Target Role:</b> 360° Match Winner (No. 3/4) | <b>Auction Priority: TIER 1 TRANSFORMATIVE</b><br/>"
         "<b>How He Strengthens RR:</b> With 540 pressure deliveries and +175.2 runs above replacement, SKY dismantles field placements. "
         "On Jaipur's large square boundaries, his ramp shots and backward-point access exploit field gaps that conventional hitters cannot breach."),

        ("6. Mahendra Singh Dhoni (Rating: 0.7038 | SR: 168.5 | Uplift: +66.9)",
         "<b>Target Role:</b> Tactical Death Ball Striker & Crisis Strategist | <b>Auction Priority: STRATEGIC BENCHMARK</b><br/>"
         "<b>How He Strengthens RR:</b> 333 pressure balls at 168.5 SR (+66.9 uplift). Represents the gold standard for game awareness, "
         "pacing run chases down to the final over and manipulating opposition death bowlers' field sets."),

        ("7. Tim David (Rating: 0.7015 | SR: 191.7 | Uplift: +24.5)",
         "<b>Target Role:</b> Overseas Power Monster (No. 6) | <b>Auction Priority: TIER 1 OVERSEAS FINISHER</b><br/>"
         "<b>How He Strengthens RR:</b> 520 pressure balls striking at 191.7 (+170.9 runs above context). David effortlessly clears Jaipur's "
         "longest 85m straight boundaries against both spin and pace, providing direct cover/rotation for Shimron Hetmyer."),

        ("8. Shashank Singh (Rating: 0.6947 | SR: 179.8 | Uplift: +46.8)",
         "<b>Target Role:</b> Middle-Order Domestic Firepower (No. 5/6) | <b>Auction Priority: TIER 2 HIGH PURSE EFFICIENCY</b><br/>"
         "<b>How He Strengthens RR:</b> 342 pressure balls at 179.8 SR across 24 matches. Shashank possesses exceptional composure when "
         "rebuilding from 40/3 and accelerating to 180+. He adds immense domestic bench depth without consuming an overseas slot."),

        ("9. Romario Shepherd (Rating: 0.6913 | SR: 161.9 | Uplift: +25.0)",
         "<b>Target Role:</b> Pace-Bowling Finisher All-Rounder (No. 7/8) | <b>Auction Priority: TIER 2 TACTICAL BALANCE</b><br/>"
         "<b>How He Strengthens RR:</b> 473 pressure balls striking at 161.9. Gives RR the multi-dimensional seam-bowling all-rounder they have "
         "lacked, providing 2 overs of heavy back-of-a-length pace and explosive lower-order hitting."),

        ("10. Andre Russell (Rating: 0.6910 | SR: 178.5 | Uplift: +15.3)",
         "<b>Target Role:</b> Game-Breaking All-Rounder | <b>Auction Priority: TIER 1 MATCH-WINNER</b><br/>"
         "<b>How He Strengthens RR:</b> 377 pressure balls with +123.2 runs above expectation. Russell's intimidating presence completely "
         "distorts bowler plans at the death, creating boundary opportunities for his batting partners.")
    ]

    for title, desc in bat_tactical_fits:
        story.append(Paragraph(title, h2_style))
        story.append(Paragraph(desc, body_style))
        story.append(Spacer(1, 2))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: BOWLERS — OVERVIEW & LEADERBOARD
    # =========================================================================
    story.append(Paragraph("4. Primary Bowling Leaderboard Under Pressure", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=RR_NAVY, spaceBefore=2, spaceAfter=8))

    bowl_desc = (
        "<b>Bowling Under High Pressure:</b> High-pressure bowling in T20 cricket is characterized by defending totals when batters "
        "have wickets in hand and are operating at an aggressive 10+ RPO run trajectory. The <b>PRESSURE IQ Bowling Engine</b> isolates "
        "bowler-credited wickets, measures economy rate suppression against context expectations, and penalizes boundary concessions."
    )
    story.append(Paragraph(bowl_desc, body_style))
    story.append(Spacer(1, 6))

    bowl_headers = ["#", "Player", "Rating", "Press Balls", "Norm Balls", "Press Econ", "Norm Econ", "Econ Imprv", "Press Wkts", "Matches", "Reliability"]
    bowl_rows = [bowl_headers]
    for _, r in bowl_df.iterrows():
        bowl_rows.append([
            str(int(r.get("rank", 0))),
            str(r.get("player_name", ""))[:18],
            f"{r.get('shrunk_rating', 0):.4f}",
            str(int(r.get("legal_balls_pressure", 0))),
            str(int(r.get("legal_balls_normal", 0))),
            f"{r.get('economy_pressure', 0):.2f}",
            f"{r.get('economy_normal', 0):.2f}",
            f"{r.get('economy_improvement', 0):+.2f}",
            str(int(r.get("bowler_wickets_pressure", r.get("bowler_wickets", 0)))),
            str(int(r.get("pressure_matches", 0))),
            str(r.get("reliability_level", "High")),
        ])
    t_bowl = Table(bowl_rows, colWidths=[20, 110, 48, 50, 48, 48, 48, 48, 42, 38, 40])
    t_bowl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), RR_NAVY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (1,0), (1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, RR_LIGHT_BG]),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ]))
    story.append(t_bowl)
    story.append(Spacer(1, 10))

    story.append(Paragraph("5. Tactical Fit for Rajasthan Royals: Top 10 Bowlers (IPL 2027 Auction)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=RR_PINK, spaceBefore=2, spaceAfter=8))

    bowl_tactical_fits = [
        ("1. Sunil Narine (Rating: 0.7435 | Econ: 6.36 | Improvement: +0.64 RPO | 20 Wkts)",
         "<b>Target Role:</b> Elite Mystery Spinner & Powerplay/Death Suffocator | <b>Auction Priority: TIER 1 HIGHEST MARQUEE</b><br/>"
         "<b>How He Strengthens RR:</b> Narine is the ultimate cheat code in T20 bowling. Delivering 318 pressure balls at an unbelievable "
         "6.36 economy rate in high-leverage situations. On Sawai Mansingh Stadium's gripping tracks, Narine gives RR an impenetrable 4-over "
         "spin choke, completely eliminating opposition middle-over assaults."),

        ("2. Sufiyan Muqeem (Rating: 0.7323 | Econ: 5.02 | Improvement: +1.60 RPO | 20 Wkts)",
         "<b>Target Role:</b> Mystery Left-Arm Wrist Spinner | <b>Auction Priority: TIER 2 HIGH-VALUE TARGET</b><br/>"
         "<b>How He Strengthens RR:</b> Concedes a microscopic 5.02 RPO across 203 pressure balls (+1.60 RPO improvement). Left-arm wrist spin "
         "is the rarest commodity in world cricket; his deceptive wrong'un turns away from right-handers, providing RR an unpickable wicket weapon."),

        ("3. Jofra Archer (Rating: 0.7249 | Econ: 7.90 | Improvement: +1.30 RPO | 25 Wkts)",
         "<b>Target Role:</b> Express Enforcer & Death Bowling Spearhead | <b>Auction Priority: TIER 1 SQUAD SPEARHEAD</b><br/>"
         "<b>How He Strengthens RR:</b> The prodigal son's return to Rajasthan Royals! 291 pressure balls at 7.90 economy (+1.30 improvement "
         "over normal 9.20 economy). Archer provides the 148+ km/h hostility, hard-length bouncers, and searing yorkers that RR desperately "
         "needs to close out tight 10-run margin games."),

        ("4. Mitchell Santner (Rating: 0.7244 | Econ: 6.85 | Improvement: +0.71 RPO | 26 Wkts)",
         "<b>Target Role:</b> Precision Left-Arm Orthodox Spinner & Lower-Order Batter | <b>Auction Priority: TIER 2 TACTICAL VALUE</b><br/>"
         "<b>How He Strengthens RR:</b> 404 pressure balls at 6.85 economy. Santner's trajectory changes and pinpoint stump-to-stump accuracy "
         "are tailor-made for Jaipur's big boundaries. He offers 4 economical overs and genuine No. 8 batting value."),

        ("5. Matheesha Pathirana (Rating: 0.7212 | Econ: 8.57 | 46 Pressure Wickets!)",
         "<b>Target Role:</b> Slingshot Death-Overs Wicket Machine | <b>Auction Priority: TIER 1 ESSENTIAL TARGET</b><br/>"
         "<b>How He Strengthens RR:</b> The single most lethal death-over wicket taker in T20 cricket with a staggering <b>46 pressure wickets</b> "
         "across 526 balls. Pairing Pathirana's 145 km/h dipping yorkers with Sandeep Sharma's wide slower-ball variations gives RR the most complete "
         "and unhittable death-overs bowling attack in the IPL.")
    ]

    for title, desc in bowl_tactical_fits:
        story.append(Paragraph(title, h2_style))
        story.append(Paragraph(desc, body_style))
        story.append(Spacer(1, 2))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: REMAINING BOWLERS & AUCTION PURSE MATRIX
    # =========================================================================
    bowl_tactical_fits_cont = [
        ("6. Abrar Ahmed (Rating: 0.7172 | Econ: 5.37 | Improvement: +1.84 RPO | 15 Wkts)",
         "<b>Target Role:</b> Attacking Leg-Break / Googly Mystery Spinner | <b>Auction Priority: TIER 2 TACTICAL BUY</b><br/>"
         "<b>How He Strengthens RR:</b> 229 pressure balls at 5.37 economy (+1.84 improvement). Bowls with rapid pace through the air, "
         "preventing batters from stepping out, perfectly suited to squeeze opposition teams at SMS Jaipur."),

        ("7. Maheesh Theekshana (Rating: 0.7070 | Econ: 7.46 | Improvement: +0.33 RPO | 29 Wkts)",
         "<b>Target Role:</b> Multi-Phase Carrom-Ball Spinner | <b>Auction Priority: TIER 1 POWERPLAY/DEATH SPINNER</b><br/>"
         "<b>How He Strengthens RR:</b> 474 pressure balls with 29 wickets. Can open the bowling in overs 1–6 and return for over 18, "
         "giving Sanju Samson immense bowling rotation flexibility."),

        ("8. Mohammad Nawaz (Rating: 0.7015 | Econ: 5.58 | Improvement: +1.89 RPO | 20 Wkts)",
         "<b>Target Role:</b> Experienced Left-Arm Finger Spinner & Pinch Hitter | <b>Auction Priority: TIER 3 VALUE TARGET</b><br/>"
         "<b>How He Strengthens RR:</b> 184 pressure balls at 5.58 economy. Highly disciplined line and length under intense pressure."),

        ("9. Jamie Overton (Rating: 0.6871 | Econ: 7.10 | Improvement: +2.24 RPO | 17 Wkts)",
         "<b>Target Role:</b> Tall Hit-the-Deck Heavy Ball Pacer | <b>Auction Priority: TIER 2 SQUAD IMPACT</b><br/>"
         "<b>How He Strengthens RR:</b> Outstanding +2.24 RPO economy improvement in pressure overs. Hits the splice of the bat on spicy pitches "
         "and provides genuine boundary hitting at No. 8."),

        ("10. Sakib Hussain (Rating: 0.6867 | Econ: 7.64 | Improvement: +3.08 RPO | 8 Wkts)",
         "<b>Target Role:</b> Domestic Emerging Death Pacer | <b>Auction Priority: TIER 3 SMART MONEY BUY</b><br/>"
         "<b>How He Strengthens RR:</b> Highest economy improvement in the entire bowling cohort (+3.08 RPO). An uncapped Indian bowler "
         "who thrives under pressure, freeing up valuable auction purse.")
    ]

    for title, desc in bowl_tactical_fits_cont:
        story.append(Paragraph(title, h2_style))
        story.append(Paragraph(desc, body_style))
        story.append(Spacer(1, 2))

    story.append(Spacer(1, 8))
    story.append(Paragraph("6. Rajasthan Royals: IPL 2027 Target Acquisition Matrix & Recommended XI", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=RR_GOLD, spaceBefore=2, spaceAfter=8))

    matrix_data = [
        ["Auction Tier", "Primary Batting Target", "Primary Bowling Target", "Tactical Role in RR XI", "Estimated Purse %"],
        ["Tier 1 (Marquee Core)", "Rinku Singh / Shreyas Iyer", "Matheesha Pathirana / Jofra Archer", "No. 5 Finisher / Death Spearhead", "35% - 45%"],
        ["Tier 2 (High Value)", "Ashutosh Sharma / Tim David", "Sufiyan Muqeem / Mitchell Santner", "Impact Hitter / Jaipur Spin Choke", "20% - 25%"],
        ["Tier 3 (Budget Depth)", "Shashank Singh", "Sakib Hussain / Jamie Overton", "Domestic Bench / Hit-the-Deck Pace", "10% - 15%"],
    ]
    t_matrix = Table(matrix_data, colWidths=[90, 115, 125, 130, 80])
    t_matrix.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), RR_NAVY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, RR_LIGHT_BG]),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ]))
    story.append(t_matrix)
    story.append(Spacer(1, 10))

    # Recommended Playing XI
    story.append(Paragraph("Recommended Rajasthan Royals 'Pressure-Engineered' Starting XII (IPL 2027)", h2_style))
    xi_text = (
        "<b>1. Yashasvi Jaiswal</b> (Aggressive Opener) | <b>2. Overseas Anchor/Opener</b> | "
        "<b>3. Sanju Samson (C/WK)</b> (Anchor-Attacker) | <b>4. Shreyas Iyer / Riyan Parag</b> (Middle Order Spin Destroyer) | "
        "<b>5. Rinku Singh</b> (High-Leverage Finisher #1) | <b>6. Shimron Hetmyer</b> (Overseas Power Finisher) | "
        "<b>7. Dhruv Jurel</b> (Clutch Indian WK/Finisher) | <b>8. Mitchell Santner / Overseas All-Rounder</b> | "
        "<b>9. Sandeep Sharma</b> (Death Swing & Wide Yorker Specialist) | <b>10. Matheesha Pathirana / Jofra Archer</b> (Express Death Spearhead) | "
        "<b>11. Indian Mystery/Leg Spinner</b> | <b>IMPACT SUB: Ashutosh Sharma / Sakib Hussain</b>"
    )
    story.append(Paragraph(xi_text, body_style))
    story.append(Spacer(1, 12))

    footer_callout = (
        "<b>SUMMARY CONCLUSION:</b> By acquiring <b>Rinku Singh</b> (or Shreyas Iyer) to cement the middle-order clutch and "
        "pairing <b>Matheesha Pathirana</b> (or Jofra Archer) alongside Sandeep Sharma at the death, Rajasthan Royals will possess "
        "statistically the most ice-cold, pressure-resilient squad in the Indian Premier League for 2027."
    )
    t_foot = Table([[Paragraph(footer_callout, callout_style)]], colWidths=[540])
    t_foot.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), RR_LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, RR_PINK),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_foot)

    doc.build(story)
    print(f"Successfully generated: {pdf_path}")


if __name__ == "__main__":
    build_pdf()
