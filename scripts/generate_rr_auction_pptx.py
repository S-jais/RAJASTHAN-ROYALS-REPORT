"""
generate_rr_auction_pptx.py — Generates a 16:9 PowerPoint Presentation
for Rajasthan Royals Management & Auction Strategy Group for the IPL 2027 Auction.
"""
import os
import sys
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_dir = os.path.join(project_root, "outputs")
os.makedirs(output_dir, exist_ok=True)

# RR Colors
COLOR_NAVY = RGBColor(11, 27, 61)       # #0B1B3D
COLOR_DARK = RGBColor(15, 23, 42)       # #0F172A
COLOR_PINK = RGBColor(216, 27, 96)      # #D81B60
COLOR_GOLD = RGBColor(229, 169, 60)     # #E5A93C
COLOR_WHITE = RGBColor(255, 255, 255)   # #FFFFFF
COLOR_GRAY = RGBColor(148, 163, 184)    # #94A3B8
COLOR_CARD = RGBColor(24, 38, 77)       # #18264D
COLOR_LIGHT_BG = RGBColor(248, 250, 252)


def set_bg(slide, prs, color):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = color
    bg.line.fill.background()
    return bg


def add_header(slide, title_text, category_text="RAJASTHAN ROYALS — PRESSURE IQ"):
    # Category tag
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11), Inches(0.3))
    tf_cat = cat_box.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_PINK

    # Title
    t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(11.5), Inches(0.6))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_WHITE


