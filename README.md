# 🏎️ PitWall — F1 Race Strategy Copilot

> IBM SkillsBuild AI Builders Challenge — May 2025 Submission

## Problem
F1 race strategy is one of the most complex real-time decision problems in sport. Pit stop timing can win or lose races, yet teams process thousands of data points per second with limited time to act. Small teams and fans have no access to the sophisticated strategy tools used by top F1 teams.

## Solution
PitWall is an AI-powered race strategy copilot that makes F1 strategy analysis accessible. It combines real F1 telemetry data with IBM Granite's reasoning capabilities to analyze race strategies and recommend optimal pit windows.

## AI Approach
- **IBM Granite 4.0** (via Ollama) — core reasoning engine for strategy analysis and pit recommendations
- **FastF1** — official F1 timing and telemetry data API
- **Gradio** — interactive web interface

## Features
- 📊 **Race Strategy Analysis** — analyze any driver's complete race strategy using real telemetry data from 2022–2024 seasons
- ⏱️ **Live Pit Window Advisor** — get real-time pit stop recommendations based on tyre compound, age, and lap time delta
- 🤖 **IBM Granite Explanations** — every recommendation includes human-readable reasoning

## Why It Matters
Strategy decisions in F1 happen in seconds under extreme pressure. PitWall democratizes access to AI-powered strategy tools, helping teams, analysts, and fans understand the "why" behind pit stop decisions through explainable AI.

## Tech Stack
| Component | Technology |
|-----------|------------|
| AI Model | IBM Granite 4.0 350M (via Ollama) |
| F1 Data | FastF1 (official timing API) |
| Frontend | Gradio |
| Language | Python 3.10 |

## Setup
```bash
pip install fastf1 gradio requests
ollama pull granite4:350m
python src/main.py
```

## Project Structure

```
pitwall-f1-copilot/
├── src/
│   ├── main.py              # Gradio UI
│   ├── fastf1_loader.py     # F1 telemetry data pipeline
│   ├── granite_engine.py    # IBM Granite integration
│   └── docling_parser.py    # FIA document parser
├── requirements.txt
└── README.md
```

## IBM Technologies Used
- **IBM Granite 4.0 350M** — strategy reasoning and explainability

## Demo
Select a season, Grand Prix, and driver → click Analyze Strategy → IBM Granite provides strategic analysis based on real telemetry data.
