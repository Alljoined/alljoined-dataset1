import h5py
import torch
import os
import re

def process_mat_files(directory):
    result = {"dataset": [], "images": [0] * 960, "labels": [0] * 960}
    y = 0
    files = sorted(os.listdir(directory))
    # Iterate through all .mat files in the directory
    for file_name in files:
        if file_name.endswith('.mat'):
            # Extract image ID and subject ID from file name
            image_id, subject_id = extract_ids(file_name)

            # Update images and labels lists
            if 0 <= image_id - 1 < 960:
                result["images"][image_id - 1] = image_id
                result["labels"][image_id - 1] = image_id

            with h5py.File(os.path.join(directory, file_name), 'r') as file:
                data = file['data']  

                # Process each of the 4 repeats
                for i in range(4):
                    dataset_entry = {'eeg': None, 'image': image_id - 1, 'label': image_id - 1, 'subject': subject_id}
                    
                    # Reshape and convert data to tensor
                    eeg_data = torch.tensor(data[:, :, :, :, :, i].reshape(64, 333))
                    dataset_entry['eeg'] = eeg_data

                    # Add entry to result
                    result["dataset"].append(dataset_entry)
                    y += 1

    return result

def extract_ids(file_name):
    # Regex pattern to extract image ID and subject ID
    pattern = r"stim (\d+).*subj(\d+).mat"
    match = re.search(pattern, file_name)
    if match:
        return int(match.group(1)), int(match.group(2))
    else:
        return 0, 0  

# Use the function
processed_data = process_mat_files('./')
print(processed_data)
