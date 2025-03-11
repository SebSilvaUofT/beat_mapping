import pandas as pd
import numpy as np
import ast  # To safely convert string to list

def analyze_beat_confidence(beat_confidences, timestamps, fade_threshold=0.5, drop_threshold=0.5):
    """Analyze beat confidence to detect fade-in, fade-out, and overall confidence trends."""

    # Identify fade-in length (first consecutive beats below threshold)
    fade_in_length = 0
    for conf in beat_confidences:
        if conf < fade_threshold:
            fade_in_length += 1
        else:
            break  # Stop counting when a beat exceeds the threshold

    # Identify fade-out length (last consecutive beats below threshold)
    fade_out_length = 0
    for conf in reversed(beat_confidences):
        if conf < fade_threshold:
            fade_out_length += 1
        else:
            break  # Stop counting when a beat exceeds the threshold

    # Find fade-in end timestamp (last weak beat in fade-in)
    fade_in_end_timestamp = timestamps[fade_in_length] if fade_in_length < len(timestamps) else 0.0

    # Find fade-out start timestamp (first weak beat in fade-out)
    fade_out_start_index = len(timestamps) - fade_out_length
    fade_out_start_timestamp = timestamps[fade_out_start_index] if fade_out_length > 0 else timestamps[len(timestamps) - 1]
    core_duration = fade_out_start_timestamp - fade_in_end_timestamp
    # Calculate mean confidence of "core" (middle) section
    if fade_in_length + fade_out_length < len(beat_confidences):
        core_confidences = beat_confidences[fade_in_length:-fade_out_length] if fade_out_length > 0 else beat_confidences[fade_in_length:]
        mean_core_confidence = np.mean(core_confidences) if len(core_confidences) > 0 else 0
    else:
        mean_core_confidence = 0  # In case the entire track is faded

    return {
        "fade_in_length": fade_in_length,  # Number of beats in fade-in
        "fade_out_length": fade_out_length,  # Number of beats in fade-out
        "mean_core_confidence": mean_core_confidence,  # Confidence excluding fade-in/out
        "core_duration": core_duration
    }


# Load CSV file
csv_file = "tempo_analysis_results.csv"  # Replace with actual file name
df = pd.read_csv(csv_file)


# Function to convert string of lists into NumPy array
def parse_confidence_list(conf_str):
    try:
        return np.array(ast.literal_eval(conf_str))  # Convert string to list, then to NumPy array
    except (SyntaxError, ValueError):
        return np.array([])  # Return empty array if parsing fails


# Process each row in the CSV
fade_in_list = []
fade_out_list = []
mean_core_conf_list = []
core_duration_list = []


for index, row in df.iterrows():
    beat_confidences = parse_confidence_list(row['confidences'])  # Assuming column name is 'confidences'
    beat_timestamps = parse_confidence_list(row['timestamps'])
    if beat_confidences.size > 0:  # Ensure data is valid
        result = analyze_beat_confidence(beat_confidences, beat_timestamps)

        fade_in_list.append(result["fade_in_length"])
        fade_out_list.append(result["fade_out_length"])
        mean_core_conf_list.append(result["mean_core_confidence"])
        core_duration_list.append(result["core_duration"])

    else:
        fade_in_list.append(None)
        fade_out_list.append(None)
        mean_core_conf_list.append(None)
        core_duration_list.append(None)


# Add results to DataFrame
df["fade_in_length"] = fade_in_list
df["fade_out_length"] = fade_out_list
df["mean_core_confidence"] = mean_core_conf_list
df["core_duration"] = core_duration_list

# Save updated CSV
output_csv = "updated_beat_data.csv"
df.to_csv(output_csv, index=False)

print(f"Processed CSV saved as {output_csv}")