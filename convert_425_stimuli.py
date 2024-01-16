import h5py
import numpy as np
from scipy.io import savemat

with h5py.File('./stimulus/nsd_stimuli.hdf5', 'r') as source_hdf5:
    # Define the number of images to save
    num_images = 100

    # Initialize an array to store the images
    cell_array = np.empty((num_images, 1), dtype=object)

    # Loop through and copy the first 1000 images from the source
    for i in range(num_images):
        print(f"Loading image {i+1}/{num_images}")
        # Read the ith image in (425, 425, 3) dimension
        image_data = source_hdf5['/imgBrick'][i, ...]

        # Add to image to our cell array
        cell_array[i, 0] = image_data

# Create a dictionary to store the data
mat_data = {'coco_file': cell_array}

# Save the data to a .mat file
savemat('coco_file_2.mat', mat_data)

print("Data saved to coco_file_2.mat")