import sounddevice as sd
import numpy as np
import threading
from audio_helpers import load_audio
import threading
import keyboard
import time
import bisect


# this method executes a feedback session/ when provided a
def run_feedback(songdata1, song_rate1, metdata1, met_target_dB, base_param_val,
                 feedback_type, count_in_ends, timestamps, baseline_cad,
                 feedback_parameter):

    # create a threading event to stop the volume thread once feedback has
    # stopped
    feedback_stopped = threading.Event()

    # Create a global variable for the target dB level of track 2 for real-time adjustment
    global met1_real_time_target, real_time_stsr, real_time_error, \
        interbeat_duration, steps
    met1_real_time_target = met_target_dB
    interbeat_duration = 60 / baseline_cad  # interbeat duration in seconds
    print("interbeat duration: ", interbeat_duration)

    # Position pointer
    position = [0]
    steps = []
    # Function to record stance-time symmetry ratios, and decide wheither or not
    # to provide the participant feedback, in the form of a volume change to the
    # metronome
    def adjust_volume():
        global met1_real_time_target, real_time_stsr
        while not feedback_stopped.is_set():
            # collect stsrs for 5 gait cycles
            cycles = []
            # currently I am inputing the stsrs manually, so this will need to
            # be modified to get these values from the WBS
            while len(cycles) < 5:
                try:
                    cycles.append(float(input(
                        f"Enter latest stsr: ")))
                except ValueError:
                    print("Invalid input. Please enter a float value.")

            print("five cycles complete, update volume")
            # we are checking to see if for 4/5 gait cycles that symmetry
            # is worse or better, than make a volume change
            above_count = 0
            below_count = 0
            for cycle in cycles:
                if cycle * 100 // 3 > real_time_stsr * 100 // 3:
                    above_count += 1
                elif cycle * 100 // 3 < real_time_stsr * 100 // 3:
                    below_count += 1

            # if their symmetry has improved for 4/5 cycles
            if above_count >= 4:
                # provide rewarding feedback
                met1_real_time_target -= 3
                # and progress the symetry target
                real_time_stsr += 0.03
            # if their symmetry is worse for at least 4/5 cycles
            elif below_count >= 4:
                # provide corrective feedback
                met1_real_time_target += 3
                # and regress the symmetry target
                real_time_stsr -= 0.03
    # Define the function that will be executed when the spacebar is pressed
    def record_action(timestamp):
        global real_time_error, met1_real_time_target, steps
        # print("spacebar pressed")
        # get the playback time that the spacebar has been triggered
        # print("timestamp: ", timestamp)
        closest_beat = closest_element_sorted(
            timestamps, timestamp)
        # print("the closest beat: ", closest_beat)
        error = abs(timestamp - closest_beat) / interbeat_duration
        # print("error: ", error)
        if len(steps) > 9:
            print("ten steps recorded")
            above_count = 0
            below_count = 0
            for step_error in steps:
                if step_error * 100 // 3 < real_time_error * 100 // 3:
                    above_count += 1
                elif step_error * 100 // 3 > real_time_error * 100 // 3:
                    below_count += 1
            # if their symmetry has improved for 4/5 cycles (8/10 steps)
            if above_count >= 8:
                print("improvement")
                # provide rewarding feedback
                met1_real_time_target -= 3
                # and progress the symetry target
                real_time_error -= 0.03
            # if their symmetry is worse for at least 4/5 cycles
            elif below_count >= 8:
                print("regression")
                # provide corrective feedback
                met1_real_time_target += 3
                # and regress the symmetry target
                real_time_error += 0.03
            print("real_time_error:", real_time_error)
            steps = []

        steps.append(error)

    # Define a thread function to listen for the spacebar
    def spacebar_listener():
        # Set up a non-blocking keyboard event for spacebar
        keyboard.on_press_key("space", lambda _: record_action(position[0]
                                                               / song_rate1))

        # Keep the thread running to listen for keypresses
        keyboard.wait()  # Wait indefinitely for keypresses

    # def error_based_volume_adjustment():
    #     global met1_real_time_target, real_time_error
    #     while not feedback_stopped.is_set():
    #         steps = []
    #         while len(steps) < 10:
    #             if keyboard.is_pressed('space'):
    #                 print("spacebar pressed")
    #                 timestamp = position[0] / song_rate1
    #                 print("timestamp: ", timestamp)
    #                 closest_beat = closest_element_sorted(
    #                     timestamps, timestamp)
    #                 print("closest beat: ", closest_beat)
    #                 error = abs(timestamp - closest_beat) / interbeat_duration
    #                 print("error: ", error)
    #                 steps.append(error)
    #                 # Add a small delay to avoid multiple detections of the same
    #                 # key press
    #                 time.sleep(0.03)
    #         above_count = 0
    #         below_count = 0
    #         for step_error in steps:
    #             if step_error * 100 // 10 < real_time_error * 100 // 10:
    #                 above_count += 1
    #             elif step_error * 100 // 10 > real_time_error * 100 // 10:
    #                 below_count += 1
    #         # if their symmetry has improved for 4/5 cycles (8/10 steps)
    #         if above_count >= 8:
    #             # provide rewarding feedback
    #             met1_real_time_target -= 3
    #             # and progress the symetry target
    #             real_time_error -= 0.1
    #         # if their symmetry is worse for at least 4/5 cycles
    #         elif below_count >= 8:
    #             # provide corrective feedback
    #             met1_real_time_target += 3
    #             # and regress the symmetry target
    #             real_time_error += 0.1

    # Function to play the audio streams in sync
    def audio_callback(outdata, frames, time, status):
        global met1_real_time_target
        song_adjustment = 1
        track_adjustment = 1
        pos = position[0]
        # Handle end of file case
        if pos + frames > len(songdata1):
            frames = len(songdata1) - pos

        # Calculate the necessary adjustment to achieve the real-time target
        # dB level
        # for intensified music and combined feedback strategies, adjust the
        # music volume

        # while the count in is occuring, keep the music volume set to zero
        if pos / song_rate1 < count_in_ends:
            song_adjustment = 1
        else:
            if feedback_type == 'IM' or feedback_type == 'C':
                song_adjustment = 10 ** (
                        -1 * (met1_real_time_target - met_target_dB) / 20)
            # for the faded metronome and combined feedback strategies,
            # adjust the metronome volume
            if feedback_type == 'FM' or feedback_type == 'C':
                track_adjustment = 10 ** (
                        (met1_real_time_target - met_target_dB) / 20)

        # Mix the two tracks and make volume adjustments
        outdata[:frames] = songdata1[
                           pos:pos + frames] * song_adjustment + metdata1[
                                                                 pos:pos + frames] * track_adjustment

        # need to add a period at the start of the song that has the music
        # volume faded, maybe pass the 9th beat stamp, and before then keep
        # the music muted

        # Update position
        position[0] += frames

        # If at the end of the data, stop playback
        if position[0] >= len(songdata1):
            raise sd.CallbackStop

    if feedback_parameter == 'S':  # symmetry-based feedback
        real_time_stsr = base_param_val
        target_function = adjust_volume
    elif feedback_parameter == 'E':  # error-based feedback
        real_time_error = base_param_val
        target_function = spacebar_listener
    else:
        return 1


    # Start the volume adjustment thread for real-time control
    volume_thread = threading.Thread(target=target_function, daemon=True)
    volume_thread.start()

    # Play the audio

    with sd.OutputStream(samplerate=song_rate1, channels=songdata1.shape[1],
                         callback=audio_callback):
        sd.sleep(int(len(songdata1) / song_rate1 * 1000))
    # tell the volume thread to stop
    feedback_stopped.set()


def closest_element_sorted(lst, target):
    # Find the insertion point using bisect
    pos = bisect.bisect_left(lst, target)

    # If target is less than the first element
    if pos == 0:
        return lst[0]
    # If target is greater than the last element
    if pos == len(lst):
        return lst[-1]

    # Get the closest of the neighbors around the insertion point
    before = lst[pos - 1]
    after = lst[pos]

    # Compare which one is closer to the target
    if abs(before - target) <= abs(after - target):
        return before
    else:
        return after
