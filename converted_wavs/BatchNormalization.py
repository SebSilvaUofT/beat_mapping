# Batch normalization script to measure the LUFS of all wav files in a folder and set them to a stardard value.
# also checks for dbfs peaks that would result in clipping.

import soundfile as sf
import pyloudnorm as pyln

data, rate = sf.read("test.wav") # load audio (with shape (samples, channels))
meter = pyln.Meter(rate) # create BS.1770 meter
loudness = meter.integrated_loudness(data) # measure loudness