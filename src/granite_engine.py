import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "granite4:350m"

def analyze_strategy(race_summary: dict) -> str:
    """Send race summary to Granite for strategy analysis."""
    
    # Get regulation context
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

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()['response']
    except requests.exceptions.ConnectionError:
        return "Error: Ollama is not running. Start it with: ollama serve"
    except Exception as e:
        return f"Error: {str(e)}"

def recommend_pit_window(lap: int, compound: str, tyre_life: int, lap_time_delta: float) -> str:
    """Get Granite recommendation for pit window."""
    
    prompt = f"""You are an F1 pit wall strategist. Given:
- Current lap: {lap}
- Current tyre compound: {compound}
- Tyre age: {tyre_life} laps
- Lap time delta vs best lap: +{lap_time_delta:.3f}s

Should the driver pit now, in 2-3 laps, or stay out? 
Give a direct recommendation with brief reasoning in 2-3 sentences."""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()['response']
    except requests.exceptions.ConnectionError:
        return "Error: Ollama is not running. Start it with: ollama serve"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Test with sample data
    test_summary = {
        "driver": "LEC",
        "grand_prix": "Monaco Grand Prix",
        "year": 2024,
        "total_laps": 78,
        "compounds_used": ["MEDIUM", "HARD"],
        "pit_stop_laps": [32],
        "avg_lap_time": 109.321,
        "best_lap_time": 75.162,
        "stint_breakdown": [
            {"compound": "MEDIUM", "start_lap": 1, "end_lap": 32, "length": 32},
            {"compound": "HARD", "start_lap": 33, "end_lap": 78, "length": 46}
        ]
    }
    
    print("Testing Granite strategy analysis...")
    print(analyze_strategy(test_summary))