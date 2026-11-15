# RAJASTHAN ROYALS — PRESSURE PERFORMANCE INTELLIGENCE REPORT
## IPL 2027 Mega-Auction Acquisition Strategy & Squad Optimization

**Project:** SupeRR Selector Season 2  
**Target Organization:** Rajasthan Royals (RR) Management, Director of Cricket & Auction Strategy Group  
**Dataset Scope:** 200,999 Deliveries | 867 Matches (IPL & T20I, 2022–2026)  
**System Name:** PRESSURE IQ  

---

## 1. Executive Summary & Rajasthan Royals Strategic Imperatives

Modern T20 championships are decided in high-leverage inflection overs—chasing 40 off 18 balls, breaking partnerships in the 17th over, or defending single-digit margins in the 20th over. Traditional cricket scouting during IPL mega-auctions frequently falters because raw tournament statistics (overall averages, flat-track strike rates) mask whether a player thrives under extreme pressure or collapses when the game is on the line.

To solve this for **Rajasthan Royals**, we engineered **PRESSURE IQ**: an empirical intelligence system that models every delivery on a continuous **Pressure Index (PI $\in [0, 1]$)** and measures performance relative to player baseline and match-context expectations.

### Rajasthan Royals Current Core Foundation & Strategic Vulnerabilities:
- **Existing Strengths:** Yashasvi Jaiswal, Captain Sanju Samson, and Riyan Parag form one of the most explosive top-4 units in T20 cricket. Sandeep Sharma provides exceptional death-over knuckleballs and wide slower balls, while Dhruv Jurel offers a calm finishing presence.
- **Critical Vulnerability 1 (Middle-Order Spin Counter):** Over-reliance on Sanju Samson at No. 3. When early wickets fall chasing 180+, RR needs a calm, proven anchor-aggressor at No. 4 who crushes spin.
- **Critical Vulnerability 2 (High-Volume Death Finisher):** When Shimron Hetmyer or Dhruv Jurel fall early, RR's scoring rate collapses. RR requires an elite finisher striking at 180+ under pressure.
- **Critical Vulnerability 3 (Sawai Mansingh Stadium / Jaipur Mastery):** Jaipur's large 80m+ boundaries reward defensive mystery spin (conceding under 6.50 RPO) and express 145+ km/h death yorkers to defend 1-run margins.

---

## 2. Methodology: How PRESSURE IQ Works

```
  Ball-Level State ──> Dynamic Pressure Index (PI) ──> Context ML Expectation ──> Relative Uplift ──> Empirical Bayes Shrinkage
   [RRR, Wkts, Phase]        [Continuous 0 to 1]          [HistGradientBoosting]      [SR_p - SR_norm]      [N0 = 75.0, Prior = 0.50]
```

1. **Continuous Pressure Index (PI):** Evaluates Chase Urgency (45% in 2nd Innings), Resource Depletion (25% in 2nd, 45% in 1st), Phase Leverage (15% in 2nd, 35% in 1st), and Win-Probability Closeness (15%) with a crisis floor ensuring monotonicity as RRR escalates.
2. **Context-Adjusted ML Benchmark:** Uses out-of-sample `HistGradientBoostingRegressor` with 5-Fold `GroupKFold` grouped by match to calculate expected runs per ball given exact match dynamics without player ID leakage.
3. **Baseline Normalization:** Evaluates players against **all non-pressure balls** ($\text{PI} < 0.425$), curing the small-sample distortion that previously afflicted finishers.
4. **Empirical Bayes Shrinkage:** Applies conjugate credibility weighting $W_i = \frac{N_i}{N_i + 75}$, pulling small samples back to the population prior ($0.5000$) and bounding uncertainty with 95% confidence intervals.

---

## 3. Audited Primary Batting Leaderboard Under Pressure

