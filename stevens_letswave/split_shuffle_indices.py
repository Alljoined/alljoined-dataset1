import random
import torch

total_length = 10000  # Replace with total length of the dataset

# Calculate lengths of each split
train_len = int(2/3 * total_length)  # 2/3 of total_length
val_len = int(1/6 * total_length)    # 1/6 of total_length
test_len = total_length - train_len - val_len  # Remaining for test

# Generate a list of indices from 0 to total_length - 1
indices = list(range(total_length))

# Shuffle the indices to ensure random distribution
random.shuffle(indices)

# Split the indices into train, val, and test
train_indices = indices[:train_len]
val_indices = indices[train_len:train_len + val_len]
test_indices = indices[train_len + val_len:]

# Create the splits dictionary
split = {
    'train': train_indices,
    'val': val_indices,
    'test': test_indices
}

# Example print to check the split
# print(f"Train split length: {len(split['train'])}")
# print(f"Val split length: {len(split['val'])}")
# print(f"Test split length: {len(split['test'])}")

# Export as .pth file
torch.save(split, 'split.pth')
