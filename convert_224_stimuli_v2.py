# Converts the hdf5 file of all images we downloaded from pscotti into a .mat file
# Originally in float, convert to int range 0-255. Also selecting specific index for testing

import h5py
import numpy as np
from scipy.io import savemat, loadmat
import argparse

file_path = r"C:\srv\matlab_preprocessing\stimulus\datasets--pscotti--mindeyev2\snapshots\9b356f8332f385c4256a3a342fff9be3df4ef275\coco_images_224_float16.hdf5"
label_path = r"C:\srv\matlab_preprocessing\stimulus\nsd_expdesign.mat"

parser = argparse.ArgumentParser(description="Subject # between 1 and 8.")
# Add the argument
parser.add_argument("-s", "--subject", type=int, choices=range(1, 9), 
                    help="Subject # between 1 and 8")
# Parse the arguments
args = parser.parse_args()

# Get image indexes
mat_contents = loadmat(label_path)
indices = []
if args.subject:
    indices = mat_contents['subjectim'][args.subject-1]
else:
    indices = mat_contents['sharedix'][0]

# Load HDF5 file
with h5py.File(file_path, 'r') as source_hdf5:
    # Define the number of images to save
    num_images = len(indices)

    # Initialize an array to store the images
    cell_array = np.empty((num_images, 1), dtype=object)

    # Loop through and copy the first num_images images from the source
    for i in range(num_images):
        print(f"Loading image {i+1}/{num_images}")
        # Read the ith image in (3, 224, 224) dimension
        image_data = (source_hdf5['images'][indices[i]-1, ...] * 255).astype(np.uint8)

        # Add to image to our cell array and transpose to (224, 224, 3)
        cell_array[i, 0] = np.transpose(image_data, (1, 2, 0))

# Save the cell array to a .mat file.
mat_data = {'coco_file': cell_array}

# Save the data to a .mat file
name = f"coco_file_224_sub{args.subject}.mat" if args.subject else "coco_file_224.mat"
savemat(name, mat_data)

print(f"Data saved to {name}.mat")