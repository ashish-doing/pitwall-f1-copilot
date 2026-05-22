---
title: PitWall F1 Copilot
emoji: 🏎️
colorFrom: red
colorTo: blue
sdk: gradio
sdk_version: 6.14.0
python_version: "3.10"
app_file: app.py
pinned: false
---

# 🏎️ PitWall — F1 Race Strategy Copilot

<p align="center">
  <img src="https://img.shields.io/badge/IBM%20Granite-4.1%208B-blue?style=for-the-badge&logo=ibm" />
  <img src="https://img.shields.io/badge/Docling-IBM-blue?style=for-the-badge&logo=ibm" />
  <img src="https://img.shields.io/badge/FastF1-Telemetry-red?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Q--Learning-RL%20Agent-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Gradio-UI-yellow?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.10-green?style=for-the-badge&logo=python" />
</p>

<p align="center">
  <strong>IBM SkillsBuild AI Builders Challenge — May 2026 Submission</strong>
</p>

<p align="center">
  <a href="https://huggingface.co/spaces/ashish-doing/pitwall-f1-copilot">🚀 Live Demo</a> •
  <a href="https://github.com/ashish-doing/pitwall-f1-copilot">📁 GitHub</a>
</p>

---

## 🏁 The Problem

F1 race strategy is one of the most complex real-time decision problems in professional sport. Every lap, a team must decide:

- **When to pit** — too early and you give up track position; too late and your tyres fall off the cliff
- **Which compound to switch to** — SOFT for pace, HARD for durability, MEDIUM as a balance
- **How to react** to Safety Cars, Virtual Safety Cars, and competitors' strategies

Top F1 teams spend **millions of dollars** on proprietary strategy software and employ entire departments of data scientists. Independent teams, analysts, students, and fans have **zero access** to these tools.

Meanwhile, F1 publishes real telemetry data via its official API — lap times, tyre compounds, pit stop laps, car speed traces — all publicly available, but requiring significant technical effort to interpret.

**The gap:** Rich data exists. Expert AI tools don't.

---

## 💡 The Solution

**PitWall** is an AI-powered F1 race strategy copilot that bridges this gap. It combines:

- **Real F1 telemetry** from FastF1 (official timing data, 2022–2024 seasons)
- **IBM Granite 4.1 8B** for natural language strategy reasoning and explainability
- **Docling** to parse FIA regulations and inject rule context into Granite prompts
- **A Q-Learning RL agent** trained on 23,400 lap decisions from 5 real F1 races

The result: a three-tab tool that lets anyone — from a curious fan to a motorsport analyst — understand and optimize F1 race strategy using the same data the teams use.

---

## 🤖 AI & Technical Approach

### Architecture Overview

```
FastF1 API (Real Telemetry)
        │
        ▼
┌─────────────────────┐     ┌──────────────────────┐
│  fastf1_loader.py   │     │  docling_parser.py   │
│  - Lap times        │     │  - FIA Regulations   │
│  - Tyre compounds   │     │  - Pit stop rules    │
│  - Pit stop laps    │     │  - Compound rules    │
│  - Driver stints    │     └──────────┬───────────┘
└──────────┬──────────┘                │
           │                           │
           └──────────┬────────────────┘
                      │
                      ▼
           ┌──────────────────────┐
           │   granite_engine.py  │
           │   IBM Granite 4.1 8B │
           │   via OpenRouter API │
           │                      │
           │  Context = Telemetry │
           │         + Regulations│
           └──────────┬───────────┘
                      │
           ┌──────────┴───────────┐
           │                      │
           ▼                      ▼
  Strategy Analysis        Pit Window Advice
  (Tab 1)                  (Tab 2)

                ┌──────────────────────┐
                │    rl_optimizer.py   │
                │    Q-Learning Agent  │
                │    23,400 decisions  │
                │    5 real F1 races   │
                └──────────┬───────────┘
                           │
                           ▼
                    RL Pit Decision
                    + Q-Values
                    + Confidence %
                    (Tab 3)
```

