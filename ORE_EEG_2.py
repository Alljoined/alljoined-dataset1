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
        logging.log(level=logging.DATA,
                    msg=f"Trigger recorded: {trigger_number}")
    else:
        pass  # Implement actual trigger recording here


def validate_block(block_trials):
    prev = -1
    for trial in block_trials:
        if trial == prev:
            return False
        prev = trial
    return True


def create_trials(n_images, n_oddballs, num_blocks, img_width, img_height, window_size):
    trials = []
    num_block_repeats = num_blocks // 8  # 8 unique blocks in a row

    for repeat in range(num_block_repeats):
        for block in range(8):
            isValidBlock = False
            block_trials = []
            while not isValidBlock:
                # Generate trials for each block
                start = 1
                end = start + n_images
                # Example: two repeats, adapt as needed
                images = list(range(start, end)) * 2
                oddballs = [-1] * n_oddballs
                block_trials = images + oddballs
                random.shuffle(block_trials)
                # ensure no two consecutive trials are the same
                isValidBlock = validate_block(block_trials)

            for idx, trial in enumerate(block_trials):
                trials.append({'block': (block + 1) * (repeat + 1), 'trial': trial,
                              'end_of_block': (idx == len(block_trials) - 1)})

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

    for i in range(len(loaded_data)):
        img_data = loaded_data[i]
        img_array = np.uint8(img_data)

        # Create a temporary PNG file for the current image.
        # This temporary file is used to store the image data in a format that PsychoPy can display.
        # The 'delete=False' argument prevents the file from being deleted as soon as it is closed,
        # allowing us to use the file path for display in PsychoPy.
        with NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            Image.fromarray(img_array).save(tmp.name)
            # Save the path to the temporary file for later use.
            images.append(tmp.name)

    # Print the total number of images
    print(f"\nTotal number of images loaded: {len(images)} \n")
    return images


def select_block_images(all_images, block_number, n_images):
    # Mod operator is used to ensure that blocks 9-16 are the same as block 1-8
    start_index = ((block_number - 1) % 8) * n_images
    end_index = start_index + n_images
    return all_images[start_index:end_index]


def display_instructions(window, session_number):
    instruction_text = (
        f"Welcome to block {session_number} of the study.\n\n"
        "In this session, you will complete a perception task.\n"
        "This session consists of 16 experimental blocks.\n\n"
        "You will see sequences of images appearing on the screen, your task is to "
        "press the space bar when you see an image appear twice in a row.\n\n"
        "When you are ready, press the space bar to start."
    )

    # Assuming a window width of 800 pixels, adjust this based on your actual window size
    # Use 80% of window width for text wrapping
    wrap_width = window.size[0] * 0.8

    message = visual.TextStim(window, text=instruction_text, pos=(
        0, 0), color=(1, 1, 1), height=40, wrapWidth=wrap_width)
    message.draw()
    window.flip()
    event.waitKeys(keyList=['space'])


def run_experiment(trials, window, subj, session_number, n_images, all_images):
    last_image = None

    current_block = 1  # Initialize the current block counter
    # Initialize an empty list to hold the image numbers for the current block
    image_sequence = []

    for idx, trial in enumerate(trials):
        if 'escape' in event.getKeys():
            print("Experiment terminated early.")
            break

        if trial['block'] != current_block:
            current_block = trial['block']
            start_index = ((current_block - 1) % 8) * n_images
            end_index = start_index + n_images
            print(f"\nBlock {current_block}, Start Index: {start_index}")
            print(f"Block {current_block}, End Index: {end_index}\n")

        block_images = select_block_images(
            all_images, trial['block'], n_images)
        # Adjust index for 0-based Python indexing
        image_path = block_images[trial['trial'] - 1]
        # Check if this trial is an oddball
        is_oddball = (trial['trial'] == -1)
        if is_oddball:
            image_path = last_image
        else:
            last_image = image_path

        # Append current image number to the sequence list
        image_sequence.append(trial['trial'])

        # Logging the trial details
        print(
            f"Block {trial['block']}, Trial {idx + 1}: Image {trial['trial']} {'(Oddball)' if is_oddball else ''}")

        # Display the image
        image_stim = visual.ImageStim(
            win=window, image=image_path, pos=(0, 0), size=(448, 448))
        image_stim.draw()
        window.flip()
        core.wait(0.3)  # Display time

        # Rest screen with a fixation cross
        display_cross_with_jitter(window, 0.3, 0.05)

        # Record a placeholder trigger
        record_trigger(99)

        # Check if end of block
        if trial['end_of_block']:
            # Print the image sequence for the current block
            print(
                f"\nEnd of Block {trial['block']} Image Sequence: \n {', '.join(map(str, image_sequence))}")
            # Clear the list for the next block
            image_sequence = []

            # Display break message at the end of each block
            display_break_message(window, trial['block'])

    # Display completion message
    display_completion_message(window)

    # Cleanup: Remove temporary image files
    for img_path in all_images:
        os.remove(img_path)

    window.close()
    core.quit()


def display_break_message(window, block_number):
    message = f"You've completed block {block_number}.\n\nTake a little break and press the space bar when you're ready to continue to the next block."
    break_message = visual.TextStim(window, text=message, pos=(
        0, 0), color=(1, 1, 1), height=40, wrapWidth=window.size[0] * 0.8)
    break_message.draw()
    window.flip()
    event.waitKeys(keyList=['space'])


def display_completion_message(window):
    completion_text = "Congratulations! You have completed the experiment.\n\nPress the space bar to exit."
    completion_message = visual.TextStim(window, text=completion_text, pos=(
        0, 0), color=(1, 1, 1), height=40, wrapWidth=window.size[0] * 0.8)
    completion_message.draw()
    window.flip()
    event.waitKeys(keyList=['space'])


def display_cross_with_jitter(window, base_time, jitter):
    rest_period = base_time + random.randint(0, int(jitter * 100)) / 100.0
    fixation_cross = visual.TextStim(
        window, text='+', pos=(0, 0), color=(1, 1, 1), height=40)
    fixation_cross.draw()
    window.flip()
    core.wait(rest_period)


def main():
    # Experiment setup
    participant_info = {'Subject': '', 'Session': '1'}
    dlg = gui.DlgFromDict(dictionary=participant_info, title='Experiment Info')
    if not dlg.OK:
        core.quit()

    # Setup window
    window = visual.Window(fullscr=True, color=[0, 0, 0], units='pix')

    # Load and shuffle images before displaying instructions
    all_images = load_images_from_mat(
        participant_info['Subject'], participant_info['Session'])

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

    trials = create_trials(n_images, n_oddballs, num_blocks,
                           img_width, img_height, window_size)

    # Run the experiment
    run_experiment(
        trials, window, participant_info['Subject'], participant_info['Session'], n_images, all_images)

    # Save results
    # This is where you would implement saving the collected data
    # e.g., response times, accuracy, etc., to a file


if __name__ == '__main__':
    main()