def build_pptx():
    pptx_path = os.path.join(output_dir, "Rajasthan_Royals_IPL_2027_Auction_Strategy.pptx")
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    bat_df = pd.read_csv(os.path.join(output_dir, "batter_rankings.csv")).head(10)
    bowl_df = pd.read_csv(os.path.join(output_dir, "bowler_rankings.csv")).head(10)

    # -------------------------------------------------------------
    # SLIDE 1: Title Slide
    # -------------------------------------------------------------
    slide1 = prs.slides.add_slide(blank_layout)
    set_bg(slide1, prs, COLOR_NAVY)

    # Pink decorative band
    band = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.8), Inches(0.15), Inches(3.8))
    band.fill.solid()
    band.fill.fore_color.rgb = COLOR_PINK
    band.line.fill.background()

    tb = slide1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.2), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "RAJASTHAN ROYALS | ANALYTICS & AUCTION INTELLIGENCE"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_GOLD

    p1 = tf.add_paragraph()
    p1.text = "Pressure Performance Intelligence System"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    p1.space_before = Pt(8)

    p2 = tf.add_paragraph()
    p2.text = "Identifying the Most Reliable Players Under Pressure & Squad Construction for IPL 2027"
    p2.font.size = Pt(18)
    p2.font.color.rgb = COLOR_PINK
    p2.space_before = Pt(10)

    p3 = tf.add_paragraph()
    p3.text = "Dataset: 200,999 Deliveries | 867 Matches (IPL & T20I, 2022–2026) | Empirical Bayes Shrinkage (N₀ = 75)"
    p3.font.size = Pt(11)
    p3.font.color.rgb = COLOR_GRAY
    p3.space_before = Pt(24)

    # -------------------------------------------------------------
    # SLIDE 2: Executive Summary & RR Strategic Context
    # -------------------------------------------------------------
    slide2 = prs.slides.add_slide(blank_layout)
    set_bg(slide2, prs, COLOR_NAVY)
    add_header(slide2, "Executive Mandate & Rajasthan Royals Tactical Imperatives")

    cards_data = [
        ("Current RR Core Strength",
         "• Top Order Anchor & Attack: Yashasvi Jaiswal, Captain Sanju Samson, Riyan Parag.\n"
         "• Death Swing Specialist: Sandeep Sharma.\n"
         "• Emerging Indian WK/Finisher: Dhruv Jurel.\n"
         "• Tactical Baseline: High ceiling, but prone to middle-order spin chokes and death-overs chase collapses."),
        ("Playoff Vulnerabilities Identified",
         "1. Middle-Order Spin Counter: Over-reliance on Sanju Samson; need a calm anchor-aggressor at No. 3/4.\n"
         "2. Extreme Death-Overs Firepower: Lack a second 180+ SR finisher when Hetmyer/Jurel fall early.\n"
         "3. Jaipur SMS Defensive Mastery: Need 145+ km/h express death yorkers and sub-6.50 RPO mystery spin."),
        ("IPL 2027 Auction Objective",
         "• Target players with statistically proven Pressure Uplift over normal baseline.\n"
         "• Eliminate 'flat-track bullies' who inflate tournament averages in low-leverage overs.\n"
         "• Construct an ice-cold, pressure-resilient XI capable of converting 1-run margins into trophies.")
    ]

    for i, (title, content) in enumerate(cards_data):
        card = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i * 3.9), Inches(1.6), Inches(3.7), Inches(5.2))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD
        card.line.color.rgb = COLOR_PINK if i == 1 else COLOR_GOLD if i == 2 else COLOR_GRAY

        tf_c = card.text_frame
        tf_c.word_wrap = True
        p_ct = tf_c.paragraphs[0]
        p_ct.text = title
        p_ct.font.size = Pt(14)
        p_ct.font.bold = True
        p_ct.font.color.rgb = COLOR_WHITE
        p_ct.space_after = Pt(10)

        p_cc = tf_c.add_paragraph()
        p_cc.text = content
        p_cc.font.size = Pt(10.5)
        p_cc.font.color.rgb = COLOR_GRAY

    # -------------------------------------------------------------
    # SLIDE 3: Methodology — The PRESSURE IQ Engine
    # -------------------------------------------------------------
    slide3 = prs.slides.add_slide(blank_layout)
    set_bg(slide3, prs, COLOR_NAVY)
    add_header(slide3, "Methodology: How PRESSURE IQ Measures True Clutch Execution")

    steps = [
        ("1. Ball-by-Ball Pressure Index (PI)",
         "Continuous index ∈ [0, 1] computed for all 200,999 deliveries:\n"
         "• Chase Urgency (45%): Sigmoid RRR pressure σ(0.5·(RRR - 9.0)) + Balls & Wkts remaining.\n"
         "• Resource Depletion (25% 2nd, 45% 1st): Wickets lost relative to innings stage.\n"
         "• Phase Leverage (15% 2nd, 35% 1st): Powerplay (0.25) to Death Overs (0.90).\n"
         "• Crisis Floor (15%): Guarantees tension increases monotonically under steep targets."),
        ("2. Context-Adjusted Expectation ML",
         "Out-of-sample HistGradientBoosting Regressors with 5-Fold GroupKFold by match:\n"
         "• Predicts expected runs per ball given match state WITHOUT player ID leakage.\n"
         "• Isolates situational difficulty from individual execution.\n"
         "• Batting Impact = Actual Runs − Expected Runs\n"
         "• Bowling Impact = Expected Conceded − Actual Conceded"),
        ("3. Normal Baseline & Shrinkage",
         "Curing Small-Sample & Anchor Bias:\n"
         "• Evaluated against ALL non-pressure balls (PI < 0.425), giving finishers 300+ baseline balls.\n"
         "• Relative Uplift: SR_pressure − SR_normal.\n"
         "• Conjugate Empirical Bayes Shrinkage (N₀ = 75.0):\n"
         "  R_shrunk = (N / (N + 75))·R_raw + (75 / (N + 75))·0.50"),
    ]

    for i, (title, content) in enumerate(steps):
        card = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i * 3.9), Inches(1.6), Inches(3.7), Inches(5.2))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD
        card.line.color.rgb = COLOR_PINK if i == 0 else COLOR_GOLD if i == 1 else COLOR_WHITE

        tf_c = card.text_frame
        tf_c.word_wrap = True
        p_ct = tf_c.paragraphs[0]
        p_ct.text = title
        p_ct.font.size = Pt(13)
        p_ct.font.bold = True
        p_ct.font.color.rgb = COLOR_WHITE
        p_ct.space_after = Pt(8)

        p_cc = tf_c.add_paragraph()
        p_cc.text = content
        p_cc.font.size = Pt(9.5)
        p_cc.font.color.rgb = COLOR_GRAY

    # -------------------------------------------------------------
    # SLIDE 4: Top 10 Batters Under Pressure (Table)
    # -------------------------------------------------------------
    slide4 = prs.slides.add_slide(blank_layout)
    set_bg(slide4, prs, COLOR_NAVY)
    add_header(slide4, "Audited Primary Leaderboard: Top 10 Batters Under Pressure")

    rows = 11
    cols = 9
    table_shape = slide4.shapes.add_table(rows, cols, Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.0))
    table = table_shape.table
    table.columns[0].width = Inches(0.6)
    table.columns[1].width = Inches(2.3)
    table.columns[2].width = Inches(1.3)
    table.columns[3].width = Inches(1.2)
    table.columns[4].width = Inches(1.2)
    table.columns[5].width = Inches(1.3)
    table.columns[6].width = Inches(1.3)
    table.columns[7].width = Inches(1.3)
    table.columns[8].width = Inches(1.2)

    headers = ["#", "Player", "Rating", "Press Balls", "Norm Balls", "Press SR", "Norm SR", "SR Uplift", "Matches"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_PINK
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.alignment = PP_ALIGN.CENTER if j != 1 else PP_ALIGN.LEFT

    for i, (_, r) in enumerate(bat_df.iterrows()):
        vals = [
            str(i+1),
            str(r.get("player_name", "")),
            f"{r.get('shrunk_rating', 0):.4f}",
            str(int(r.get("balls_faced_pressure", 0))),
            str(int(r.get("balls_faced_normal", 0))),
            f"{r.get('strike_rate_pressure', 0):.1f}",
            f"{r.get('strike_rate_normal', 0):.1f}",
            f"{r.get('sr_uplift', 0):+.1f}",
            str(int(r.get("pressure_matches", 0)))
        ]
        for j, v in enumerate(vals):
            cell = table.cell(i+1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLOR_CARD if i % 2 == 0 else COLOR_DARK
            p = cell.text_frame.paragraphs[0]
            p.text = v
            p.font.size = Pt(9.5)
            p.font.color.rgb = COLOR_WHITE if j <= 2 else COLOR_GOLD if j == 7 else COLOR_GRAY
            p.alignment = PP_ALIGN.CENTER if j != 1 else PP_ALIGN.LEFT

    # -------------------------------------------------------------
    # SLIDE 5: Batters 1–5: How Each Strengthens Rajasthan Royals
    # -------------------------------------------------------------
    slide5 = prs.slides.add_slide(blank_layout)
    set_bg(slide5, prs, COLOR_NAVY)
    add_header(slide5, "Rajasthan Royals Tactical Fits: Top Batters (Ranks 1–5)")

    b5_data = [
        ("1. SHREYAS IYER (Rating: 0.7522 | SR: 198.6 | Uplift: +53.7)",
         "Role: No. 3/4 Anchor-Aggressor & Spin Destroyer | Tier 1 Marquee Target\n"
         "• Solves RR's top-order over-reliance on Samson; brings proven IPL-winning leadership.\n"
         "• Strikes at 198.6 in high pressure (+53.7 uplift), dominating spin at SMS Jaipur."),

        ("2. DINESH KARTHIK (Rating: 0.7485 | SR: 194.1 | Uplift: +53.8)",
         "Role: Elite Death-Overs Finisher & Mentor Archetype | Tier 2 / Veteran Impact\n"
         "• 321 pressure balls at 194.1 SR with supreme 360-degree boundary execution in overs 17–20.\n"
         "• The ideal finishing partner and strategic mentor for young Dhruv Jurel."),

        ("3. RINKU SINGH (Rating: 0.7369 | SR: 185.2 | Uplift: +52.2)",
         "Role: The Ultimate Clutch Finisher (No. 5/6) | Tier 1 HIGHEST PRIORITY TARGET\n"
         "• Crown jewel of pressure batting: 480 pressure balls across 38 matches striking at 185.2.\n"
         "• Left-handed foil to Shimron Hetmyer; eliminates RR's playoff run chase collapses."),

        ("4. ASHUTOSH SHARMA (Rating: 0.7248 | SR: 179.6 | Uplift: +67.5)",
         "Role: High-Impact Domestic Finisher (No. 7) | Tier 2 High-Value Target\n"
         "• Highest strike rate uplift in elite cricket (+67.5 SR over normal overs).\n"
         "• Specializes in scoring against express pace; provides lethal lower-order muscle."),

        ("5. SURYAKUMAR YADAV (Rating: 0.7099 | SR: 184.3 | Uplift: +22.3)",
         "Role: Transformational 360° Match Winner (No. 3/4) | Tier 1 Transformative\n"
         "• 540 pressure deliveries with +175.2 runs above expectation.\n"
         "• Exploits Jaipur's large square boundaries with ramps and sweeps impossible to defend.")
    ]

    for i, (title, content) in enumerate(b5_data):
        card = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5 + i * 1.15), Inches(11.7), Inches(1.02))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD
        card.line.color.rgb = COLOR_PINK if i == 2 else COLOR_GOLD if i == 0 else COLOR_GRAY

        tf_c = card.text_frame
        tf_c.word_wrap = True
        p_ct = tf_c.paragraphs[0]
        p_ct.text = title
        p_ct.font.size = Pt(11)
        p_ct.font.bold = True
        p_ct.font.color.rgb = COLOR_WHITE

        p_cc = tf_c.add_paragraph()
        p_cc.text = content
        p_cc.font.size = Pt(9)
        p_cc.font.color.rgb = COLOR_GRAY

    # -------------------------------------------------------------
    # SLIDE 6: Batters 6–10: How Each Strengthens Rajasthan Royals
    # -------------------------------------------------------------
    slide6 = prs.slides.add_slide(blank_layout)
    set_bg(slide6, prs, COLOR_NAVY)
    add_header(slide6, "Rajasthan Royals Tactical Fits: Top Batters (Ranks 6–10)")

    b10_data = [
        ("6. MS DHONI (Rating: 0.7038 | SR: 168.5 | Uplift: +66.9)",
         "Role: Tactical Game Awareness & Crisis Striker | Strategic Benchmark\n"
         "• 333 pressure balls at 168.5 SR (+66.9 uplift). Represents gold standard in pacing chases\n"
         "  down to the final 6 balls and manipulating bowler field sets."),

        ("7. TIM DAVID (Rating: 0.7015 | SR: 191.7 | Uplift: +24.5)",
         "Role: Overseas Power Monster (No. 6) | Tier 1 Overseas Finisher\n"
         "• 520 pressure balls striking at 191.7 (+170.9 runs above context expectation).\n"
         "• Effortlessly clears Jaipur's 85m straight boundaries; provides elite cover for Hetmyer."),

        ("8. SHASHANK SINGH (Rating: 0.6947 | SR: 179.8 | Uplift: +46.8)",
         "Role: Middle-Order Domestic Firepower (No. 5/6) | Tier 2 High Purse Efficiency\n"
         "• 342 pressure balls at 179.8 SR across 24 matches. Composure to rebuild from 40/3\n"
         "  and accelerate to 185+, providing vital domestic batting depth."),

        ("9. ROMARIO SHEPHERD (Rating: 0.6913 | SR: 161.9 | Uplift: +25.0)",
         "Role: Fast-Bowling All-Rounder (No. 7/8) | Tier 2 Tactical Balance\n"
         "• 473 pressure balls at 161.9 SR. Gives RR the multi-dimensional seam all-rounder\n"
         "  they lack: 2 overs of heavy pace + explosive lower-order boundary hitting."),

        ("10. ANDRE RUSSELL (Rating: 0.6910 | SR: 178.5 | Uplift: +15.3)",
         "Role: Game-Breaking Match-Winner | Tier 1 Match Winner\n"
         "• 377 pressure balls with +123.2 runs above expectation. Psychological dominance at death\n"
         "  forces opposition captains into defensive errors and extras.")
    ]

    for i, (title, content) in enumerate(b10_data):
        card = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5 + i * 1.15), Inches(11.7), Inches(1.02))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD
        card.line.color.rgb = COLOR_GOLD if i == 1 else COLOR_GRAY

        tf_c = card.text_frame
        tf_c.word_wrap = True
        p_ct = tf_c.paragraphs[0]
        p_ct.text = title
        p_ct.font.size = Pt(11)
        p_ct.font.bold = True
        p_ct.font.color.rgb = COLOR_WHITE

        p_cc = tf_c.add_paragraph()
        p_cc.text = content
        p_cc.font.size = Pt(9)
        p_cc.font.color.rgb = COLOR_GRAY

    # -------------------------------------------------------------
    # SLIDE 7: Top 10 Bowlers Under Pressure (Table)
    # -------------------------------------------------------------
    slide7 = prs.slides.add_slide(blank_layout)
    set_bg(slide7, prs, COLOR_NAVY)
    add_header(slide7, "Audited Primary Leaderboard: Top 10 Bowlers Under Pressure")

    table_shape7 = slide7.shapes.add_table(rows, cols, Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.0))
    table7 = table_shape7.table
    table7.columns[0].width = Inches(0.6)
    table7.columns[1].width = Inches(2.3)
    table7.columns[2].width = Inches(1.3)
    table7.columns[3].width = Inches(1.2)
    table7.columns[4].width = Inches(1.2)
    table7.columns[5].width = Inches(1.3)
    table7.columns[6].width = Inches(1.3)
    table7.columns[7].width = Inches(1.3)
    table7.columns[8].width = Inches(1.2)

    headers_b = ["#", "Player", "Rating", "Press Balls", "Norm Balls", "Press Econ", "Norm Econ", "Econ Imprv", "Wkts"]
    for j, h in enumerate(headers_b):
        cell = table7.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_PINK
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.alignment = PP_ALIGN.CENTER if j != 1 else PP_ALIGN.LEFT

    for i, (_, r) in enumerate(bowl_df.iterrows()):
        vals = [
            str(i+1),
            str(r.get("player_name", "")),
            f"{r.get('shrunk_rating', 0):.4f}",
            str(int(r.get("legal_balls_pressure", 0))),
            str(int(r.get("legal_balls_normal", 0))),
            f"{r.get('economy_pressure', 0):.2f}",
            f"{r.get('economy_normal', 0):.2f}",
            f"{r.get('economy_improvement', 0):+.2f}",
            str(int(r.get("bowler_wickets_pressure", r.get("bowler_wickets", 0))))
        ]
        for j, v in enumerate(vals):
            cell = table7.cell(i+1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLOR_CARD if i % 2 == 0 else COLOR_DARK
            p = cell.text_frame.paragraphs[0]
            p.text = v
            p.font.size = Pt(9.5)
            p.font.color.rgb = COLOR_WHITE if j <= 2 else COLOR_GOLD if j == 7 else COLOR_GRAY
            p.alignment = PP_ALIGN.CENTER if j != 1 else PP_ALIGN.LEFT

    # -------------------------------------------------------------
    # SLIDE 8: Bowlers 1–5: How Each Strengthens Rajasthan Royals
    # -------------------------------------------------------------
    slide8 = prs.slides.add_slide(blank_layout)
    set_bg(slide8, prs, COLOR_NAVY)
    add_header(slide8, "Rajasthan Royals Tactical Fits: Top Bowlers (Ranks 1–5)")

    bw5_data = [
        ("1. SUNIL NARINE (Rating: 0.7435 | Econ: 6.36 | Improvement: +0.64 RPO | 20 Wkts)",
         "Role: Elite Mystery Spinner & Multi-Phase Suffocator | Tier 1 Highest Marquee Target\n"
         "• Concedes an unbelievable 6.36 RPO across 318 pressure balls. On Jaipur's gripping tracks,\n"
         "  Narine gives RR an impenetrable 4-over spin choke, strangling opposition middle overs."),

        ("2. SUFIYAN MUQEEM (Rating: 0.7323 | Econ: 5.02 | Improvement: +1.60 RPO | 20 Wkts)",
         "Role: Left-Arm Wrist Spin Mystery Weapon | Tier 2 High-Value Target\n"
         "• Microscopic 5.02 economy across 203 pressure balls (+1.60 RPO improvement).\n"
         "• Left-arm wrist spin is cricket's rarest commodity; sharp wrong'uns turn away from right-handers."),

        ("3. JOFRA ARCHER (Rating: 0.7249 | Econ: 7.90 | Improvement: +1.30 RPO | 25 Wkts)",
         "Role: Express Enforcer & Death Spearhead | Tier 1 SQUAD SPEARHEAD (Return to RR!)\n"
         "• 291 pressure balls at 7.90 economy (+1.30 improvement over normal 9.20 economy).\n"
         "• Brings the 148+ km/h hostility, hard bouncers, and yorkers RR needs to defend single-digit margins."),

        ("4. MITCHELL SANTNER (Rating: 0.7244 | Econ: 6.85 | Improvement: +0.71 RPO | 26 Wkts)",
         "Role: Precision Finger Spinner & Lower-Order Batter | Tier 2 Tactical Value\n"
         "• 404 pressure balls at 6.85 economy. Trajectory changes and stump-to-stump accuracy are tailor-made\n"
         "  for Jaipur's big boundaries. Also offers genuine No. 8 batting capability."),

        ("5. MATHEESHA PATHIRANA (Rating: 0.7212 | Econ: 8.57 | 46 PRESSURE WICKETS!)",
         "Role: Slingshot Death Wicket Machine | Tier 1 ESSENTIAL TARGET\n"
         "• The most lethal death bowler in modern T20: 46 pressure wickets across 526 balls.\n"
         "• Pairing Pathirana's 145 km/h yorkers with Sandeep Sharma's wide slower-balls creates the IPL's top death duo.")
    ]

    for i, (title, content) in enumerate(bw5_data):
        card = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5 + i * 1.15), Inches(11.7), Inches(1.02))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD
        card.line.color.rgb = COLOR_PINK if i in [2, 4] else COLOR_GOLD if i == 0 else COLOR_GRAY

        tf_c = card.text_frame
        tf_c.word_wrap = True
        p_ct = tf_c.paragraphs[0]
        p_ct.text = title
        p_ct.font.size = Pt(11)
        p_ct.font.bold = True
        p_ct.font.color.rgb = COLOR_WHITE

        p_cc = tf_c.add_paragraph()
        p_cc.text = content
        p_cc.font.size = Pt(9)
        p_cc.font.color.rgb = COLOR_GRAY

    # -------------------------------------------------------------
    # SLIDE 9: Bowlers 6–10: How Each Strengthens Rajasthan Royals
    # -------------------------------------------------------------
    slide9 = prs.slides.add_slide(blank_layout)
    set_bg(slide9, prs, COLOR_NAVY)
    add_header(slide9, "Rajasthan Royals Tactical Fits: Top Bowlers (Ranks 6–10)")

    bw10_data = [
        ("6. ABRAR AHMED (Rating: 0.7172 | Econ: 5.37 | Improvement: +1.84 RPO | 15 Wkts)",
         "Role: Rapid Leg-Break/Googly Specialist | Tier 2 Tactical Value\n"
         "• 229 pressure balls at 5.37 economy (+1.84 improvement). Bowls rapid pace through the air,\n"
         "  preventing batters from stepping out on gripping Jaipur pitches."),

        ("7. MAHEESH THEEKSHANA (Rating: 0.7070 | Econ: 7.46 | Improvement: +0.33 RPO | 29 Wkts)",
         "Role: Multi-Phase Carrom-Ball Spinner | Tier 1 Powerplay/Death Spinner\n"
         "• 474 pressure balls with 29 wickets. Can open the bowling in powerplays (overs 1–6)\n"
         "  and return for over 18, providing unmatched tactical flexibility."),

        ("8. MOHAMMAD NAWAZ (Rating: 0.7015 | Econ: 5.58 | Improvement: +1.89 RPO | 20 Wkts)",
         "Role: Experienced Left-Arm Finger Spinner & Pinch Hitter | Tier 3 Tactical Depth\n"
         "• 184 pressure balls at 5.58 economy. Reliable, repeatable mechanics under intense pressure."),

        ("9. JAMIE OVERTON (Rating: 0.6871 | Econ: 7.10 | Improvement: +2.24 RPO | 17 Wkts)",
         "Role: Tall Hit-the-Deck Heavy Ball Pacer | Tier 2 Squad Impact\n"
         "• Massive +2.24 RPO economy improvement in pressure overs. Attacks the batter's ribs and splice,\n"
         "  plus provides ferocious lower-order hitting power."),

        ("10. SAKIB HUSSAIN (Rating: 0.6867 | Econ: 7.64 | Improvement: +3.08 RPO | 8 Wkts)",
         "Role: Emerging Domestic Death Pacer | Tier 3 Smart Money Buy\n"
         "• Highest economy improvement in the tournament (+3.08 RPO!). An uncapped Indian bowler\n"
         "  who elevates his game under pressure, saving vital auction purse.")
    ]

    for i, (title, content) in enumerate(bw10_data):
        card = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5 + i * 1.15), Inches(11.7), Inches(1.02))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD
        card.line.color.rgb = COLOR_GOLD if i == 4 else COLOR_GRAY

        tf_c = card.text_frame
        tf_c.word_wrap = True
        p_ct = tf_c.paragraphs[0]
        p_ct.text = title
        p_ct.font.size = Pt(11)
        p_ct.font.bold = True
        p_ct.font.color.rgb = COLOR_WHITE

        p_cc = tf_c.add_paragraph()
        p_cc.text = content
        p_cc.font.size = Pt(9)
        p_cc.font.color.rgb = COLOR_GRAY

    # -------------------------------------------------------------
    # SLIDE 10: Auction Purse Allocation & Recommended Starting XII
    # -------------------------------------------------------------
    slide10 = prs.slides.add_slide(blank_layout)
    set_bg(slide10, prs, COLOR_NAVY)
    add_header(slide10, "IPL 2027 Auction Target Priority Matrix & Recommended Starting XII")

    # Target Priority Matrix Card
    card_m = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.7), Inches(5.3))
    card_m.fill.solid()
    card_m.fill.fore_color.rgb = COLOR_CARD
    card_m.line.color.rgb = COLOR_GOLD

    tf_m = card_m.text_frame
    tf_m.word_wrap = True
    p_mt = tf_m.paragraphs[0]
    p_mt.text = "AUCTION PURSE ALLOCATION STRATEGY"
    p_mt.font.size = Pt(13)
    p_mt.font.bold = True
    p_mt.font.color.rgb = COLOR_GOLD

    p_mc = tf_m.add_paragraph()
    p_mc.text = (
        "\n• TIER 1 MARQUEE TARGETS (35% – 45% Purse):\n"
        "  - Batting: Rinku Singh (Highest Priority) or Shreyas Iyer\n"
        "  - Bowling: Matheesha Pathirana or Jofra Archer\n"
        "  - Mission: Lock in one elite death-overs finisher and one express death-bowling spearhead.\n\n"
        "• TIER 2 VALUE CORE (20% – 25% Purse):\n"
        "  - Batting: Ashutosh Sharma / Tim David\n"
        "  - Bowling: Sufiyan Muqeem / Mitchell Santner\n"
        "  - Mission: Jaipur spin choke and dynamic Impact Sub boundary power.\n\n"
        "• TIER 3 BUDGET DEPTH (10% – 15% Purse):\n"
        "  - Batting: Shashank Singh\n"
        "  - Bowling: Sakib Hussain / Jamie Overton\n"
        "  - Mission: High-upside uncapped domestic clutch depth."
    )
    p_mc.font.size = Pt(9.5)
    p_mc.font.color.rgb = COLOR_WHITE

    # Recommended Starting XII Card
    card_xi = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.3))
    card_xi.fill.solid()
    card_xi.fill.fore_color.rgb = COLOR_CARD
    card_xi.line.color.rgb = COLOR_PINK

    tf_xi = card_xi.text_frame
    tf_xi.word_wrap = True
    p_xit = tf_xi.paragraphs[0]
    p_xit.text = "RECOMMENDED 'PRESSURE-ENGINEERED' STARTING XII"
    p_xit.font.size = Pt(13)
    p_xit.font.bold = True
    p_xit.font.color.rgb = COLOR_PINK

    p_xic = tf_xi.add_paragraph()
    p_xic.text = (
        "\n1. Yashasvi Jaiswal (Aggressive Indian Opener)\n"
        "2. Overseas Dynamic Opener\n"
        "3. Sanju Samson (C/WK) (Attacking Anchor)\n"
        "4. Shreyas Iyer / Riyan Parag (Middle Order Spin Neutralizer)\n"
        "5. RINKU SINGH (Elite Pressure Finisher #1 | 185.2 SR)\n"
        "6. Shimron Hetmyer (Overseas Power Finisher)\n"
        "7. Dhruv Jurel (WK / Clutch Indian Finisher)\n"
        "8. Mitchell Santner / Romario Shepherd (All-Rounder)\n"
        "9. Sandeep Sharma (Death Swing & Wide Yorker Specialist)\n"
        "10. MATHEESHA PATHIRANA / JOFRA ARCHER (145+ km/h Death Spearhead)\n"
        "11. Indian Mystery Spinner (Sufiyan Muqeem / Domestic)\n"
        "--------------------------------------------------\n"
        "IMPACT SUB: Ashutosh Sharma (179.6 Pressure SR) / Sakib Hussain"
    )
    p_xic.font.size = Pt(9.5)
    p_xic.font.color.rgb = COLOR_WHITE

    prs.save(pptx_path)
    print(f"Successfully generated: {pptx_path}")


if __name__ == "__main__":
    build_pptx()
