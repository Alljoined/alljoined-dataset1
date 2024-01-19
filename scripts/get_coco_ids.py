# Converts the hdf5 file of all images we downloaded from pscotti into a .mat file
# Originally in float, convert to int range 0-255. Also selecting specific index for testing

import h5py
import numpy as np
from scipy.io import savemat, loadmat
import json
import argparse

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

with open('data/coco_indices.json', 'w') as file:
    json.dump(indices, file)