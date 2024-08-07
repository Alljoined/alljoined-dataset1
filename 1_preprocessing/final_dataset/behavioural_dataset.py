import pandas as pd
import os

""" 
This script is responsible for building the behavioural data
    portion of the final dataset in the Post-LetsWave6 format.
    The created table does not have non-oddball, no-press events.
"""

SUBJECT_ID = 4
SESSION = 2

DATASET_COLUMNS = [
    "subject_id",
    "session",
    "block",
    "curr_time",
    "is_oddball",
    "pressed",
    "reaction_time"
]

EVENT_CODES = {
    "BLOCK_START": 65536,
    "CORRECT_REJ": 252, # Not oddball, not pressed
    "FALSE_ALARM": 253, # Not oddball, pressed
    "CORRECT_HIT": 254, # Oddball, pressed
    "MISS": 251,        # Oddball, not pressed
    "ODDBALL_START": 151, # Oddball codes go from 151 to 166
    "ODDBALL_END": 166
}

def log_error(message, row, trial):
    print(f"Error: {message} occured in row {row}, corresponding trial: {trial}")

def convert_raw_eeg_to_letswave6(
        subject_id: int,
        session: int,
        raw_eeg_df: pd.DataFrame,
        sample_rate: int = 512
        ) -> pd.DataFrame:
    """
    Converts raw EEG data to the Post_LetsWave6 Format
    
    Parameters:
    - subject_id: subject id
    - session: the number of the session
    - raw_eeg_df: EEG data with the columns onset, sig, code.
    - sample_rate: sample rate of the EEG data

    Returns:
    - DataFrame with columns = [
        "subject_id",
        "session",
        "block",
        "curr_time",
        "is_oddball",
        "pressed",
        "reaction_time"
      ]
    """
    # We skip two rows, one is start signal, second is block start
    inital_rows_to_skip = 2 
    rows_per_trial = 3
    output = pd.DataFrame(columns=DATASET_COLUMNS)
    block = 1
    num_trials = 0

    for i in range(inital_rows_to_skip, len(raw_eeg_df), rows_per_trial):
        is_oddball = False
        pressed = False

        trial = raw_eeg_df.iloc[i: i + rows_per_trial]

        # Signal to indicate type of event
        trial_block_code = trial.iloc[0]["code"]
        # Signal to indicate if a user pressed a key
        trial_user_response_code = trial.iloc[2]["code"]
       
        curr_time = trial.iloc[1]["onset"] / sample_rate
        reaction_time = (trial.iloc[2]["onset"] - trial.iloc[1]["onset"]) / sample_rate

        if trial_block_code == block:
            # Regular trial event is occuring
            if trial_user_response_code == EVENT_CODES["CORRECT_REJ"]:
                continue
            elif trial_user_response_code == EVENT_CODES["FALSE_ALARM"]:
                pressed = True
        
        elif trial_block_code == EVENT_CODES["BLOCK_START"]:
            # New block is starting
            block += 1
            continue
        elif trial_block_code >= EVENT_CODES["ODDBALL_START"] and \
                trial_block_code <= EVENT_CODES["ODDBALL_END"]:
            # Oddball event
            is_oddball = True
            if trial_user_response_code == EVENT_CODES["CORRECT_HIT"]:
                pressed = True
        elif trial_block_code != block:
            log_error(f"Unexpected code: expected {block} - got {trial_block_code}",
                      i, trial)
        
        new_entry = {
            "subject_id": subject_id,
            "session": session,
            "block": block, 
            "curr_time": curr_time,
            "is_oddball": is_oddball,
            "pressed": pressed,
            "reaction_time": reaction_time
        }
        output.loc[num_trials] = new_entry
        num_trials += 1
    
    return output

if __name__ == "__main__":
    raw_csv_path = os.path.join("eeg_data", "raw_csv", "subj04_session2.csv")
    raw_eeg_df = pd.read_csv(raw_csv_path)
    eeg_letswave6 = convert_raw_eeg_to_letswave6(
        subject_id=SUBJECT_ID,
        session=SESSION,
        raw_eeg_df=raw_eeg_df
    )
    dataset_csv_path = raw_csv_path.replace("raw_csv", "behavioural_csv")
    os.makedirs(os.path.dirname(dataset_csv_path), exist_ok=True)
    eeg_letswave6.to_csv(dataset_csv_path, index=False)

