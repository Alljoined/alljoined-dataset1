import scipy.io
import torch

# Load the .mat file
mat = scipy.io.loadmat('your_file.mat')

# Assuming the .mat file has keys 'eeg_data', 'image_ids', 'labels', 'subjects'
# Update these keys based on your .mat file structure
eeg_data = mat['eeg_data']  # Replace with actual key
image_ids = mat['image_ids']  # Replace with actual key
labels = mat['labels']  # Replace with actual key
subjects = mat['subjects']  # Replace with actual key

# Initialize the dataset list
dataset = []

# Iterate through your data and populate the dataset
for i in range(len(eeg_data)):
    data_point = {
        'eeg': torch.tensor(eeg_data[i]),  # Convert to tensor
        'image': int(image_ids[i]),
        'label': int(labels[i]),
        'subject': int(subjects[i])
    }
    dataset.append(data_point)

# Extract unique labels and images if needed
unique_labels = list(set(labels))
unique_images = list(set(image_ids))

# Print some information for verification
print(f"Dataset length: {len(dataset)}")
print(f"Example dataset entry: {dataset[0]}")
print(f"Labels length: {len(unique_labels)}")
print(f"Images length: {len(unique_images)}")

# Assuming 'dataset' is your list of dictionaries as mentioned previously
torch.save(dataset, 'dataset.pth')

# To load this dataset in another script or session
loaded_dataset = torch.load('dataset.pth')