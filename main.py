from beat_mapping_script import *
from gen_metronome_py9 import *
import json
import os
import pandas as pd


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
    # Read from JSON
    with open("metadata.json", "r") as f:
        data = json.load(f)
    print(data)
    print(type(data))



