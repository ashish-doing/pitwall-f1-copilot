import fastf1
import pandas as pd
import os

CACHE_DIR = "C:/f1cache"
fastf1.Cache.enable_cache(CACHE_DIR)

def get_race_session(year: int, grand_prix: str, session_type: str = 'R'):
    """Load a race session from FastF1."""
    session = fastf1.get_session(year, grand_prix, session_type)
    session.load(telemetry=True, weather=True, messages=False)
    return session

def get_driver_stints(session, driver: str):
    """Get stint/tire data for a specific driver."""
    laps = session.laps.pick_drivers(driver)
    stints = laps[['LapNumber', 'Compound', 'TyreLife', 'LapTime', 'PitInTime', 'PitOutTime']].copy()
    stints['LapTimeSeconds'] = stints['LapTime'].dt.total_seconds()
    return stints

def get_pit_stops(session, driver: str):
    """Extract pit stop laps for a driver."""
    laps = session.laps.pick_drivers(driver)
    pit_laps = laps[laps['PitInTime'].notna()][['LapNumber', 'Compound', 'TyreLife']].copy()
    return pit_laps

def get_race_summary(session, driver: str):
    """Get a concise race summary dict for Granite to analyze."""
    stints = get_driver_stints(session, driver)
    pit_stops = get_pit_stops(session, driver)
    
    summary = {
        "driver": driver,
        "grand_prix": session.event['EventName'],
        "year": session.event.year,
        "total_laps": int(stints['LapNumber'].max()) if not stints.empty else 0,
        "compounds_used": stints['Compound'].dropna().unique().tolist(),
        "pit_stop_laps": pit_stops['LapNumber'].tolist(),
        "avg_lap_time": round(stints['LapTimeSeconds'].mean(), 3),
        "best_lap_time": round(stints['LapTimeSeconds'].min(), 3),
        "stint_breakdown": []
    }
    
    # Build stint breakdown
    current_compound = None
    stint_start = None
    for _, row in stints.iterrows():
        if row['Compound'] != current_compound:
            if current_compound is not None:
                summary['stint_breakdown'].append({
                    "compound": current_compound,
                    "start_lap": int(stint_start),
                    "end_lap": int(row['LapNumber'] - 1),
                    "length": int(row['LapNumber'] - stint_start)
                })
            current_compound = row['Compound']
            stint_start = row['LapNumber']
    
    return summary

if __name__ == "__main__":
    print("Loading 2024 Monaco GP...")
    session = get_race_session(2024, 'Monaco', 'R')
    summary = get_race_summary(session, 'LEC')
    print(summary)