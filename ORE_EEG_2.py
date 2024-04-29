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
    prev = -1
    for trial in block_trials:
        if trial == prev:
            return False
        prev = trial
    return True

def create_trials(n_images, n_oddballs, num_blocks, img_width, img_height, window_size):
    trials = []
    for block in range(num_blocks):
        # Step 1: Shuffle the unique images
        images = list(range(1, n_images + 1))
        random.shuffle(images)

        # Step 2: Create a boolean array of size 120 and initialize to False
        oddball_flags = [False] * n_images

        # Step 3: Randomly pick indices and set them to True
        oddball_positions = []
        while len(oddball_positions) < n_oddballs:
            index = random.randint(0, n_images - 1)
            if not oddball_flags[index] and (index == 0 or not oddball_flags[index - 1]) and (index == n_images - 1 or not oddball_flags[index + 1]):
                oddball_flags[index] = True
                oddball_positions.append(index)

        # Step 4: Identify the images at the oddball positions
        oddball_images = [images[i] for i in oddball_positions]

        # Step 5: Recreate the array with duplicated oddball images
        block_trials = []
        for i in range(n_images):
            block_trials.append(images[i])
            if oddball_flags[i]:
                block_trials.append(images[i])

        # Append trials with block information
        for idx, trial in enumerate(block_trials):
            trials.append({
                'block': block + 1,
                'trial': trial,
                'end_of_block': (idx == len(block_trials) - 1)  # Mark the end of a block
            })

    return trials

def load_images_from_mat(subj, session_number):
    filename = f'processed-stimulus/coco_file_224_sub{subj}_ses{session_number}.mat'
    loaded_data = loadmat(filename, simplify_cells=True)['coco_file']  
    images = []

    for i in range(len(loaded_data)):
        img_data = loaded_data[i]
        img_array = np.uint8(img_data)

        with NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            Image.fromarray(img_array).save(tmp.name)
            images.append(tmp.name)  # Save the path to the temporary file for later use.

    print(f"\n\nTotal number of images loaded: {len(images)} \n\n")  # Print the total number of images
    return images

def load_and_shuffle_images(subj, session_number):
    filename = f'processed-stimulus/coco_file_224_sub{subj}_ses{session_number}.mat'
    loaded_data = loadmat(filename, simplify_cells=True)['coco_file']  
    images = []

    for i in range(len(loaded_data)):
        img_data = loaded_data[i]
        img_array = np.uint8(img_data)

        with NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            Image.fromarray(img_array).save(tmp.name)
            images.append(tmp.name)  # Save the path to the temporary file for later use.

    print(f"\n\nTotal number of images loaded: {len(images)} \n\n")  # Print the total number of images
    random.shuffle(images)  # Shuffle all the loaded images
    return images

def select_block_images(all_images, block_number, n_images):
    # Mod operator is used to ensure that blocks 9-16 are the same as block 1-8
    start_index = ((block_number - 1) % 8) * n_images
    end_index = start_index + n_images
    return all_images[start_index:end_index]


def display_instructions(window, session_number):
    instruction_text1 = (
        f"Welcome to session {session_number} of the study.\n\n"
        "In this session, you will complete a perception task.\n"
        "This session consists of one training block and 16 experimental blocks.\n\n"
        "You will see sequences of faces appearing on the screen, your task is to "
        "press the space bar when you see a face appear twice in a row.\n\n"
        "Press the space bar to continue."
    )
    instruction_text2 = (
        "This is the training block.\n\n"
        "You will see sequences of faces appearing on the screen, your task is to "
        "press the space bar when you see a face appear twice in a row.\n\n"
        "When you are ready, press the space bar to start."
    )

    # Assuming a window width of 800 pixels, adjust this based on your actual window size
    wrap_width = window.size[0] * 0.8  # Use 80% of window width for text wrapping

    message1 = visual.TextStim(window, text=instruction_text1, pos=(0, 0), color=(1, 1, 1), height=40, wrapWidth=wrap_width)
    message1.draw()
    window.flip()
    event.waitKeys(keyList=['space'])

    window.flip()
    core.wait(0.5)

    message2 = visual.TextStim(window, text=instruction_text2, pos=(0, 0), color=(1, 1, 1), height=40, wrapWidth=wrap_width)
    message2.draw()
    window.flip()
    event.waitKeys(keyList=['space'])


