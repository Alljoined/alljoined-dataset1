import numpy as np
from psychopy import visual, core, event, gui, data, logging
from os import path, makedirs
import json
import random

# Placeholder function for EEG setup and trigger recording
def setup_eeg():
    # Initialize EEG, e.g., with Emotiv SDK
    # This function needs to be implemented based on your EEG SDK's documentation
    pass

def record_trigger(trigger_number, debug_mode=True):
    # Record or send a trigger to the EEG device
    # This part needs to be adapted based on your EEG device's API
    if debug_mode:
        logging.log(level=logging.DATA, msg=f"Trigger recorded: {trigger_number}")
    else:
        pass # Implement actual trigger recording here

# Create trials for the experiment
def create_trials(n_images, n_oddballs, num_blocks, img_width, img_height, window_size):
    trials = []
    coords = [window_size[0]/2 - img_width/2, window_size[1]/2 - img_height/2,
              window_size[0]/2 + img_width/2, window_size[1]/2 + img_height/2]

    for block in range(num_blocks):
        # Generate trials for each block
        images = list(range(1, n_images + 1)) * 2  # Example: two repeats, adapt as needed
        oddballs = [-1] * n_oddballs
        block_trials = images + oddballs
        random.shuffle(block_trials)

        for trial in block_trials:
            trials.append({'block': block + 1, 'trial': trial, 'coords': coords})

    return trials

# Main experiment
def run_experiment(trials, window):
    # Setup stimuli presentation
    for trial in trials:
        # Check for escape key press to exit early
        if 'escape' in event.getKeys():
            print("Experiment terminated early.")
            break  # Break out of the loop


        if trial['trial'] == -1:
            # This is an oddball trial; adapt handling as needed
            pass
        else:
            # Regular trial
            # Placeholder for image loading and presentation
            # For actual experiment, load the image based on trial['trial'] identifier
            stim = visual.Rect(win=window, width=100, height=100, fillColor='white', pos=(0, 0))
            stim.draw()

        window.flip()
        core.wait(0.5)  # Display time, adapt as needed

        # Record response
        # Here, implement response collection and timing
        # e.g., reaction time measurement, accuracy calculation

        window.flip()
        core.wait(0.2)  # ISI - inter-stimulus interval

        # Record a placeholder trigger
        record_trigger(99)  # Replace 99 with actual trigger number

    # End of experiment, clean up
    window.close()

def main():
    # Experiment setup
    participant_info = {'ID': '', 'Session': '1'}
    dlg = gui.DlgFromDict(dictionary=participant_info, title='Experiment Info')
    if not dlg.OK:
        core.quit()

    # Setup window
    window = visual.Window(fullscr=True, color=[0, 0, 0])
    window_size = window.size

    # Setup EEG
    setup_eeg()

    # Parameters
    n_images = 60  # Number of images
    n_oddballs = 24  # Number of oddball images
    num_blocks = 16  # Number of blocks
    img_width, img_height = 425, 425

    trials = create_trials(n_images, n_oddballs, num_blocks, img_width, img_height, window_size)

    # Run the experiment
    run_experiment(trials, window)

    # Save results
    # This is where you would implement saving the collected data
    # e.g., response times, accuracy, etc., to a file

if __name__ == '__main__':
    main()