### IBM Technologies Used

#### 1. IBM Granite 4.1 8B
The core reasoning engine. Used in two ways:

**Tab 1 — Race Strategy Analysis:**
Granite receives real telemetry data (lap times, tyre compounds, pit stop laps, best lap) + FIA regulation context from Docling, then generates a 3-paragraph strategic analysis covering:
- Assessment of the actual pit strategy used
- Whether timing was optimal per regulations
- Alternative strategies that could have been faster
- Key insights from the compound choices

**Tab 2 — Live Pit Window Advisor:**
Given current race state (lap number, compound, tyre age, lap time delta vs best), Granite gives a direct pit stop recommendation with reasoning — simulating what a pit wall engineer would advise.

#### 2. Docling
Used in `docling_parser.py` to parse the FIA Sporting Regulations PDF and extract relevant pit stop rules, tyre compound requirements, and mandatory stop regulations. This extracted context is injected directly into every Granite prompt, making the AI's recommendations regulation-aware rather than just data-driven.

```python
# Docling extracts regulations, injected into Granite prompts
reg_context = get_pit_rules_context()[:800]
prompt = f"REGULATIONS CONTEXT:\n{reg_context}\n\nRACE DATA:\n{race_data}"
```

### Q-Learning RL Agent

The RL agent (`rl_optimizer.py`) was trained on real F1 race data:

- **Training data:** 23,400 lap decisions extracted from 5 races (2023–2024 seasons) via FastF1
- **State space:** Tyre age (binned) × Lap time delta (binned) × Laps remaining (binned) × Tyre compound = 4-dimensional
- **Action space:** 3 actions — Stay Out, Pit Now, Pit in 2 Laps
- **Reward signal:** Based on real race outcomes — did the actual strategy succeed?
- **Q-table:** Saved as `data/q_table.pkl`, loaded at runtime

The agent provides:
- A pit decision recommendation (Stay Out / Pit Now / Pit in 2)
- Confidence score (% difference between best and second-best Q-value)
- Full Q-value breakdown for all 3 actions

### FastF1 Integration

`fastf1_loader.py` loads real race sessions:
```python
session = fastf1.get_session(year, grand_prix, 'R')
session.load(telemetry=True, weather=True)
```
Extracts per-driver stint data, lap times, tyre compound history, and pit stop laps — the same data F1 teams use for strategy analysis.

---

## 🖥️ Features

### Tab 1 — Race Strategy Analysis
- Select any season (2022–2024), Grand Prix, and driver
- FastF1 loads real telemetry: total laps, best lap time, compounds used, pit stop laps
- IBM Granite (with Docling regulation context) analyzes the strategy in 3 paragraphs
- Identifies suboptimal decisions and suggests alternatives

### Tab 2 — Live Pit Window Advisor
- Input current race state via sliders: current lap, tyre age, lap time delta
- Select current tyre compound (SOFT/MEDIUM/HARD/INTERMEDIATE/WET)
- IBM Granite gives a direct pit/stay-out recommendation with reasoning
- Simulates real-time pit wall decision support

### Tab 3 — RL Pit Optimizer
- Input tyre age, laps remaining, compound, and lap time delta
- Q-learning agent (trained on 23,400 real decisions) gives a recommendation
- Shows full Q-values for all 3 actions — explainable AI, not a black box
- Confidence score shows how decisive the agent is about its recommendation

---

## 🌍 Why It Matters

**Democratization of F1 strategy:** Top teams spend millions on strategy tools. PitWall makes AI-powered F1 strategy analysis free and accessible to everyone.

**Education:** Students learning about RL, LLMs, and sports analytics can use PitWall as a real-world example of all three working together.

**Explainability:** Unlike a black-box model that just says "pit now", PitWall shows *why* — Granite explains the reasoning in natural language, and the RL agent shows its Q-values.

