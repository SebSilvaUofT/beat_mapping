# Sebastian Silva - MASc Student, PROPEL LAB
# This script makes use of spotify API functions to generate an accompaning
# metronome track

from dataclasses import dataclass
from typing import Tuple, Optional

import numpy as np
import audiosegment
from pydub import AudioSegment

@dataclass
class MetronomeConfig:
    frequency: float = 1000  # Hz
    tone_duration: float = 0.05  # seconds
    sample_rate: int = 44100
    amplitude: float = 0.5

def generate_tone(config: MetronomeConfig) -> np.ndarray:
    t = np.linspace(0, config.tone_duration,
                    int(config.sample_rate * config.tone_duration),
                    endpoint=False)
    return config.amplitude * np.sin(2 * np.pi * config.frequency * t)

def generate_metronome_track(
        timestamps: list[float],
        target_db: float,
        output_path: Optional[str] = None,
        config: MetronomeConfig = MetronomeConfig()
) -> Tuple[np.ndarray, int]:

    # Pre-generate tone
    tone = generate_tone(config)
    tone_samples = len(tone)

    # Create track
    total_duration = max(timestamps) + config.tone_duration
    audio_track = np.zeros(int(config.sample_rate * total_duration))

    # Insert tones
    for timestamp in timestamps:
        start_idx = int(timestamp * config.sample_rate)
        end_idx = start_idx + tone_samples
        audio_track[start_idx:end_idx] += tone[:len(audio_track[start_idx:end_idx])]

    # Normalize and convert to 16-bit
    audio_track = np.clip(audio_track, -1.0, 1.0)
    audio_track = (audio_track * 32767).astype(np.int16)

    # Create mono audio segment
    audio: AudioSegment = (audiosegment.from_numpy_array(audio_track, config.sample_rate).set_channels(1))

    # Adjust volume
    change_in_db = target_db - audio.dBFS
    adjusted_audio = audio.apply_gain(change_in_db)

    # Convert to numpy array
    data = np.array(adjusted_audio.get_array_of_samples()).astype(np.float32) / 32767

    if output_path:
        adjusted_audio.export(output_path, format="wav")

    return data, adjusted_audio.frame_rate
