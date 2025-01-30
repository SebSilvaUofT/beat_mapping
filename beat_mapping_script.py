from madmom.features.beats import RNNBeatProcessor, DBNBeatTrackingProcessor
def get_beat_timestamps(songfile_path):
    # Initialize the RNN beat processor
    proc = RNNBeatProcessor()

    # Process the audio file to get beat activations
    activations = proc(songfile_path)

    # Explicitly specify parameters for the DBN processor
    tracker = DBNBeatTrackingProcessor(fps=100, max_bpm=200, min_bpm=50)  # Adjust bpm range as needed

    # Use the tracker to find beats
    beats = tracker(activations)

    # Return detected beats
    return beats

