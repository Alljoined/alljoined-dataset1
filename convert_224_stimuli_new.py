# Converts the hdf5 file of all images we downloaded from pscotti into a .mat file
# Originally in float, convert to int range 0-255. Also selecting specific index for testing

import h5py
import numpy as np
from scipy.io import savemat, loadmat

file_path = r"C:\srv\matlab_preprocessing\stimulus\datasets--pscotti--mindeyev2\snapshots\9b356f8332f385c4256a3a342fff9be3df4ef275\coco_images_224_float16.hdf5"
label_path = r"C:\srv\matlab_preprocessing\stimulus\nsd_expdesign.mat"

# Get image indexes
mat_contents = loadmat(label_path)
select_idx = mat_contents['sharedix'][0]

# Load HDF5 file
with h5py.File(file_path, 'r') as file:
    images = np.array(file['images'])

# Prepare the data for saving in .MAT format
# MATLAB prefers dictionaries
subset = images[select_idx]
subset = (subset * 255).astype(np.uint8)
num_images = len(subset)

cell_array = np.empty((num_images, 1), dtype=object)

# Insert each image into the cell array as a uint8 array.
for i in range(num_images):
    # Transpose the image from (3, 224, 224) to (224, 224, 3) and ensure it's uint8
    cell_array[i, 0] = np.transpose(subset[i], (1, 2, 0))

# Save the cell array to a .mat file.
savemat('coco_file.mat', {'coco_file': cell_array})