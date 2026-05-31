# Contributing to PitWall F1 Copilot

## Setup
1. Fork the repo
2. `cp .env.example .env` and add your keys
3. `pip install -r requirements.txt`
4. `python src/main.py` — runs locally at `http://localhost:7861`

## Architecture
Three AI systems in `src/`:
- `fastf1_loader.py` — fetches real lap times, tyre compounds, pit stop laps via FastF1 API
- `docling_parser.py` — parses FIA Sporting Regulations PDF using IBM Docling
- `granite_engine.py` — IBM Granite 4.1 8B via Groq; powers Tab 1 strategy analysis + Tab 2 pit advisor
- `rl_optimizer.py` — Q-Learning agent trained on 23,400 real F1 lap decisions; powers Tab 3
- `main.py` — Gradio UI wiring all three systems into tabs

## Adding a new Grand Prix
1. Add the circuit name to the `CIRCUITS` list in `src/fastf1_loader.py`
2. Test with `load_race_data(circuit, driver, season)` — FastF1 handles the rest via cache

## Adding a new RL training race
1. Add the race to `TRAINING_RACES` in `src/rl_optimizer.py`
2. Re-run `train_agent()` to update `data/q_table.pkl`
3. Commit the updated `q_table.pkl`

## Pull Request Guidelines
- One feature per PR
- Test all 3 tabs before submitting
- Update README if adding new circuits, drivers, or capabilities

## Reporting Issues
Open a GitHub issue with: tab used, inputs entered, error message, and HuggingFace Spaces logs if applicable.