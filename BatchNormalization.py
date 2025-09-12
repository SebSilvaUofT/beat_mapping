import ast
import os
import subprocess
import json
import pandas as pd
import bisect


def get_lufs(file_path):
    """Returns the LUFS (integrated loudness) of a WAV file using FFmpeg."""
    cmd = [
        "ffmpeg", "-i", file_path, "-af", "loudnorm=print_format=json", "-f", "null", "-"
    ]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)

    json_text = ""
    capture = False
    for line in result.stderr.split("\n"):
        line = line.strip()
        if line.startswith("{"):
            capture = True
        if capture:
            json_text += line
        if line.endswith("}"):
            break

    if not json_text:
        print(f"Warning: No LUFS data extracted for {file_path}. Check file integrity.")
        return None

    try:
        loudness_data = json.loads(json_text)
        return float(loudness_data["input_i"])  # Ensure it's a float
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        print(f"Error extracting LUFS for {file_path}: {e}")
        return None


def normalize_wav(input_folder, output_folder, csv_path, target_lufs=-9, target_duration=130):
    """Normalizes all WAV files in a folder to the target LUFS and trims to target duration."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    log_data = []

    # Load CSV file
    df = pd.read_csv(csv_path, converters={"timestamps": ast.literal_eval, "confidences": ast.literal_eval})


    for idx, row in df.iterrows():
        filename = row['file name']
        start_time = row['Start_Time']
        row["timestamps"] = list(map(float, row["timestamps"]))
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, f"normalized_{filename}")

        if not os.path.exists(input_path):
            print(f"Skipping {filename}: File not found.")
            continue

        original_lufs = get_lufs(input_path)

        if original_lufs is not None:
            print(f"Processing: {filename} (Original LUFS: {original_lufs:.2f})")

            # Determine trim start time (if stable duration start is less than 2 seconds in, dont trim the start
            if start_time <= 2.0:
                start_time = 0
            else:
                # remove the fade in timestamps and offset them appropriately
                start_index = bisect.bisect_left(row['timestamps'], start_time)
                df.at[idx, 'timestamps'] = [timestamp - start_time for timestamp in row['timestamps'][start_index:]]
                df.at[idx, 'confidences'] = row['confidences'][start_index:]

            last_index = bisect.bisect(row['timestamps'], target_duration)
            # Trim timestamps and confidences in the original DataFrame
            df.at[idx, 'timestamps'] = df.at[idx, 'timestamps'][:last_index]
            df.at[idx, 'confidences'] = df.at[idx, 'confidences'][:last_index]

            print("last timestamp: ",  df.at[idx, 'timestamps'][-1])

            # # FFmpeg command for loudness normalization and trimming
            cmd = [
                "ffmpeg", "-i", input_path, "-af",
                f"loudnorm=I={target_lufs}:TP=-1.5",
                "-ss", str(start_time), "-t", str(target_duration),
                "-ar", "44100",  # Specify the sample rate here
                output_path
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            normalized_lufs = get_lufs(output_path)
            log_data.append({
                "file": filename,
                "original_LUFS": original_lufs,
                "normalized_LUFS": normalized_lufs,
                "trim_start": start_time
            })
        else:
            print(f"Skipping {filename} due to LUFS extraction error.")


    output_csv = "normalized_library_using_BEATS.csv"
    # Save the cleaned file
    df.to_csv(output_csv, index=False)
    print(f"Cleaned CSV file saved: {output_csv}")


# Example usage
input_folder = "converted_wavs"
output_folder = "normalized_library_using_BEATS_and9LUFS"

normalize_wav(input_folder, output_folder, "App Music Library.csv", target_lufs=-9)
