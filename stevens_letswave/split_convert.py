import random

'''
TODO: do we need to randomize
TODO: 

'''

# Assuming the total length of your dataset
total_length = 11965  # Replace with the actual length of your dataset

# Lengths of each split
train_len = 7970
val_len = 1998
test_len = 1997

# Generate a list of indices from 0 to total_length - 1
indices = list(range(total_length))

# Shuffle the indices to ensure random distribution
random.shuffle(indices)

# Split the indices into train, val, and test
train_indices = indices[:train_len]
val_indices = indices[train_len:train_len + val_len]
test_indices = indices[train_len + val_len:]

# Create the splits list
splits = []

# Shuffle indices again for each split
random.shuffle(indices)
train_indices = indices[:train_len]
val_indices = indices[train_len:train_len + val_len]
test_indices = indices[train_len + val_len:]

split = {
    'train': train_indices,
    'val': val_indices,
    'test': test_indices
}
splits.append(split)

# Example print to check one of the splits
print(f"Train split length: {len(splits[0]['train'])}")
print(f"Val split length: {len(splits[0]['val'])}")
print(f"Test split length: {len(splits[0]['test'])}")
