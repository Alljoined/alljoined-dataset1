import h5py
import numpy as np
from scipy.io import savemat

with h5py.File('./stimulus/nsd_stimuli.hdf5', 'r') as source_hdf5:
    # Define the number of images to save
    num_images = 100

    # Initialize an array to store the images
    images = np.zeros((num_images, 425, 425, 3), dtype='uint8')

    # Loop through and copy the first 1000 images from the source
    for i in range(num_images):
        print(f"Loading image {i+1}/{num_images}")
        # Read the ith image (Adjust indices for 0-based Python indexing)
        image_data = source_hdf5['imgBrick'][..., i]
        print("Read Image Data")

        # Permute the dimensions to match MATLAB's format
        image_data = np.transpose(image_data, (2, 1, 0))

        # Add to the list of images
        images.append(image_data)

# Create a dictionary to store the data
mat_data = {'coco_file': images}

# Save the data to a .mat file
savemat('coco_file_2.mat', mat_data)

print("Data saved to coco_file_2.mat")