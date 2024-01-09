import h5py
import numpy as np
from scipy.io import savemat

file_path = r"C:\Users\jonat\Documents\coding\matlab_preprocessing\datasets--pscotti--mindeyev2\snapshots\2996c8186484bce80304442676ffeb351d35a62d\coco_images_224_float16.hdf5"

# Load HDF5 file
with h5py.File(file_path, 'r') as file:
    images = np.array(file['images'])

# Prepare the data for saving in .MAT format
# MATLAB prefers dictionaries
subset = images[:100]
subset = (subset * 255).astype(np.uint8)
num_images = len(subset)

cell_array = np.empty((num_images, 1), dtype=object)

# Insert each image into the cell array as a uint8 array.
for i in range(num_images):
    # Transpose the image from (3, 224, 224) to (224, 224, 3) and ensure it's uint8
    cell_array[i, 0] = np.transpose(subset[i], (1, 2, 0))

# Save the cell array to a .mat file.
savemat('coco_file.mat', {'coco_file': cell_array})