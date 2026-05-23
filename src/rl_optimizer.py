import numpy as np
import fastf1
import pandas as pd
import os
import pickle

os.makedirs("/tmp/f1cache", exist_ok=True)
fastf1.Cache.enable_cache("/tmp/f1cache")

COMPOUNDS = {'SOFT': 0, 'MEDIUM': 1, 'HARD': 2, 'INTERMEDIATE': 3, 'WET': 4}
TYRE_AGE_BINS  = [0, 10, 20, 30, 40, 60]
LAP_DELTA_BINS = [0, 0.3, 0.7, 1.5, 3.0]
LAPS_REM_BINS  = [0, 5, 15, 30, 50]

N_TYRE     = len(TYRE_AGE_BINS)
N_DELTA    = len(LAP_DELTA_BINS)
N_LAPS     = len(LAPS_REM_BINS)
N_COMPOUND = len(COMPOUNDS)
N_ACTIONS  = 3

Q_TABLE_PATH = "data/q_table.pkl"

def discretize(value, bins):
    idx = np.searchsorted(bins, value, side='right') - 1
    return int(np.clip(idx, 0, len(bins) - 1))

def get_state(tyre_age, lap_delta, laps_remaining, compound):
    t = discretize(float(tyre_age),      TYRE_AGE_BINS)
    d = discretize(abs(float(lap_delta)), LAP_DELTA_BINS)
    l = discretize(float(laps_remaining), LAPS_REM_BINS)
    c = COMPOUNDS.get(str(compound), 1)
    return (t, d, l, c)

def compute_reward(action, tyre_age, lap_delta, laps_remaining, did_pit_actual):
    if action == 0:  # stay out
        if tyre_age > 30 and lap_delta > 1.0:
            reward = -10
        elif tyre_age > 20 and lap_delta > 0.5:
            reward = -5
        else:
            reward = 5
    elif action == 1:  # pit now
        if tyre_age > 25 and lap_delta > 0.7:
            reward = 15
        elif tyre_age < 10:
            reward = -10
        else:
            reward = 5
    else:  # pit in 2
        if tyre_age > 15 and lap_delta > 0.3:
            reward = 10
        else:
            reward = 2

    # Bonus for matching actual race decision
    if (action >= 1 and did_pit_actual) or (action == 0 and not did_pit_actual):
        reward += 5
    return reward

def load_or_create_qtable():
    os.makedirs("data", exist_ok=True)
    if os.path.exists(Q_TABLE_PATH):
        with open(Q_TABLE_PATH, 'rb') as f:
            return pickle.load(f)
    # Small random init to break ties
    return np.random.uniform(0, 0.01, (N_TYRE, N_DELTA, N_LAPS, N_COMPOUND, N_ACTIONS))

def save_qtable(q_table):
    with open(Q_TABLE_PATH, 'wb') as f:
        pickle.dump(q_table, f)

def train_on_race(session, q_table, alpha=0.5, gamma=0.9, epsilon=0.2):
    total_laps = 0
    for driver in session.laps['Driver'].unique()[:5]:
        try:
            laps = session.laps.pick_drivers(driver).copy()
            laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()
            laps = laps.dropna(subset=['LapTimeSeconds', 'TyreLife', 'Compound'])
            if len(laps) < 5:
                continue

            best_lap   = laps['LapTimeSeconds'].min()
            max_lap    = int(laps['LapNumber'].max())

            for i in range(len(laps) - 1):
                lap      = laps.iloc[i]
                next_lap = laps.iloc[i + 1]

                tyre_age       = float(lap['TyreLife'])
                lap_delta      = float(lap['LapTimeSeconds']) - best_lap
                laps_remaining = max_lap - int(lap['LapNumber'])
                compound       = lap['Compound'] if lap['Compound'] in COMPOUNDS else 'MEDIUM'

                # Correct pit detection
                did_pit = False
                if 'PitOutTime' in next_lap.index:
                    val = next_lap['PitOutTime']
                    did_pit = (val is not None) and (not pd.isna(val))

                state = get_state(tyre_age, lap_delta, laps_remaining, compound)

                # Epsilon-greedy
                if np.random.random() < epsilon:
                    action = np.random.randint(N_ACTIONS)
                else:
                    action = int(np.argmax(q_table[state]))

                reward = compute_reward(action, tyre_age, lap_delta, laps_remaining, did_pit)

                # Next state
                next_tyre  = min(tyre_age + 1, 60)
                next_delta = lap_delta + 0.05 if action == 0 else 0.0
                next_laps  = max(laps_remaining - 1, 0)
                next_state = get_state(next_tyre, next_delta, next_laps, compound)

                # Q-update
                best_next = float(np.max(q_table[next_state]))
                q_table[state][action] += alpha * (
                    reward + gamma * best_next - q_table[state][action]
                )
                total_laps += 1
        except Exception:
            continue
    return q_table, total_laps