**Real data, real decisions:** Every recommendation is grounded in official F1 telemetry, not simulated data. The RL agent learned from actual race outcomes.

**Extensibility:** The architecture supports adding new races, new compounds, Safety Car detection, and weather-based strategy adjustments.

---

## 📊 Results

The RL agent was trained and validated on the following races:

| Race | Season | Laps Processed |
|------|--------|----------------|
| Monaco Grand Prix | 2024 | ~4,680 |
| British Grand Prix | 2024 | ~4,680 |
| Italian Grand Prix | 2023 | ~4,680 |
| Belgian Grand Prix | 2023 | ~4,680 |
| Spanish Grand Prix | 2023 | ~4,680 |
| **Total** | | **23,400** |

Example RL output for Monaco 2024 conditions (tyre age: 25 laps, MEDIUM, 30 laps remaining, +0.8s delta):
```json
{
  "decision": "PIT NOW",
  "confidence": "65.2%",
  "q_values": {
    "Stay Out": 7.6,
    "Pit Now": 14.978,
    "Pit in 2": 7.506
  }
}
```

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| AI Reasoning | IBM Granite 4.1 8B (via OpenRouter) |
| Regulations Parser | Docling (IBM) |
| RL Agent | Q-Learning (custom implementation) |
| F1 Data | FastF1 3.8.3 (official timing API) |
| Frontend | Gradio 6.14.0 |
| Language | Python 3.10 |
| Deployment | HuggingFace Spaces |

---

## 📁 Project Structure

```
pitwall-f1-copilot/
├── app.py                    # HF Spaces entry point
├── requirements.txt
├── README.md
├── data/
│   ├── q_table.pkl           # Trained RL policy (23,400 updates)
│   └── f1_regulations_summary.txt
└── src/
    ├── main.py               # Local Gradio UI (port 7861)
    ├── fastf1_loader.py      # FastF1 telemetry pipeline
    ├── granite_engine.py     # IBM Granite via OpenRouter API
    ├── docling_parser.py     # FIA regulations parser (Docling)
    └── rl_optimizer.py       # Q-Learning RL agent
```

---

## 🚀 Setup & Run

### HuggingFace Spaces (Live)
The app is deployed at: https://huggingface.co/spaces/ashish-doing/pitwall-f1-copilot

Required secrets in HF Space settings:
- `OPENROUTER_API_KEY` — OpenRouter API key for IBM Granite access

### Local Setup

```bash
# Clone the repo
git clone https://github.com/ashish-doing/pitwall-f1-copilot
cd pitwall-f1-copilot

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENROUTER_API_KEY=your_openrouter_key_here

# Run locally
python src/main.py  # runs on http://localhost:7861
```

### Requirements
```
fastf1==3.8.3
gradio==6.14.0
huggingface_hub==0.23.4
requests
pandas
numpy
torch
stable-baselines3
gymnasium
matplotlib
docling
```

---

## 🔗 Links

- **Live Demo:** https://huggingface.co/spaces/ashish-doing/pitwall-f1-copilot
- **GitHub:** https://github.com/ashish-doing/pitwall-f1-copilot
- **IBM Granite:** https://github.com/ibm-granite-community
- **Docling:** https://www.docling.ai
- **FastF1 Docs:** https://docs.fastf1.dev

---

## 👤 Author

**Ashish Kumar**
B.Tech ECE, IIIT Guwahati (Batch 2024)
- GitHub: [@ashish-doing](https://github.com/ashish-doing)
- LinkedIn: [linkedin.com/in/ashish-kumar-014aaa3b9](https://linkedin.com/in/ashish-kumar-014aaa3b9)
- HuggingFace: [huggingface.co/ashish-doing](https://huggingface.co/ashish-doing)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built for the <strong>IBM SkillsBuild AI Builders Challenge — May 2026</strong><br>
  Powered by IBM Granite + Docling + FastF1 + Q-Learning RL
</p>