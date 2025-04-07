import os
import fastf1
import matplotlib
import numpy as np
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ----------------- Adjust Global Plotting Params -----------------
plt.rcParams.update({
    'figure.dpi': 100,        # Lower DPI for a smaller display
    'savefig.dpi': 100,
    'font.size': 6,           # Smaller base font size
    'lines.linewidth': 1,
    'axes.labelsize': 7,      # Slightly larger than base for clarity
    'axes.titlesize': 8,
    'lines.antialiased': True
})

def format_timedelta(td):
    total_seconds = td.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = total_seconds - minutes * 60
    return f"{minutes}:{seconds:05.3f}"

# ----- Setup FastF1 Session -----
cache_path = './f1_cache'
os.makedirs(cache_path, exist_ok=True)
fastf1.Cache.enable_cache(cache_path)

Year = 2025
Session = "Qualifying"
Location = "Suzuka"
session = fastf1.get_session(Year, Location, Session)
session.load()

available_drivers = list(session.laps['Driver'].unique())
default_driver1 = 'VER'
default_driver2 = 'NOR'

# Driver colors (as of 2025 season)
driver_colors = {
    # McLaren
    'NOR': '#FF8000',
    'PIA': '#FF8000',
    # Ferrari
    'LEC': '#DC0000',
    'HAM': '#DC0000',
    # Red Bull Racing
    'VER': '#1E41FF',
    'TSU': '#1E41FF',
    # Mercedes
    'RUS': '#00D2BE',
    'ANT': '#00D2BE',
    # Aston Martin
    'ALO': '#006F62',
    'STR': '#006F62',
    # Alpine
    'GAS': '#0090FF',
    'DOO': '#0090FF',
    # Haas
    'OCO': '#787878',
    'BEA': '#787878',
    # Racing Bulls
    'LAW': '#6699FF',
    'HAD': '#6699FF',
    # Williams
    'ALB': '#005AFF',
    'SAI': '#005AFF',
    # Kick Sauber
    'HUL': '#9B0000',
    'BOR': '#9B0000',
}
default_color1 = 'cyan'
default_color2 = 'magenta'

root = tk.Tk()
root.title("F1 Telemetry Dashboard - Dark Mode")

control_frame = tk.Frame(root, bg='black')
control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

tk.Label(control_frame, text="Driver 1:", bg='black', fg='white').pack(side=tk.LEFT, padx=5)
driver1_var = tk.StringVar(value=default_driver1)
driver1_combo = ttk.Combobox(control_frame, textvariable=driver1_var,
                             values=available_drivers, state="readonly", width=5)
driver1_combo.pack(side=tk.LEFT, padx=5)

tk.Label(control_frame, text="Driver 2:", bg='black', fg='white').pack(side=tk.LEFT, padx=5)
driver2_var = tk.StringVar(value=default_driver2)
driver2_combo = ttk.Combobox(control_frame, textvariable=driver2_var,
                             values=available_drivers, state="readonly", width=5)
driver2_combo.pack(side=tk.LEFT, padx=5)

