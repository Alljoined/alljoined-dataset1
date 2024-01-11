# Converts the hdf5 file of all images we downloaded from pscotti into a .mat file
# Originally in float, convert to int range 0-255. Also selecting specific index for testing

import h5py
import numpy as np
from scipy.io import savemat, loadmat

# file_path = r"C:\Users\jonat\Documents\coding\matlab_preprocessing\datasets--pscotti--mindeyev2\snapshots\2996c8186484bce80304442676ffeb351d35a62d\coco_images_224_float16.hdf5"
# label_path = r"C:\Users\jonat\Documents\coding\matlab_preprocessing\stimulus\nsd_expdesign.mat"

file_path = "/Users/tazik/Downloads/nsd_stimuli.hdf5"
label_path = "/Users/tazik/Downloads/matlab_preprocessing-main (1)/matlab_preprocessing-main/stimulus/nsd_expdesign.mat"

# Get image indexes
mat_contents = loadmat(label_path)
select_idx = mat_contents['sharedix'][0]

batch_size = 100  # Adjust this based on your memory constraints
num_images = len(select_idx)
num_batches = int(np.ceil(num_images / batch_size))

#Load h5 file 
with h5py.File(file_path, 'r') as file:
    cell_array = np.empty((num_images, 1), dtype=object)

    for batch in range(num_batches):
        start = batch * batch_size
        end = min(start + batch_size, num_images)
        batch_indices = select_idx[start:end]

        # Load a batch of images
        images = np.array(file['imgBrick'][batch_indices])
        images = (images * 255).astype(np.uint8)

        for i, img in enumerate(images):
            # Process each image and add it to the cell array
            # img = np.transpose(img, (1, 2, 0))  # Transpose the image
            # img = img[:, :, ::-1]  # Swap Red and Blue channels
            cell_array[start + i, 0] = img

        del images  # Free up memory

# Save the cell array to a .mat file.
savemat('coco_file.mat', {'coco_file': cell_array})


