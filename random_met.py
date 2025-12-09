import numpy as np
from scipy.io.wavfile import write

# Parameters
sample_rate = 44100  # Samples per second
bpm = 100  # Beats per minute
beat_duration = 60 / bpm  # Duration of each beat in seconds
num_beats = 60  # Total number of beats
freq_normal = 1000  # Frequency of normal beat (Hz)
freq_high = 1500  # Frequency of accented high beat (Hz)
freq_low = 750  # Frequency of accented low beat (Hz)
tone_duration = 0.1  # Duration of each tone in seconds

# Generate individual beat tone

def generate_tone(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    tone = 0.5 * np.sin(2 * np.pi * frequency * t)
    return tone

# Generate metronome sequence
silence_duration = beat_duration - tone_duration
silence = np.zeros(int(sample_rate * silence_duration))

audio = []
for i in range(num_beats):
    if i % 8 == 0:  # Every 8th beat
        frequency = np.random.choice([freq_high, freq_low])
    else:
        frequency = freq_normal
    tone = generate_tone(frequency, tone_duration, sample_rate)
    audio.extend(tone)
    audio.extend(silence)

# Convert to NumPy array and save
audio = np.array(audio, dtype=np.float32)
write("metronome.wav", sample_rate, audio)

print("Metronome audio file 'metronome.wav' generated successfully!")
