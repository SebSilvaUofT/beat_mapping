import os
import subprocess
import json

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

def normalize_wav(input_folder, output_folder, target_lufs=-16):
    """Normalizes all WAV files in a folder to the target LUFS."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    log_data = []

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".wav"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"normalized_{filename}")

            original_lufs = get_lufs(input_path)

            if original_lufs is not None:
                print(f"Processing: {filename} (Original LUFS: {original_lufs:.2f})")

                cmd = [
                    "ffmpeg", "-i", input_path, "-af",
                    f"loudnorm=I={target_lufs}:TP=-1.5", output_path  # Removed LRA=7
                ]

                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                normalized_lufs = get_lufs(output_path)
                log_data.append({
                    "file": filename,
                    "original_LUFS": original_lufs,
                    "normalized_LUFS": normalized_lufs
                })
            else:
                print(f"Skipping {filename} due to LUFS extraction error.")

    # Save log to a file
    log_path = os.path.join(output_folder, "loudness_log.json")
    with open(log_path, "w") as log_file:
        json.dump(log_data, log_file, indent=4)

    print(f"Normalization complete! Log saved at {log_path}")


# Example usage
input_folder = "Music Library"
output_folder = "normalizedWavs"
normalize_wav(input_folder, output_folder, target_lufs=-9)
