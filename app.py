import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Pre-train RL agent on startup if no q_table exists
if not os.path.exists('data/q_table.pkl'):
    print("Training RL agent...")
    from rl_optimizer import train_agent
    train_agent()

import gradio as gr
from fastf1_loader import get_race_session, get_race_summary
from granite_engine import analyze_strategy, recommend_pit_window

session_cache = {}

def load_and_analyze(year, grand_prix, driver):
    try:
        cache_key = f"{year}_{grand_prix}"
        if cache_key not in session_cache:
            session_cache[cache_key] = get_race_session(int(year), grand_prix, 'R')
        session = session_cache[cache_key]
        summary = get_race_summary(session, driver)
        analysis = analyze_strategy(summary)
        summary_text = f"""
**Driver:** {summary['driver']} | **Race:** {summary['grand_prix']} {summary['year']}
**Total Laps:** {summary['total_laps']} | **Best Lap:** {summary['best_lap_time']}s
**Compounds Used:** {', '.join(summary['compounds_used'])}
**Pit Stop Laps:** {summary['pit_stop_laps']}
        """
        return summary_text.strip(), analysis
    except Exception as e:
        return f"Error: {str(e)}", ""

def get_pit_recommendation(lap, compound, tyre_life, lap_delta):
    try:
        return recommend_pit_window(int(lap), compound, int(tyre_life), float(lap_delta))
    except Exception as e:
        return f"Error: {str(e)}"

def get_rl_rec(tyre_age, compound, laps_rem, delta):
    try:
        from rl_optimizer import get_rl_recommendation
        result = get_rl_recommendation(int(tyre_age), float(delta), int(laps_rem), compound)
        return result['recommendation'], f"{result['confidence']}%", result['q_values']
    except Exception as e:
        return f"Error: {str(e)}", "", {}

with gr.Blocks(title="PitWall — F1 Race Strategy Copilot") as app:
    gr.Markdown("""
    # 🏎️ PitWall — F1 Race Strategy Copilot
    **Powered by IBM Granite + FastF1 telemetry data + RL Agent**
    *IBM SkillsBuild AI Builders Challenge — May 2026*
    """)

    with gr.Tab("📊 Race Strategy Analysis"):
        gr.Markdown("Analyze a driver's complete race strategy using real F1 telemetry data.")
        with gr.Row():
            year_input = gr.Dropdown(choices=["2024", "2023", "2022"], value="2024", label="Season")
            gp_input = gr.Dropdown(choices=["Monaco", "Bahrain", "Silverstone", "Monza", "Spa", "Suzuka"], value="Monaco", label="Grand Prix")
            driver_input = gr.Dropdown(choices=["LEC", "VER", "HAM", "NOR", "SAI", "RUS", "ALO", "PIA"], value="LEC", label="Driver")
        analyze_btn = gr.Button("🔍 Analyze Strategy", variant="primary")
        summary_out = gr.Markdown(label="Race Summary")
        analysis_out = gr.Textbox(label="🤖 IBM Granite Strategy Analysis", lines=12, interactive=False)
        analyze_btn.click(fn=load_and_analyze, inputs=[year_input, gp_input, driver_input], outputs=[summary_out, analysis_out])

    with gr.Tab("⏱️ Live Pit Window Advisor"):
        gr.Markdown("Get real-time pit stop recommendations based on current race conditions.")
        with gr.Row():
            lap_input = gr.Slider(1, 70, value=25, step=1, label="Current Lap")
            compound_input = gr.Dropdown(choices=["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"], value="MEDIUM", label="Current Compound")
        with gr.Row():
            tyre_life_input = gr.Slider(1, 50, value=20, step=1, label="Tyre Age (laps)")
            delta_input = gr.Number(value=0.5, label="Lap Time Delta vs Best (seconds)")
        pit_btn = gr.Button("🏁 Get Pit Recommendation", variant="primary")
        pit_out = gr.Textbox(label="🤖 IBM Granite Recommendation", lines=5, interactive=False)
        pit_btn.click(fn=get_pit_recommendation, inputs=[lap_input, compound_input, tyre_life_input, delta_input], outputs=[pit_out])

    with gr.Tab("🤖 RL Pit Optimizer"):
        gr.Markdown("""
        ### Reinforcement Learning Pit Window Optimizer
        Trained on **23,400 lap decisions** from 5 real F1 races (2023-2024).
        """)
        with gr.Row():
            rl_tyre_age = gr.Slider(1, 55, value=25, step=1, label="Tyre Age (laps)")
            rl_compound = gr.Dropdown(choices=["SOFT", "MEDIUM", "HARD"], value="MEDIUM", label="Compound")
        with gr.Row():
            rl_laps_rem = gr.Slider(1, 60, value=20, step=1, label="Laps Remaining")
            rl_delta = gr.Number(value=0.8, label="Lap Time Delta vs Best (s)")
        rl_btn = gr.Button("🧠 Get RL Recommendation", variant="primary")
        with gr.Row():
            rl_rec_out = gr.Textbox(label="RL Agent Decision", lines=2)
            rl_conf_out = gr.Textbox(label="Confidence", lines=2)
        rl_qval_out = gr.JSON(label="Q-Values (learned policy)")
        rl_btn.click(fn=get_rl_rec, inputs=[rl_tyre_age, rl_compound, rl_laps_rem, rl_delta], outputs=[rl_rec_out, rl_conf_out, rl_qval_out])

    gr.Markdown("""
    ---
    **Tech Stack:** IBM Granite · FastF1 · Gradio · Python · Q-Learning RL
    **Data:** Official F1 timing data via FastF1 API
    """)

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)