| Rank | Player ID | Player Name | Pressure Rating | Pressure Balls | Normal Balls | Pressure SR | Normal SR | SR Uplift | Pressure Matches | Reliability |
|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | `3647` | **Shreyas Iyer** | **0.7522** | 287 | 1,578 | **198.6** | 144.9 | **+53.7** | 19 | High |
| **2** | `143` | **Dinesh Karthik** | **0.7485** | 321 | 318 | **194.1** | 140.3 | **+53.8** | 28 | High |
| **3** | `4708` | **Rinku Singh** | **0.7369** | 480 | 804 | **185.2** | 133.0 | **+52.2** | 38 | High |
| **4** | `8101` | **Ashutosh Sharma** | **0.7248** | 280 | 66 | **179.6** | 112.1 | **+67.5** | 22 | High |
| **5** | `1699` | **Suryakumar Yadav** | **0.7099** | 540 | 2,219 | **184.3** | 161.9 | **+22.3** | 33 | High |
| **6** | `8` | **MS Dhoni** | **0.7038** | 333 | 130 | **168.5** | 101.5 | **+66.9** | 26 | High |
| **7** | `6396` | **Tim David** | **0.7015** | 520 | 706 | **191.7** | 167.3 | **+24.5** | 43 | High |
| **8** | `2756` | **Shashank Singh** | **0.6947** | 342 | 218 | **179.8** | 133.0 | **+46.8** | 24 | High |
| **9** | `6726` | **Romario Shepherd** | **0.6913** | 473 | 214 | **161.9** | 136.9 | **+25.0** | 34 | High |
| **10** | `1318` | **Andre Russell** | **0.6910** | 377 | 356 | **178.5** | 163.2 | **+15.3** | 30 | High |

---

## 4. How Each Top 10 Batter Strengthens Rajasthan Royals (IPL 2027)

### 1. Shreyas Iyer (Rating: 0.7522 | Pressure SR: 198.6 | Uplift: +53.7)
- **Target Role:** No. 3/4 Anchor-Aggressor & Spin Counter | **Auction Tier:** TIER 1 MARQUEE
- **Tactical Fit for RR:** Shreyas solves RR's top-order over-dependence on Sanju Samson. In high-pressure chases, Shreyas strikes at a staggering 198.6 (+53.7 uplift over normal overs). He is arguably the finest player of spin in Indian cricket, perfectly countering the middle-overs squeeze at Sawai Mansingh Stadium. Furthermore, he provides championship-winning captaincy support to Samson.

### 2. Dinesh Karthik (Rating: 0.7485 | Pressure SR: 194.1 | Uplift: +53.8)
- **Target Role:** Death Finisher & Strategic Mentor Archetype | **Auction Tier:** TIER 2 / IMPACT VETERAN
- **Tactical Fit for RR:** Across 321 pressure deliveries, DK maintains an elite 194.1 strike rate with +106.8 runs above expectation. Acquiring a finisher of this profile creates the ideal mentor-partner for Dhruv Jurel, providing ice-cold decision making in overs 18–20.

### 3. Rinku Singh (Rating: 0.7369 | Pressure SR: 185.2 | Uplift: +52.2)
- **Target Role:** The Ultimate Clutch Finisher (No. 5/6) | **Auction Tier:** TIER 1 HIGHEST PRIORITY TARGET
- **Tactical Fit for RR:** Rinku is the crown jewel of high-pressure batting in modern cricket. He has faced 480 pressure balls across 38 matches, striking at 185.2 with +131.0 runs above expectation. Slotting Rinku at No. 5 alongside Shimron Hetmyer gives RR the most devastating left-hand/right-hand death-overs combination in IPL history. His ability to hit boundaries against 145+ km/h death bowling directly fixes RR's playoff run chase collapses.

### 4. Ashutosh Sharma (Rating: 0.7248 | Pressure SR: 179.6 | Uplift: +67.5)
- **Target Role:** Indian Power-Hitter & Dynamic Impact Sub (No. 7) | **Auction Tier:** TIER 2 HIGH-VALUE TARGET
- **Tactical Fit for RR:** Ashutosh boasts the highest strike rate uplift in elite cricket (+67.5 SR over normal overs). He specializes in scoring against 145+ km/h pace, scooping and reverse-sweeping elite death bowlers. He solves RR's lower-order tail vulnerability.

### 5. Suryakumar Yadav (Rating: 0.7099 | Pressure SR: 184.3 | Uplift: +22.3)
- **Target Role:** 360° Transformative Match Winner (No. 3/4) | **Auction Tier:** TIER 1 TRANSFORMATIVE
- **Tactical Fit for RR:** With 540 pressure balls and +175.2 runs above replacement, SKY dismantles bowling fields. On Jaipur's expansive square boundaries, his ramp shots and backward-point access exploit field gaps that conventional hitters cannot breach.

