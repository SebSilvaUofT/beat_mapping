from beat_mapping_script import *
from gen_metronome_py9 import *
import json
import os
import pandas as pd
from audio_helpers import convert_m4a_to_wav


def get_metadata():
    """
    get all the track data from each track in the musicLibrary folder
    """

    trackfiles = os.listdir('musicLibrary')
    # calculate beat metadata for each track
    metadata = []
    for filePath in trackfiles:
        beat_dict = get_beat_timestamps('musicLibrary/' + filePath)
        metadata.append(beat_dict)

    # metadata_df = pd.DataFrame.from_records(metadata).to_json()
    with open("metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)


if __name__ == "__main__":
    itunes_lib_path = "Music"
    wav_library_path = "converted_wavs"  # Directory to store converted WAV files
    # Ensure the WAV library directory exists
    os.makedirs(wav_library_path, exist_ok=True)
    # Find all .m4a files in iTunes Library (Artist/Album/Songs.m4a)
    m4a_files = []
    for root, _, files in os.walk(itunes_lib_path):
        for file in files:
            if file.endswith(".m4a"):
                m4a_files.append(os.path.join(root, file))

    results = []
    # Process each song
    for i, m4a_path in enumerate(m4a_files):
        try:
            print(f"Processing {i + 1}/{len(m4a_files)}: {os.path.basename(m4a_path)}")

            # Convert M4A to WAV
            wav_path = convert_m4a_to_wav(m4a_path, itunes_lib_path, wav_library_path)

            # Extract beat information
            beat_data = get_beat_timestamps(wav_path)
            beat_data["wav_path"] = wav_path  # Store the WAV path
            results.append(beat_data)  # Store the result

            # Save progress every 10 songs
            if (i + 1) % 10 == 0:
                pd.DataFrame(results).to_csv("tempo_analysis_results.csv", index=False)
        except Exception as e:
            print(f"Error processing {m4a_path}: {e}")

    # Save final results
    pd.DataFrame(results).to_csv("tempo_analysis_results.csv", index=False)
    with open("tempo_analysis_results.json", "w") as json_file:
        json.dump(results, json_file, indent=4)

    print("Processing complete! WAVs saved in 'converted_wavs' and results in 'tempo_analysis_results.csv'.")




