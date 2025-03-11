from madmom.features.beats import RNNBeatProcessor, DBNBeatTrackingProcessor
import numpy as np

def get_beat_timestamps(songfile_path) -> dict:
    # Initialize the RNN beat processor and the temp0 processor
    proc = RNNBeatProcessor()

    # Process the audio file to get beat activations
    activations = proc(songfile_path)
    # Explicitly specify parameters for the DBN processor
    tracker = DBNBeatTrackingProcessor(fps=100, max_bpm=200,
                                       min_bpm=50)  # Adjust bpm range as needed
    # Use the tracker to find beats
    beats = tracker(activations)
    # Compute instantaneous tempo (BPM) between consecutive beats
    beat_intervals = np.diff(beats)  # Time differences between beats
    tempo_values = 60.0 / beat_intervals  # Convert to BPM

    # Compute tempo consistency metrics
    mean_tempo = np.mean(tempo_values)
    std_tempo = np.std(tempo_values)  # Standard deviation of tempo
    cv_tempo = std_tempo / mean_tempo  # Coefficient of variation (normalized)

    # back calculate the beat frames
    beat_frames = (beats * 100).astype(int)
    beat_confidences = activations[beat_frames]
    avg_beat_confidence = np.mean(beat_confidences)

    beat_dict = {'file name': songfile_path,
                 'beat interval CV': cv_tempo,
                 'average beat confidence': avg_beat_confidence,
                 'timestamps': beats.tolist(),
                 'confidences': beat_confidences.tolist()}

    # Return detected beats
    return beat_dict
