import requests
import json
import os

# Use HF Inference API for Granite (works on HF Spaces)
HF_TOKEN = os.environ.get("HF_TOKEN", "")
API_URL = "https://api-inference.huggingface.co/models/ibm-granite/granite-3.1-8b-instruct"

def query_granite(prompt: str) -> str:
    """Query IBM Granite via HuggingFace Inference API."""
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 400,
            "temperature": 0.7,
            "return_full_text": False
        }
    }
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list):
            return result[0].get('generated_text', 'No response generated.')
        return str(result)
    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to HuggingFace API."
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_strategy(race_summary: dict) -> str:
    try:
        from docling_parser import get_pit_rules_context
        reg_context = get_pit_rules_context()[:800]
    except:
        reg_context = "Standard F1 pit stop rules apply."

    prompt = f"""You are an expert F1 race strategist. Using the regulations below as context, analyze the race data and provide:
1. Assessment of the pit stop strategy used
2. Whether the timing was optimal per regulations
3. What alternative strategy could have been faster
4. Key insights from the tire compounds used

REGULATIONS CONTEXT:
{reg_context}

RACE DATA:
- Driver: {race_summary['driver']}
- Grand Prix: {race_summary['grand_prix']} {race_summary['year']}
- Total Laps: {race_summary['total_laps']}
- Compounds Used: {', '.join(race_summary['compounds_used'])}
- Pit Stop Laps: {race_summary['pit_stop_laps']}
- Average Lap Time: {race_summary['avg_lap_time']}s
- Best Lap Time: {race_summary['best_lap_time']}s

Provide a concise strategic analysis in 3 paragraphs."""

    return query_granite(prompt)

def recommend_pit_window(lap: int, compound: str, tyre_life: int, lap_time_delta: float) -> str:
    prompt = f"""You are an F1 pit wall strategist. Given:
- Current lap: {lap}
- Current tyre compound: {compound}
- Tyre age: {tyre_life} laps
- Lap time delta vs best lap: +{lap_time_delta:.3f}s

Should the driver pit now, in 2-3 laps, or stay out?
Give a direct recommendation with brief reasoning in 2-3 sentences."""

    return query_granite(prompt)

if __name__ == "__main__":
    print("Testing Granite via HF API...")
    result = recommend_pit_window(25, "MEDIUM", 20, 0.8)
    print(result)