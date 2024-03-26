import numpy as np
from psychopy import visual, core, event, gui, data, logging
import os
from scipy.io import loadmat
from PIL import Image
from tempfile import NamedTemporaryFile
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

def validate_block(block_trials):
    prev  = -1
    for trial in block_trials:
        if trial == prev:
            return False
        prev = trial
    return True

# Create trials for the experiment
def create_trials(n_images, n_oddballs, num_blocks, img_width, img_height, window_size):
    trials = []
    num_block_repeats = num_blocks // 8 # 8 unique blocks in a row

    for repeat in range(num_block_repeats):
        for block in range(8):
            isValidBlock = False
            block_trials = []
            while not isValidBlock:
                # Generate trials for each block
                start = block * n_images + 1
                end = start + n_images
                images = list(range(start, end)) * 2  # Example: two repeats, adapt as needed
                oddballs = [-1] * n_oddballs
                block_trials = images + oddballs
                random.shuffle(block_trials)
                # ensure no two consecutive trials are the same
                isValidBlock = validate_block(block_trials)

            for trial in block_trials:
                trials.append({'block': (block + 1) * repeat, 'trial': trial})

    return trials


def load_images_from_mat(subj, session_number):
    # Load the .mat file containing the images.
    # The parameter 'simplify_cells=True' makes nested structures in the .mat file 
    # easier to access by converting them into nested dictionaries or arrays.
    # This is particularly useful for MATLAB cell arrays and structures,
    # allowing for more Pythonic access to the data.
    # Note: 'simplify_cells' might not be available in all versions of SciPy.
    # If you encounter an error with this parameter, ensure you are using a compatible version of SciPy,
    # or you may need to manually navigate the nested structures without this parameter.
    filename = f'processed-stimulus/coco_file_224_sub{subj}_ses{session_number}.mat'
    loaded_data = loadmat(filename, simplify_cells=True)['coco_file']  
    images = []

    # Iterate through each item in the loaded image data.
    for i in range(len(loaded_data)):
        # Access the image data. Given the structure noted, each 'img_data' should be directly
        # an RGB image with the shape (224, 224, 3), meaning no additional reshaping or squeezing is needed.
        img_data = loaded_data[i]

        # Ensure the image data is in the expected uint8 format for image processing.
        # This step converts the MATLAB image data into a format suitable for creating an image file.
        img_array = np.uint8(img_data)

        # Create a temporary PNG file for the current image.
        # This temporary file is used to store the image data in a format that PsychoPy can display.
        # The 'delete=False' argument prevents the file from being deleted as soon as it is closed,
        # allowing us to use the file path for display in PsychoPy.
        with NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            Image.fromarray(img_array).save(tmp.name)
            images.append(tmp.name)  # Save the path to the temporary file for later use.

    return images


# Main experiment
def run_experiment(trials, window, subj, session_number):
    stim_images = load_images_from_mat(subj, session_number)

    last_image = None
    for trial in trials:
        if 'escape' in event.getKeys():
            print("Experiment terminated early.")
            break

        if trial['trial'] == -1 and last_image is not None:
            # Oddball trial, display the last image again
            image_path = last_image
        else:
            # Regular trial
            image_path = stim_images[trial['trial'] - 1]  # Adjust index for 0-based
            last_image = image_path
        
        # Display the image
        image_stim = visual.ImageStim(win=window, image=image_path, pos=(0, 0))
        image_stim.draw()
        window.flip()
        core.wait(0.3)  # Display time

        # Rest screen with a fixation cross
        display_cross_with_jitter(window, 0.3, 0.05)

        # Record a placeholder trigger
        record_trigger(99)

        # Block end message and wait for space press to continue, if end of block
        if trial.get('end_of_block', False):
            display_block_end_message(window, trial['block'], len(trials) // len(trial['block']))

    # Cleanup: Remove temporary image files
    for img_path in stim_images:
        os.remove(img_path)
    
    window.close()
    core.quit()

def display_cross_with_jitter(window, base_time, jitter):
    rest_period = base_time + random.randint(0, int(jitter * 100)) / 100.0
    fixation_cross = visual.TextStim(window, text='+', pos=(0, 0), color=(1, 1, 1))
    fixation_cross.draw()
    window.flip()
    core.wait(rest_period)

def display_block_end_message(window, block_number, total_blocks):
    message = f"You have completed {block_number} out of {total_blocks} blocks.\nTake a short rest\nPress Space to continue"
    block_message = visual.TextStim(window, text=message, pos=(0, 0), color=(1, 1, 1))
    block_message.draw()
    window.flip()
    event.waitKeys(keyList=['space'])

def main():
    # Experiment setup
    participant_info = {'Subject': '', 'Session': '1'}
    dlg = gui.DlgFromDict(dictionary=participant_info, title='Experiment Info')
    if not dlg.OK:
        core.quit()

    # Setup window
    window = visual.Window(fullscr=True, color=[0, 0, 0])
    window_size = window.size

    # Setup EEG
    setup_eeg()

    # Parameters
    n_images = 120  # Number of unique images
    n_oddballs = 24  # Number of oddball images
    num_blocks = 16  # Number of blocks
    img_width, img_height = 425, 425

    trials = create_trials(n_images, n_oddballs, num_blocks, img_width, img_height, window_size)

    # Run the experiment
    run_experiment(trials, window, participant_info['Subject'], participant_info['Session'])

    # Save results
    # This is where you would implement saving the collected data
    # e.g., response times, accuracy, etc., to a file

if __name__ == '__main__':
    main()