### 6. Mahendra Singh Dhoni (Rating: 0.7038 | Pressure SR: 168.5 | Uplift: +66.9)
- **Target Role:** Strategic Benchmark & Crisis Striker | **Auction Tier:** BENCHMARK
- **Tactical Fit for RR:** 333 pressure balls at 168.5 SR (+66.9 uplift). Represents the gold standard for game awareness, pacing chases down to the final over and manipulating opposition death bowlers' field sets.

### 7. Tim David (Rating: 0.7015 | Pressure SR: 191.7 | Uplift: +24.5)
- **Target Role:** Overseas Power Monster (No. 6) | **Auction Tier:** TIER 1 OVERSEAS FINISHER
- **Tactical Fit for RR:** 520 pressure balls striking at 191.7 (+170.9 runs above context). David effortlessly clears Jaipur's 85m straight boundaries against both spin and pace, providing direct cover and tactical rotation for Shimron Hetmyer.

### 8. Shashank Singh (Rating: 0.6947 | Pressure SR: 179.8 | Uplift: +46.8)
- **Target Role:** Middle-Order Domestic Firepower (No. 5/6) | **Auction Tier:** TIER 2 HIGH PURSE EFFICIENCY
- **Tactical Fit for RR:** 342 pressure balls at 179.8 SR across 24 matches. Shashank possesses exceptional composure when rebuilding from 40/3 and accelerating to 180+. He adds immense domestic bench depth without consuming an overseas slot.

### 9. Romario Shepherd (Rating: 0.6913 | Pressure SR: 161.9 | Uplift: +25.0)
- **Target Role:** Fast-Bowling All-Rounder (No. 7/8) | **Auction Tier:** TIER 2 TACTICAL BALANCE
- **Tactical Fit for RR:** 473 pressure balls at 161.9 SR. Gives RR the multi-dimensional seam-bowling all-rounder they have lacked: 2 overs of heavy back-of-a-length pace and explosive lower-order hitting.

### 10. Andre Russell (Rating: 0.6910 | Pressure SR: 178.5 | Uplift: +15.3)
- **Target Role:** Game-Breaking All-Rounder | **Auction Tier:** TIER 1 MATCH-WINNER
- **Tactical Fit for RR:** 377 pressure balls with +123.2 runs above expectation. Russell's intimidating presence completely distorts bowler plans at the death, creating boundary opportunities for his batting partners.

---

## 5. Audited Primary Bowling Leaderboard Under Pressure

| Rank | Bowler ID | Bowler Name | Pressure Rating | Pressure Balls | Normal Balls | Pressure Econ | Normal Econ | Econ Improvement | Pressure Wickets | Reliability |
|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | `781` | **Sunil Narine** | **0.7435** | 318 | 1,212 | **6.36** | 7.00 | **+0.64** | 20 | High |
| **2** | `34485` | **Sufiyan Muqeem** | **0.7323** | 203 | 315 | **5.02** | 6.63 | **+1.60** | 20 | High |
| **3** | `3298` | **Jofra Archer** | **0.7249** | 291 | 970 | **7.90** | 9.20 | **+1.30** | 25 | High |
| **4** | `4101` | **Mitchell Santner** | **0.7244** | 404 | 1,333 | **6.85** | 7.56 | **+0.71** | 26 | High |
| **5** | `8661` | **Matheesha Pathirana** | **0.7212** | 526 | 609 | **8.57** | 8.63 | **+0.06** | **46** | High |
| **6** | `5979` | **Abrar Ahmed** | **0.7172** | 229 | 535 | **5.37** | 7.21 | **+1.84** | 15 | High |
| **7** | `19316` | **Maheesh Theekshana** | **0.7070** | 474 | 1,790 | **7.46** | 7.79 | **+0.33** | 29 | High |
| **8** | `2490` | **Mohammad Nawaz** | **0.7015** | 184 | 820 | **5.58** | 7.47 | **+1.89** | 20 | High |
| **9** | `2382` | **Jamie Overton** | **0.6871** | 169 | 329 | **7.10** | 9.34 | **+2.24** | 17 | High |
| **10** | `35318` | **Sakib Hussain** | **0.6867** | 117 | 136 | **7.64** | 10.72 | **+3.08** | 8 | High |

