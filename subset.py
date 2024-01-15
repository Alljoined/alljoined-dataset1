import h5py
import numpy as np
from scipy.io import savemat

with h5py.File('./stimulus/nsd_stimuli.hdf5', 'r') as source_hdf5:
    # Define the number of images to save
    num_images = 1000

    # Initialize an array to store the images
    images = np.zeros((num_images, 425, 425, 3), dtype='uint8')

    # Loop through and copy the first 1000 images from the source
    for i in range(num_images):
        source_image = source_hdf5['/imgBrick'][i, :, :, :]
        # Convert the image to uint8 and store it
        images[i] = source_image.astype('uint8')

# Create a dictionary to store the data
mat_data = {'coco_file': images}

# Save the data to a .mat file
savemat('coco_file_2.mat', mat_data)

print("Data saved to coco_file_2.mat")