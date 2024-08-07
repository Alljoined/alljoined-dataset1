import csv
from scipy.io import loadmat
import mne
import pandas as pd
import os

DATA_FOLDER = '/srv/eeg_reconstruction/shared/biosemi-dataset'
LO_HI = "05_125"

def load_csv_to_list(csv_filepath):
    """
    Reads a CSV file and converts it into a list of tuples.

    Parameters:
    - csv_filepath: Path to the CSV file.

    Returns:
    - A list of tuples, where each tuple contains [image number, cocoId].
    """
    data = []
    with open(csv_filepath, mode='r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)
        for idx, row in enumerate(reader):
            # Convert the first, second columns to int 
            if row[0] == '':
                print(f"Row index: {idx} is blank")
                continue
            else:
                data.append((int(row[0]), int(row[1])))
    return data



def get_nsd_indices(mat_contents, subject, session):
    """
    Returns the NSD image ID for a given subject, session, and id.

    Parameters:
    - mat_contents: The contents loaded from the .mat file.
    - subject: The subject number (1-indexed).
    - session: The session number (1-indexed).
    - id: The index within the session (0-999).

    Returns:
    - Image ID corresponding to the specified subject, session, and id.
    """

    if session % 2 == 0:  # For even sessions, use shared images
        indices = mat_contents['sharedix'][0]
    else:
        indices = mat_contents['subjectim'][subject - 1]  # Adjust for 0-indexing

    # Fetch and return the image ID using the global index.
    return indices


def get_coco_id(csv_data, index):
    """
    Returns the COCO ID for a given index from CSV data.

    Parameters:
    - csv_data: A list of tuples/lists where each tuple/list contains [image number, cocoId].
    - index: The 0-based image number to find the COCO ID for.

    Returns:
    - The COCO ID corresponding to the given index.
    """
    for row in csv_data:
        if row[0] == index:
            return row[1]
    return None  # Return None if the index is not found


def load_fiff_epochs(fiff_file_path):
    """
    Load FIFF data file as epochs.
    
    Parameters:
    - fiff_file_path: Path to the FIFF file.
    
    Returns:
    - epochs: Loaded MNE epochs object.
    """
    epochs = mne.read_epochs(fiff_file_path, preload=True)
    print("Epochs loaded successfully.")
    return epochs


def generate_dataset(fiff_file_path, conversion_csv_data, mat_contents):
    """
    Generates a dataset by combining EEG data with image IDs and timing information.

    Parameters:
    - fiff_file_path: Path to the FIFF file containing EEG data.
    - csv_file_path: Path to the CSV file containing trial information.
    - conversion_csv_data: List of tuples containing mapping from image number to COCO ID.
    - mat_contents: Contents of the .mat file containing NSD experiment design.

    Returns:
    - A pandas DataFrame containing the combined dataset.
    """
    epochs = load_fiff_epochs(fiff_file_path)

    # Extract subject and session from FIFF file name
    base_name = os.path.basename(fiff_file_path)
    subject, session = base_name.split('_')[0][4:], base_name.split('_')[1].split('.')[0][7:]

    subject = int(subject) 
    session = int(session)  
    nsd_indices = get_nsd_indices(mat_contents, subject, session)

    dataset = []
    block = 1

    for i, event in enumerate(epochs.events):
        trial = i + 1

        # Extract EEG data for the trial
        eeg_data = epochs[i].get_data(copy=False).squeeze()  # Extracting EEG data for the ith trial
        # eeg_data = pickle.dumps(eeg_data, protocol=4)
        onset = event[0]
        image_id = event[2] - 1 # Triggers are sent between [1, 960]

        if image_id > 120 * (block % 8):
            block += 1
        elif block == 8 and image_id < 120:
            block = 9

        # Extract other attributes
        nsd_id = nsd_indices[image_id] - 1 # NSD Indices count from 1
        coco_id = get_coco_id(conversion_csv_data, nsd_id)  
        curr_time = onset / 512

        # Append to the dataset
        dataset.append({
            "subject_id": subject,
            "session": session,
            "block": block,
            "trial": trial,
            "73k_id": nsd_id,
            "coco_id": coco_id,
            "eeg": eeg_data,  
            "curr_time": curr_time
        })

    # Convert dataset to DataFrame
    dataset_df = pd.DataFrame(dataset)
    return dataset_df


def process_all_datasets(eeg_data_folder, conversion_csv_data, nsd_mat_contents):
    # Find all FIFF files in the final_eeg folder
    fif_files = os.path.join(eeg_data_folder, "final_eeg", LO_HI)

    for file in os.listdir(fif_files):
        # if file.endswith('_epo.fif'):
        if file == "subj08_session2_epo.fif":
            # Generate the dataset
            print("generating dset for", file)
            dataset = generate_dataset(os.path.join(fif_files, file), conversion_csv_data, nsd_mat_contents)

            output_name = os.path.basename(file)[:-8] + ".h5"
            output_path = os.path.join(eeg_data_folder, "final_hdf5", LO_HI,  output_name)
            dataset.to_hdf(output_path, key='df', complib='blosc', complevel=9)
            print(f"Dataset saved to {output_path}")

# Load conversion CSV data and .mat contents outside the loop to avoid reloading for each file
conversion_csv_filepath = 'nsd_coco_conversion.csv'  
conversion_csv_data = load_csv_to_list(conversion_csv_filepath)

nsd_mat_file_path = 'nsd_expdesign.mat'
nsd_mat_contents = loadmat(nsd_mat_file_path)

# Process all datasets
process_all_datasets(DATA_FOLDER, conversion_csv_data, nsd_mat_contents)
