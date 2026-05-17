---
title: PitWall F1 Copilot
emoji: 🏎️
colorFrom: red
colorTo: blue
sdk: gradio
sdk_version: "3.50.2"
python_version: "3.10"
app_file: app.py
pinned: false
---

# 🏎️ PitWall — F1 Race Strategy Copilot

> IBM SkillsBuild AI Builders Challenge — May 2026 Submission

## Problem
F1 race strategy is one of the most complex real-time decision problems in sport. Pit stop timing can win or lose races, yet teams process thousands of data points per second with limited time to act. Small teams and fans have no access to the sophisticated strategy tools used by top F1 teams.

## Solution
PitWall is an AI-powered race strategy copilot that makes F1 strategy analysis accessible. It combines real F1 telemetry data with IBM Granite's reasoning capabilities and a trained RL agent to analyze race strategies and recommend optimal pit windows.

## AI Approach
- **IBM Granite 3.3 8B** (via HuggingFace Inference API) — core reasoning engine for strategy analysis and pit recommendations
- **Q-Learning RL Agent** — trained on 23,400 lap decisions from 5 real F1 races (2023-2024)
- **FastF1** — official F1 timing and telemetry data API
- **Docling** — FIA regulations parser for context-aware analysis
- **Gradio** — interactive web interface

## Features
- 📊 **Race Strategy Analysis** — analyze any driver's complete race strategy using real telemetry data from 2022–2024 seasons
- ⏱️ **Live Pit Window Advisor** — get real-time pit stop recommendations powered by IBM Granite
- 🤖 **RL Pit Optimizer** — Q-learning agent trained on real F1 race data recommends optimal pit windows with confidence scores

## Why It Matters
Strategy decisions in F1 happen in seconds under extreme pressure. PitWall democratizes access to AI-powered strategy tools, helping teams, analysts, and fans understand the "why" behind pit stop decisions through explainable AI.

## Tech Stack
| Component | Technology |
|-----------|------------|
| AI Model | IBM Granite 3.3 8B (HuggingFace Inference API) |
| RL Agent | Q-Learning trained on FastF1 data |
| F1 Data | FastF1 (official timing API) |
| Regulations | Docling (IBM) |
| Frontend | Gradio |
| Language | Python 3.10 |

## Setup
```bash
pip install fastf1 gradio requests docling
export HF_TOKEN=your_token_here
python app.py
```

## Project Structure

```
pitwall-f1-copilot/
├── app.py                    # HF Spaces entry point
├── requirements.txt
├── README.md
├── data/
│   ├── q_table.pkl           # Trained RL policy (23,400 updates)
│   └── f1_regulations_summary.txt
└── src/
    ├── main.py               # Local Gradio UI
    ├── fastf1_loader.py      # F1 telemetry data pipeline
    ├── granite_engine.py     # IBM Granite integration
    ├── docling_parser.py     # FIA document parser
    └── rl_optimizer.py       # Q-Learning RL agent
```

## IBM Technologies Used
- **IBM Granite 3.3 8B** — strategy reasoning and explainability via HuggingFace
- **Docling** — FIA regulations PDF parsing for context-aware Granite prompts

## Demo
1. Select a season, Grand Prix, and driver → click **Analyze Strategy** → IBM Granite provides strategic analysis based on real telemetry data
2. Use **Live Pit Window Advisor** → adjust tyre age and lap delta → get Granite recommendation
3. Use **RL Pit Optimizer** → get recommendation from agent trained on 23,400 real F1 lap decisions