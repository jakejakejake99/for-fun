import fastf1
import numpy as np
import pandas as pd
import plotly.graph_objects as go

fastf1.Cache.enable_cache('f1_cache')

def plot_time_gaps_interactive(year, grand_prix, session_type):
    session = fastf1.get_session(year, grand_prix, session_type)
    session.load()

    laps = session.laps
    results = session.results.sort_values(by='Position')
    drivers_sorted = results['Abbreviation'].tolist()
    winner = results.iloc[0]['Abbreviation']
    leader_laps = laps.pick_drivers([winner])
    leader_lap_times = leader_laps['LapTime'].dt.total_seconds().values
    leader_lap_numbers = leader_laps['LapNumber'].values
    leader_cumulative_time = np.cumsum(leader_lap_times)

    fig = go.Figure()

    for driver in drivers_sorted:
        driver_laps = laps.pick_drivers([driver])
        if driver_laps.empty:
            continue

        driver_lap_times = driver_laps['LapTime'].dt.total_seconds().values
        driver_lap_numbers = driver_laps['LapNumber'].values
        driver_cumulative_time = np.cumsum(driver_lap_times)

        common_laps = []
        time_gaps = []
        for i, lap_num in enumerate(driver_lap_numbers):
            leader_indices = np.where(leader_lap_numbers == lap_num)[0]
            if len(leader_indices) > 0:
                leader_idx = leader_indices[0]
                common_laps.append(lap_num)
                time_gaps.append(driver_cumulative_time[i] - leader_cumulative_time[leader_idx])

        color = f"#{session.results.loc[session.results.Abbreviation == driver, 'TeamColor'].values[0]}"
        fig.add_trace(go.Scatter(
            x=common_laps,
            y=time_gaps,
            mode='lines',
            name=driver,
            line=dict(color=color, width=3 if driver == winner else 1.5),
            hovertemplate=f"<b>{driver}</b><br>Lap: %{{x}}<br>Gap: %{{y:.2f}} sec<extra></extra>"
        ))

    fig.update_layout(
        title=f"Time Gaps to Leader - {grand_prix} {year}",
        xaxis_title='Lap Number',
        yaxis_title='Gap to Leader (sec)',
        yaxis_autorange='reversed',  # Inverted axis like in F1 broadcast
        template='plotly_white',
        legend=dict(title="Drivers", traceorder="normal")
    )

    fig.show()

# Example usage
plot_time_gaps_interactive(2025, 'Suzuka', 'R')
