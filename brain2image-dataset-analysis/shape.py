import torch

file_path = 'tmp/eeg_5_95_std.pth'
# file_path = 'tmp/block_splits_by_image_all.pth'

# Load the .pth file
data = torch.load(file_path)

print()

# Function to print the structure of an object
def print_structure(obj, name):
    if isinstance(obj, dict):
        print(f"{name} is a dictionary with keys: {list(obj.keys())}")
        for key, value in obj.items():
            print_structure(value, f"{name}[{key}]")
    elif isinstance(obj, list):
        print(f"{name} is a list with length {len(obj)}")
        if len(obj) > 0:
            print_structure(obj[0], f"{name}[0]")
    elif isinstance(obj, torch.Tensor):
        print(f"{name} is a tensor with shape {obj.shape}")
    else:
        print(f"{name} is a {type(obj)}. Example: {obj}")

# Print the structure of each key in the main dictionary
for key in data.keys():
    print_structure(data[key], key)
