from beat_mapping_script import *
from gen_metronome_py9 import *

if __name__ == "__main__":
    # generate the beat timestamps
    beat_timestamps = get_beat_timestamps('05 Dirty Harry.wav')
    generate_metronome_track(beat_timestamps, -20.0, 'Dirty Harry_met.wav')