def run_experiment(trials, window, subj, session_number, n_images):
    all_images = load_and_shuffle_images(subj, session_number)
    last_image = None
    last_trial_number = None  # Track the last trial number to detect oddballs

    current_block = 1  # Initialize the current block counter
    image_sequence = []  # Initialize an empty list to hold the image numbers for the current block

    for idx, trial in enumerate(trials):
        if trial['block'] != current_block:
            current_block = trial['block']
            start_index = ((current_block - 1) % 8) * n_images
            end_index = start_index + n_images
            print(f"\nBlock {current_block}, Start Index: {start_index}")
            print(f"Block {current_block}, End Index: {end_index}\n")

        block_images = select_block_images(all_images, trial['block'], n_images)
        image_path = block_images[trial['trial'] - 1]  # Adjust index for 0-based Python indexing
        is_oddball = (trial['trial'] == last_trial_number)  # Check if this trial is an oddball

        # Append current image number to the sequence list
        image_sequence.append(trial['trial'])

        # Logging the trial details
        print(f"Block {trial['block']}, Trial {idx + 1}: Image {trial['trial']} {'(Oddball)' if is_oddball else ''}")

        # Display the image
        image_stim = visual.ImageStim(win=window, image=image_path, pos=(0, 0), size=(448, 448))
        image_stim.draw()
        window.flip()
        core.wait(0.3)  # Display time

        last_trial_number = trial['trial']  # Update the last trial number

        # Rest screen with a fixation cross
        display_cross_with_jitter(window, 0.3, 0.05)

        # Record a placeholder trigger
        record_trigger(99)

        # Check if end of block
        if trial['end_of_block']:
            # Print the image sequence for the current block
            print(f"End of Block {trial['block']} Image Sequence: \n {', '.join(map(str, image_sequence))}")
            # Clear the list for the next block
            image_sequence = []

            # Display break message at the end of each block
            display_break_message(window, trial['block'])

    # Cleanup: Remove temporary image files
    for img_path in all_images:
        os.remove(img_path)

    window.close()
    core.quit()


def display_break_message(window, block_number):
    message = f"You've completed block {block_number}. Take a little break and press the space bar when you're ready to continue to the next block."
    break_message = visual.TextStim(window, text=message, pos=(0, 0), color=(1, 1, 1), height=40, wrapWidth=window.size[0] * 0.8)
    break_message.draw()
    window.flip()
    event.waitKeys(keyList=['space'])

def display_cross_with_jitter(window, base_time, jitter):
    rest_period = base_time + random.randint(0, int(jitter * 100)) / 100.0
    fixation_cross = visual.TextStim(window, text='+', pos=(0, 0), color=(1, 1, 1), height=40)
    fixation_cross.draw()
    window.flip()
    core.wait(rest_period)

def display_block_end_message(window, block_number, total_blocks):
    message = f"You have completed {block_number} out of {total_blocks} blocks.\nTake a short rest\nPress Space to continue"
    wrap_width = window.size[0] * 0.8  # Same wrap width as instructions
    block_message = visual.TextStim(window, text=message, pos=(0, 0), color=(1, 1, 1), height=40, wrapWidth=wrap_width)
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
    window = visual.Window(fullscr=True, color=[0, 0, 0], units='pix')

    # Display instructions
    display_instructions(window, participant_info['Session'])

    # Setup EEG
    setup_eeg()

    # Parameters
    n_images = 120  # Number of unique images
    n_oddballs = 24  # Number of oddball images
    num_blocks = 16  # Number of blocks
    img_width, img_height = 425, 425  # Define image dimensions
    window_size = window.size

    trials = create_trials(n_images, n_oddballs, num_blocks, img_width, img_height, window_size)

    # Run the experiment
    run_experiment(trials, window, participant_info['Subject'], participant_info['Session'], n_images)

    # Save results
    # This is where you would implement saving the collected data
    # e.g., response times, accuracy, etc., to a file

if __name__ == '__main__':
    main() 