def update_plot():
    driver1_code = driver1_var.get()
    driver2_code = driver2_var.get()

    color1 = driver_colors.get(driver1_code, default_color1)
    color2 = driver_colors.get(driver2_code, default_color2)

    fig.clf()
    fig.patch.set_facecolor('black')

    # Adjust margins: leave room on the right for lap info without clipping.
    fig.subplots_adjust(left=0.08, right=0.78, top=0.88, bottom=0.12,
                        hspace=0.3, wspace=0.3)

    # 3-row x 2-column layout
    gs = gridspec.GridSpec(
        3, 2,
        height_ratios=[2.5, 1, 1],
        hspace=0.25,
        wspace=0.25
    )

    # 1) Grab each driver's fastest lap
    lap1 = session.laps.pick_driver(driver1_code).pick_fastest()
    lap2 = session.laps.pick_driver(driver2_code).pick_fastest()

    # 2) Get telemetry and add distance
    tel1 = lap1.get_car_data().add_distance()
    tel2 = lap2.get_car_data().add_distance()

    # 3) Create a LapRelativeTime that starts at zero for each driver's fastest lap
    tel1['LapRelativeTime'] = (tel1['Time'] - tel1['Time'].iloc[0]).dt.total_seconds()
    tel2['LapRelativeTime'] = (tel2['Time'] - tel2['Time'].iloc[0]).dt.total_seconds()

    def style_axis(ax, title=None, xlabel=None, ylabel=None):
        ax.set_facecolor('black')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.tick_params(axis='both', colors='white', labelsize=6)
        if title:
            ax.set_title(title, fontsize=8, color='white')
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=7, color='white')
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=7, color='white')

    # --- SPEED vs DISTANCE (Row 0) ---
    ax0 = fig.add_subplot(gs[0, :])
    ax0.plot(tel1['Distance'], tel1['Speed'], label=driver1_code,
             color=color1, lw=1, alpha=0.8)
    ax0.plot(tel2['Distance'], tel2['Speed'], label=driver2_code,
             color=color2, lw=1, alpha=0.8, linestyle='--')
    style_axis(ax0,
               title=f"{Year} {Location} {Session} - Speed Comparison",
               xlabel="Distance (m)", ylabel="Speed (km/h)")
    legend = ax0.legend(fontsize=8, facecolor='white', edgecolor='white')
    for text in legend.get_texts():
        text.set_color('black')
    ax0.grid(True, color='gray', linestyle='--', linewidth=0.5)

    # --- Prepare sector & lap time info text ---
    lap1_time = format_timedelta(lap1['LapTime'])
    lap2_time = format_timedelta(lap2['LapTime'])
    sector1_time_1 = format_timedelta(lap1['Sector1Time'])
    sector2_time_1 = format_timedelta(lap1['Sector2Time'])
    sector3_time_1 = format_timedelta(lap1['Sector3Time'])
    sector1_time_2 = format_timedelta(lap2['Sector1Time'])
    sector2_time_2 = format_timedelta(lap2['Sector2Time'])
    sector3_time_2 = format_timedelta(lap2['Sector3Time'])

    lap_info = (
        f"{'':<10}{driver1_code:<10}{driver2_code:<10}\n"
        f"{'Lap Time':<10}{lap1_time:<10}{lap2_time:<10}\n"
        f"{'Sector 1':<10}{sector1_time_1:<10}{sector1_time_2:<10}\n"
        f"{'Sector 2':<10}{sector2_time_1:<10}{sector2_time_2:<10}\n"
        f"{'Sector 3':<10}{sector3_time_1:<10}{sector3_time_2:<10}"
    )
    fig.text(
        0.81, 0.85,
        lap_info,
        ha='left', va='top',
        fontfamily='monospace', color='white', size=10,
        bbox=dict(facecolor='black', edgecolor='white', pad=4)
    )

    # --- SPEED DELTA (Row 1) ---
    ax_speed_delta = fig.add_subplot(gs[1, :])
    # Use Driver 1's distance array as reference
    distance_ref = tel1['Distance'].values

    # Retrieve speeds from each telemetry set
    speed1 = tel1['Speed'].values
    speed2 = tel2['Speed'].values

    # Interpolate Driver 2's speed onto Driver 1's distance reference
    speed2_interp = np.interp(distance_ref, tel2['Distance'].values, speed2)

    # Compute speed delta
    speed_delta = speed1 - speed2_interp
    ax_speed_delta.plot(distance_ref, speed_delta, color='lime', lw=1, alpha=0.8)
    # Emphasized y=0 line: solid white and thicker
    ax_speed_delta.axhline(0, color='white', linestyle='-', lw=1, alpha=0.4)
    style_axis(ax_speed_delta, xlabel="Distance (m)", ylabel="Speed Delta (km/h)", title="Speed Delta")
    ax_speed_delta.grid(True, color='gray', linestyle='--', linewidth=0.5)

    # --- BRAKE TRACE (Row 2, Column 0) ---
    ax1 = fig.add_subplot(gs[2, 0])
    ax1.plot(tel1['Distance'], tel1['Brake'], label=driver1_code,
             color=color1, lw=1, alpha=0.8)
    ax1.plot(tel2['Distance'], tel2['Brake'], label=driver2_code,
             color=color2, lw=1, alpha=0.8, linestyle='--')
    style_axis(ax1, xlabel="Distance (m)", ylabel="Brake (%)", title="Brake Trace")
    ax1.grid(True, color='gray', linestyle='--', linewidth=0.5)

    # --- THROTTLE INPUT (Row 2, Column 1) ---
    ax2 = fig.add_subplot(gs[2, 1])
    ax2.plot(tel1['Distance'], tel1['Throttle'], label=driver1_code,
             color=color1, lw=1, alpha=0.8)
    ax2.plot(tel2['Distance'], tel2['Throttle'], label=driver2_code,
             color=color2, lw=1, alpha=0.8, linestyle='--')
    style_axis(ax2, xlabel="Distance (m)", ylabel="Throttle (%)", title="Throttle Input")
    ax2.grid(True, color='gray', linestyle='--', linewidth=0.5)

    # Force redraw
    canvas.draw()

update_button = tk.Button(control_frame, text="Update Plot", command=update_plot,
                          bg='gray', fg='white')
update_button.pack(side=tk.LEFT, padx=5)

# Create figure
fig = plt.Figure(figsize=(8, 4))
fig.set_dpi(100)
fig.patch.set_facecolor('black')

canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

update_plot()
root.mainloop()
