import h5py

'''
eeg = torch of size 64x333 (channels (64)x time)
image = '48' filename[1] -> index into 'data' to get real image index 
label = get label from 'data' TODO: Confirm this
subject = filename[-1]

.mat shape = (333, 1, 1, 1, 64, 4)

TODO: Where to find lables and 'data' and how do the indices convert?

'''

# Load the .mat file
with h5py.File('stim 48 bl reref dt icfilt ica ar dc trl blk 209 but ch subj01.mat', 'r') as file:

    # Access the 'data' variable
    data = file['data']

    # Print the shape of 'data'
    print(data.shape)

    # Print a portion of 'data' (e.g., first 5 elements)
    print(data[:5])  # Adjust as needed based on data size



# labels and images should be an array of 960. BC we have 120 images per block, 8 unique blocks = 960
# labels is an array of 960 elements
# images is an array of 960 elements


# we expect to be able to extract the image id from each .mat file from ricky. Let's say that .mat file is the y index
# whatever that image id is (call it z). the data["dataset"][y]["image"] = z-1
# data["dataset"][z-1] = z


# dataset[0] is a dictionary with keys: ['eeg', 'image', 'label', 'subject']
# data["dataset"][0]["image"] = 0 to 959, call it x
# data["images"][x] = x+1
# 
# data["dataset"][0]["label"] = x
# data["label"][x] = x+1
    

# images will just be the image id we showed in the session (1-960)