def train_agent(races=None, episodes=15):
    if races is None:
        races = [
            (2024, 'Bahrain'),
            (2024, 'Monaco'),
            (2024, 'Silverstone'),
            (2023, 'Bahrain'),
            (2023, 'Monaco'),
        ]

    q_table = load_or_create_qtable()
    print(f"Training RL pit optimizer on {len(races)} races x {episodes} episodes...")

    sessions = []
    for year, gp in races:
        try:
            print(f"  Loading {year} {gp}...")
            session = fastf1.get_session(year, gp, 'R')
            session.load(telemetry=False, weather=False, messages=False)
            sessions.append(session)
        except Exception as e:
            print(f"  Skipped {gp}: {e}")

    total = 0
    for ep in range(episodes):
        epsilon = max(0.05, 0.4 - ep * 0.025)
        for session in sessions:
            q_table, laps = train_on_race(session, q_table, epsilon=epsilon)
            total += laps
        if (ep + 1) % 5 == 0:
            print(f"  Episode {ep+1}/{episodes} done (epsilon={epsilon:.2f})")

    save_qtable(q_table)
    print(f"Training complete. Total Q-updates: {total}")
    return q_table

def get_rl_recommendation(tyre_age: int, lap_delta: float,
                           laps_remaining: int, compound: str) -> dict:
    q_table  = load_or_create_qtable()
    state    = get_state(tyre_age, abs(lap_delta), laps_remaining, compound)
    q_values = q_table[state]
    action   = int(np.argmax(q_values))

    labels = {0: "✅ STAY OUT", 1: "🔴 PIT NOW", 2: "⚠️ PIT IN 2 LAPS"}

    sorted_q = np.sort(q_values)[::-1]
    spread = (sorted_q[0] - sorted_q[1]) / (abs(sorted_q[0]) + 1e-6)
    confidence = float(np.clip(spread * 180 + 35, 35.0, 95.0))

    return {
        "recommendation": labels[action],
        "action_id": action,
        "confidence": round(confidence, 1),
        "q_values": {
            "Stay Out": round(float(q_values[0]), 3),
            "Pit Now":  round(float(q_values[1]), 3),
            "Pit in 2": round(float(q_values[2]), 3),
        }
    }

if __name__ == "__main__":
    q_table = train_agent()

    tests = [
        (28, 1.2, 15, 'MEDIUM'),   # worn tyres, slow — should pit
        (5,  0.1, 40, 'SOFT'),     # fresh tyres — should stay out
        (18, 0.6, 8,  'HARD'),     # moderate wear, few laps left
    ]
    print("\n--- Test recommendations ---")
    for tyre_age, delta, laps_rem, compound in tests:
        r = get_rl_recommendation(tyre_age, delta, laps_rem, compound)
        print(f"  Age={tyre_age} Delta={delta} Laps={laps_rem} {compound}: "
              f"{r['recommendation']} (conf={r['confidence']}%) "
              f"Q={r['q_values']}")