---

## 6. How Each Top 10 Bowler Strengthens Rajasthan Royals (IPL 2027)

### 1. Sunil Narine (Rating: 0.7435 | Pressure Econ: 6.36 | Improvement: +0.64 RPO | 20 Wkts)
- **Target Role:** Elite Mystery Spinner & Multi-Phase Suffocator | **Auction Tier:** TIER 1 HIGHEST MARQUEE TARGET
- **Tactical Fit for RR:** Narine is the ultimate cheat code in T20 bowling. Delivering 318 pressure balls at an unbelievable 6.36 economy rate in high-leverage situations. On Sawai Mansingh Stadium's gripping tracks, Narine gives RR an impenetrable 4-over spin choke, completely eliminating opposition middle-over assaults.

### 2. Sufiyan Muqeem (Rating: 0.7323 | Pressure Econ: 5.02 | Improvement: +1.60 RPO | 20 Wkts)
- **Target Role:** Mystery Left-Arm Wrist Spinner | **Auction Tier:** TIER 2 HIGH-VALUE TARGET
- **Tactical Fit for RR:** Concedes a microscopic 5.02 RPO across 203 pressure balls (+1.60 RPO improvement). Left-arm wrist spin is the rarest commodity in world cricket; his deceptive wrong'un turns away from right-handers, providing RR an unpickable wicket weapon on turning surfaces.

### 3. Jofra Archer (Rating: 0.7249 | Pressure Econ: 7.90 | Improvement: +1.30 RPO | 25 Wkts)
- **Target Role:** Express Enforcer & Death Spearhead (The Homecoming) | **Auction Tier:** TIER 1 SQUAD SPEARHEAD
- **Tactical Fit for RR:** The prodigal son's return to Rajasthan Royals! 291 pressure balls at 7.90 economy (+1.30 improvement over normal 9.20 economy). Archer provides the 148+ km/h hostility, hard-length bouncers, and searing yorkers that RR desperately needs to close out tight 10-run margin games.

### 4. Mitchell Santner (Rating: 0.7244 | Pressure Econ: 6.85 | Improvement: +0.71 RPO | 26 Wkts)
- **Target Role:** Precision Left-Arm Finger Spinner & Lower-Order Batter | **Auction Tier:** TIER 2 TACTICAL VALUE
- **Tactical Fit for RR:** 404 pressure balls at 6.85 economy. Santner's trajectory changes and pinpoint stump-to-stump accuracy are tailor-made for Jaipur's big boundaries. He offers 4 economical overs and genuine No. 8 batting value.

### 5. Matheesha Pathirana (Rating: 0.7212 | Pressure Econ: 8.57 | 46 PRESSURE WICKETS!)
- **Target Role:** Slingshot Death Wicket Machine | **Auction Tier:** TIER 1 ESSENTIAL TARGET
- **Tactical Fit for RR:** The single most lethal death-over wicket taker in modern T20 cricket with a staggering **46 pressure wickets** across 526 balls. Pairing Pathirana's 145 km/h dipping yorkers with Sandeep Sharma's wide slower-ball variations gives RR the most complete and unhittable death-overs bowling attack in the IPL.

### 6. Abrar Ahmed (Rating: 0.7172 | Pressure Econ: 5.37 | Improvement: +1.84 RPO | 15 Wkts)
- **Target Role:** Attacking Leg-Break / Googly Mystery Spinner | **Auction Tier:** TIER 2 TACTICAL VALUE
- **Tactical Fit for RR:** 229 pressure balls at 5.37 economy (+1.84 improvement). Bowls with rapid pace through the air, preventing batters from stepping out, perfectly suited to squeeze opposition teams at SMS Jaipur.

### 7. Maheesh Theekshana (Rating: 0.7070 | Pressure Econ: 7.46 | Improvement: +0.33 RPO | 29 Wkts)
- **Target Role:** Multi-Phase Carrom-Ball Spinner | **Auction Tier:** TIER 1 POWERPLAY/DEATH SPINNER
- **Tactical Fit for RR:** 474 pressure balls with 29 wickets. Can open the bowling in overs 1–6 and return for over 18, giving Sanju Samson immense bowling rotation flexibility.

