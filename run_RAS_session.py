# Sebastian Silva, UOFT BME MASc Candidate
# PROPEL Lab, Bloorview Research Institute,
# Holland Bloorview Kids Rehab Hospital
import os

import pandas as pd
import time
from audio_helpers import PV_stretch, crossfade_songs
from gen_metronome_py9 import *
from feedback import *
import bisect


# this function can be called to initiate a RAS feedback session, provided a
# feedback type (Combined, FM, IM, or NF), two selected songs,
# the participant's baseline cadence, their baseline symmetry, and the initial
# volumes for each track (met and music)
def run_RAS_session(feedback_type, track1_id, track2_id, baseline_cad,
                    baseline_stsr, baseline_error, song_target_dB,
                    met_target_dB, shortened):

    # Open and read the tracklist
    tracklist_df = pd.read_json('tracklist.json')
    tracks = []
    # select the tracks and their metadata from the tracklist\
    for track in [track1_id, track2_id]:
        track_series = tracklist_df.loc[tracklist_df['track_id']
                                        == track].iloc[0]
        track_dict = track_series.to_dict()
        tracks.append(track_dict)

    trackdata = []
    metdata = []

    for track in tracks:
        OGtimestamps = track['beat timestamps']
        trackfile = r"Music Library/" + track['filename']

        if shortened:
            index = bisect.bisect_left(OGtimestamps, 10.0)
            OGtimestamps = OGtimestamps[:index]
            pre, ext = os.path.splitext(trackfile)
            trackfile = pre + "_shortened.wav"
            print(trackfile)


        # check if the participants baseline cadence is not matching the
        # song's original tempo. if so, a modified track must be generated
        if int(baseline_cad) != int(track['tempo']):

            # calculate the required stretching rate to generate a track that
            # matches the participant's baseline cadence
            s_rate = round(((track['tempo'] +
                             (baseline_cad - track['tempo']))
                            / track['tempo']), 2)
            # the time stretching is quite slow, hence the runtime tracking.
            print("generating stretched track...")
            start = time.time()  # tracking run time
            # call PV_stretch to generate a modified track

            track, rate = PV_stretch(trackfile, s_rate,
                                     song_target_dB)
            trackdata.append((track, rate))
            end = time.time()
            print("complete! track generation took: " + str(end - start) +
                  "s")

            # modify the timestamps by the stretch rate
            timestamps = [OGtimestamps[i] * (1 / s_rate)
                          for i in range(len(OGtimestamps))]

            metdata.append(timestamps)


        # if there is no difference between the participant's baseline
        # cadence and the song tempo, then no modified track needs to be
        # created
        else:
            metdata.append(OGtimestamps)
            track, rate = load_audio(trackfile, song_target_dB)
            trackdata.append((track, rate))

    # now we need to merge the two tracks for both the metronome and
    # music
    # first, get the 8th last timestamp of the first track
    first_song_8thlast_beat = metdata[0][-8]
    # now, get the first timestamp of the second track
    second_song_first_beat = metdata[1][0]
    # with this we can calulate when the second song should begin relative
    # to the first track
    second_song_start = first_song_8thlast_beat - second_song_first_beat
    print("first song length ", trackdata[0][0].duration_seconds)
    print (second_song_start)
    # crossfade_duration_in_ms = int((metdata[0][-1] - metdata[0][
    #     -8]) * 1000)
    crossfade_duration_in_ms = int((trackdata[0][0].duration_seconds -
                                    second_song_start) * 1000)
    print(crossfade_duration_in_ms)
    complete_song = crossfade_songs(trackdata[0][0],
                                    trackdata[1][0],
                                    int(second_song_start * 1000),
                                    crossfade_duration_in_ms)
    modified_second_track_beatstamps = [timestamp + second_song_start for
                                        timestamp in metdata[1]]
    complete_timestamps = (metdata[0][:-8] +
                           modified_second_track_beatstamps)
    met, met_rate = generate_metronome_track(complete_timestamps,
                                           met_target_dB)

    # the music track will be played at 0 dB until the participant has
    # recieved an 8 beat metronome count in. to achieve this, we can start
    # playing the music inbetween the 8th and 9th beat

    # count in will end halfway between the 8th and 9th beat
    count_in_ends = (metdata[0][7] + ((metdata[0][8] - metdata[0][7]) / 2))

    # if the participant's baseline symmetry is not perfect
    if (baseline_stsr * 100) < 97:
        # run the stance-time symmetry based feedback
        run_feedback(complete_song, trackdata[0][1], met,
                     met_target_dB, baseline_stsr, feedback_type, count_in_ends,
                     complete_timestamps, baseline_cad, 'S')

    # if the participant's symmetry is near-perfect, then run an
    # error-based feedback session
    else:
        run_feedback(complete_song, trackdata[0][1], met,
                     met_target_dB, baseline_error, feedback_type, count_in_ends,
                     complete_timestamps, baseline_cad, 'E')


run_RAS_session('C', '6XKvPNWlmnN0gJejCKm1k7',
                "4DX82Vc8qAH4jJPvKxvwg6",
                118, 0.98, 0.2, -20.0, -23.0,
                True,
                )
