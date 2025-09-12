import numpy as np
import pandas as pd
import ast  # For safely converting string to list
from scipy.stats import gaussian_kde

# Parameters
hLocal = 5.0   # Local stability threshold (%)
hRun = 10      # Minimum stable run duration (s)
hGap = 2.5     # Max gap duration (s)

# Load the CSV file
csv_file = "App Music Library.csv"    # Replace with your CSV file path
output_file = "beats_output_with_segments.csv"    # Output file to save results

# Load CSV into DataFrame
df = pd.read_csv(csv_file)

# Store results
results = []

def process_ibei(timestamps, song_id):
    """Process a single IBeI series and return summary statistics including start/end times."""
    if len(timestamps) < 2:
        return [song_id, len(timestamps), 0, 0, 0, 0, 0, 0, 0, 0, None, None]

    # Step 1: Calculate IBeI series (difference between timestamps)
    ibei = np.diff(timestamps)

    if len(ibei) < 2:
        return [song_id, len(ibei), 0, 0, 0, 0, 0, 0, 0, 0, None, None]

    # Step 2: KDE for central tendency
    kde = gaussian_kde(ibei, bw_method='scott')
    density = kde(ibei)
    central_tendency = ibei[np.argmax(density)]

    # Step 3: Calculate PDL and SPC
    pdl = 100 * (ibei - central_tendency) / central_tendency
    spc = 100 * np.diff(ibei) / ibei[:-1] if len(ibei) > 1 else np.array([])

    # Step 4: Identify stable IBeIs
    stable = np.abs(pdl) <= hLocal
    successive_stable = np.concatenate([[False], np.abs(spc) <= hLocal])

    # Ensure shape alignment
    stable_final = stable[:len(successive_stable)] & successive_stable

    # Step 5: Identify Runs and Gaps
    run_indices = np.where(stable_final)[0]

    if len(run_indices) < 2:
        return [song_id, len(ibei), 0, 0, 0, 0, 0, 0, 0, 0, None, None]

    # Calculate gap durations in seconds
    gaps = np.diff(timestamps[run_indices])

    # Identify stable segments
    stable_segments = []
    current_run = [run_indices[0]]

    for i in range(1, len(run_indices)):
        if gaps[i - 1] <= hGap:
            current_run.append(run_indices[i])
        else:
            # Check if the current run meets the minimum duration threshold
            run_duration = timestamps[current_run[-1]] - timestamps[current_run[0]]
            if run_duration >= hRun:
                stable_segments.append(current_run)
            current_run = [run_indices[i]]

    # Handle the last run
    if current_run:
        run_duration = timestamps[current_run[-1]] - timestamps[current_run[0]]
        if run_duration >= hRun:
            stable_segments.append(current_run)

    # Find the longest stable segment
    if stable_segments:
        # Use duration (in seconds) to find the longest segment
        longest_segment = max(stable_segments, key=lambda x: timestamps[x[-1]] - timestamps[x[0]])
        start_time = timestamps[longest_segment[0]]
        end_time = timestamps[longest_segment[-1]]
        stable_duration = end_time - start_time  # Duration of the longest stable segment
    else:
        start_time, end_time = None, None
        stable_duration = 0

    # Summary statistics
    total_duration = timestamps[-1] - timestamps[0]  # Total duration of the song
    stable_percentage = (stable_duration / total_duration) * 100 if total_duration > 0 else 0
    run_percentage = (len(run_indices) / len(ibei)) * 100 if len(ibei) > 0 else 0

    pdl_max = np.max(np.abs(pdl)) if len(pdl) > 0 else 0
    spc_max = np.max(np.abs(spc)) if len(spc) > 0 else 0

    return [
        song_id,
        len(ibei),
        stable_duration,
        stable_percentage,
        run_percentage,
        central_tendency,
        pdl_max,
        spc_max,
        len(stable_segments),
        len(run_indices),
        start_time,
        end_time
    ]

# Process each song in the CSV
for _, row in df.iterrows():
    song_id = row["file name"]  # Adjust column name if different
    timestamps_str = row["timestamps"]

    try:
        # Convert the stringified list to a Python list of floats
        timestamps = np.array(ast.literal_eval(timestamps_str), dtype=float)

        if len(timestamps) < 2:
            print(f"Skipping {song_id}: Not enough timestamps")
            continue

        # Process IBeI series
        stats = process_ibei(timestamps, song_id)
        results.append(stats)

    except (ValueError, SyntaxError) as e:
        print(f"Error parsing timestamps for {song_id}: {e}")

# Save results to CSV
columns = [
    "Song_ID", "Total_IBeIs", "Stable_Duration", "Stable_Percentage",
    "Run_Percentage", "Central_Tendency", "PDL_Max", "SPC_Max",
    "Stable_Segments", "Run_Indices", "Start_Time", "End_Time"
]

output_df = pd.DataFrame(results, columns=columns)
 # Convert columns to numeric where applicable
output_df = output_df.apply(pd.to_numeric, errors='ignore')
output_df.to_csv(output_file, index=False)

print(f"Analysis complete! Results saved to {output_file}")