### 8. Mohammad Nawaz (Rating: 0.7015 | Pressure Econ: 5.58 | Improvement: +1.89 RPO | 20 Wkts)
- **Target Role:** Experienced Left-Arm Finger Spinner & Pinch Hitter | **Auction Tier:** TIER 3 TACTICAL DEPTH
- **Tactical Fit for RR:** 184 pressure balls at 5.58 economy. Highly disciplined line and length under intense pressure.

### 9. Jamie Overton (Rating: 0.6871 | Pressure Econ: 7.10 | Improvement: +2.24 RPO | 17 Wkts)
- **Target Role:** Tall Hit-the-Deck Heavy Ball Pacer | **Auction Tier:** TIER 2 SQUAD IMPACT
- **Tactical Fit for RR:** Outstanding +2.24 RPO economy improvement in pressure overs. Hits the splice of the bat on spicy pitches and provides genuine boundary hitting at No. 8.

### 10. Sakib Hussain (Rating: 0.6867 | Pressure Econ: 7.64 | Improvement: +3.08 RPO | 8 Wkts)
- **Target Role:** Domestic Emerging Death Pacer | **Auction Tier:** TIER 3 SMART MONEY BUY
- **Tactical Fit for RR:** Highest economy improvement in the entire bowling cohort (+3.08 RPO). An uncapped Indian bowler who thrives under pressure, freeing up valuable auction purse.

---

## 7. Rajasthan Royals Auction Target Priority Matrix & Recommended Starting XII

### Target Priority Matrix for IPL 2027 Auction:
| Auction Tier | Primary Batting Target | Primary Bowling Target | Tactical Role in RR XI | Target Purse Allocation |
|---|---|---|---|:---:|
| **Tier 1 (Marquee Core)** | **Rinku Singh** / **Shreyas Iyer** | **Matheesha Pathirana** / **Jofra Archer** | No. 5 Finisher / 145+ km/h Death Spearhead | **35% – 45%** |
| **Tier 2 (High Value Core)** | **Ashutosh Sharma** / **Tim David** | **Sufiyan Muqeem** / **Mitchell Santner** | Impact Hitter / SMS Jaipur Spin Choke | **20% – 25%** |
| **Tier 3 (Budget Depth)** | **Shashank Singh** | **Sakib Hussain** / **Jamie Overton** | Domestic Middle Order / Heavy Ball Pacer | **10% – 15%** |
| **Unallocated Reserve** | — | — | Tactical In-Auction Bidding Flexibility | **20%** |

### Recommended "Pressure-Engineered" Starting XII (IPL 2027):
```
  1. Yashasvi Jaiswal               (Attacking Indian Opener)
  2. Dynamic Overseas Opener         (Powerplay Enforcer)
  3. Sanju Samson [C / WK]          (Attacking Anchor)
  4. Shreyas Iyer / Riyan Parag     (Middle-Order Spin Destroyer | Rating: 0.7522)
  5. RINKU SINGH                    (Elite High-Leverage Finisher #1 | Rating: 0.7369 | 185.2 SR)
  6. Shimron Hetmyer                (Overseas Power Finisher)
  7. Dhruv Jurel                    (Clutch Indian WK / Finisher)
  8. Mitchell Santner / R. Shepherd (Multi-Phase Bowling All-Rounder | 6.85 Econ)
  9. Sandeep Sharma                 (Death Swing & Wide Yorker Specialist)
 10. MATHEESHA PATHIRANA / JOFRA ARCHER (145+ km/h Express Death Spearhead | 46 Wkts)
 11. Sufiyan Muqeem / Indian Spinner (Jaipur Mystery Spin Choke | 5.02 Econ)
--------------------------------------------------------------------------------------
 IMPACT SUB: Ashutosh Sharma (179.6 Pressure SR, +67.5 Uplift) / Sakib Hussain (+3.08 Econ Imprv)
```

---

## 8. Summary Conclusion

By targeting **Rinku Singh** (or Shreyas Iyer) to cement the middle-to-death overs and securing **Matheesha Pathirana** (or Jofra Archer) to partner Sandeep Sharma at the death, Rajasthan Royals will possess statistically the most pressure-resilient squad in the Indian Premier League for the 2027 season.
