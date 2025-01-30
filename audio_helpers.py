import os
from io import BytesIO

import sounddevice as sd
import numpy as np
from scipy.io import wavfile
from pydub import AudioSegment
import audiosegment
import soundfile as sf
import pyrubberband as pyrb


# Function to generate a tone of given frequency and duration
def generate_tone(frequency, duration, sample_rate=44100, amplitude=0.5):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    signal = amplitude * np.sin(2 * np.pi * frequency * t)
    return signal


def play_track_sample(file_path):

    # Load WAV file
    sample_rate, data = wavfile.read(file_path)

    # Clip to 10 seconds of data
    clip_duration_seconds = 10
    clip_data = data[:clip_duration_seconds * sample_rate]

    # Play the clip
    sd.play(clip_data, samplerate=sample_rate)
    sd.wait()  # Wait until the sound finishes playing


def load_audio(file_path, target_dB):
    # Load audio file using pydub and convert to numpy array
    audio = AudioSegment.from_file(file_path)
    audio = audio.set_channels(2)  # Ensure stereo output

    # Calculate the adjustment needed to reach the target dB level
    change_in_dB = target_dB - audio.dBFS
    adjusted_audio = audio.apply_gain(change_in_dB)

    # Convert the adjusted audio to a numpy array
    # data = np.array(adjusted_audio.get_array_of_samples()).reshape(
    #     (-1, 2)).astype(np.float32) / (2 ** 15)
    samplerate = audio.frame_rate

    return adjusted_audio, samplerate


def PV_stretch(song_path, rate, target_dB):
    # read the file
    y, sr = sf.read(song_path)
    # apply phase vocoder stretching
    y_stretch = pyrb.time_stretch(y, sr, rate)
    y_stretch = (y_stretch * 32767).astype(np.int16)
    # Create a BytesIO buffer
    buffer = BytesIO()

    # Write the y_stretch data into the buffer as a WAV file
    sf.write(buffer, y_stretch, sr, format='WAV')

    # Move the buffer position to the beginning
    buffer.seek(0)

    # Create an AudioSegment from the buffer
    audio = AudioSegment.from_file(buffer, format="wav")
    # audio = AudioSegment.from_numpy_array(y_stretch, sr)
    audio = audio.set_channels(2)  # Ensure stereo output

    # Calculate the adjustment needed to reach the target dB level
    change_in_dB = target_dB - audio.dBFS
    adjusted_audio = audio.apply_gain(change_in_dB)

    # Convert the adjusted audio back to a numpy array
    # data = np.array(adjusted_audio.get_array_of_samples()).reshape(
    #     (-1, 2)).astype(np.float32) / (2 ** 15)
    samplerate = audio.frame_rate  # not sure if this is necessary

    return adjusted_audio, samplerate
    # write the stretched file to the music library
    # new_filepath = song_path + str(rate) + 'stretch.wav'
    # sf.write(new_filepath, y_stretch, sr)
    # return y_stretch, sr


def convert_m4a_to_wav(filename):
    # Load the .m4a file
    audio = AudioSegment.from_file(filename, format="m4a")
    # Export as .wav
    pre, ext = os.path.splitext(filename)
    audio.export(pre + ".wav", format="wav")


def crossfade_songs(song1: AudioSegment, song2: AudioSegment, start_time_in_ms,
                    crossfade_duration_in_ms):

    # Ensure start time for second song is within bounds
    if start_time_in_ms > len(song1):
        raise ValueError("Start time is beyond the length of the first song")
    # Make sure both songs have the same number of channels and sample rate
    song2 = song2.set_channels(song1.channels)
    song2 = song2.set_frame_rate(song1.frame_rate)

    # Split song1 into two parts: before and after the crossfade point
    # first_part = song1[:start_time_in_ms].fade_out(crossfade_duration_in_ms)

    # Apply fade-in to the second song

    # Concatenate the first part of song1 and the second part of song2
    crossfaded_song = song1.append(song2, crossfade=crossfade_duration_in_ms)
    crossfaded_song.export("fullSong.wav", format="wav")
    data = np.array(crossfaded_song.get_array_of_samples()).reshape(
        (-1, 2)).astype(np.float32) / (2 ** 15)
    return data

def shorten_wave_files(file1, file2, duration):
    """
    Shortens two wave files to a specified duration.

    Args:
        file1 (str): Path to the first wave file.
        file2 (str): Path to the second wave file.
        duration (float): Duration to shorten both files to, in seconds.
        output_file1 (str): Output path for the shortened first file. Default is 'shortened1.wav'.
        output_file2 (str): Output path for the shortened second file. Default is 'shortened2.wav'.
    """
    # Load the wave files using pydub
    audio1 = AudioSegment.from_wav(file1)
    audio2 = AudioSegment.from_wav(file2)

    # Convert the duration from seconds to milliseconds
    duration_ms = duration * 1000

    # Shorten both files to the specified duration
    shortened_audio1 = audio1[:duration_ms]
    shortened_audio2 = audio2[:duration_ms]
    pre1, ext1 = os.path.splitext(file1)
    pre2, ext2 = os.path.splitext(file2)
    output_file1 = pre1 + "_shortened.wav"
    output_file2 = pre2 + "_shortened.wav"

# Export the shortened files
    shortened_audio1.export(output_file1, format="wav")
    shortened_audio2.export(output_file2, format="wav")

    print(f"Files have been shortened and saved as {output_file1} and {output_file2}")
