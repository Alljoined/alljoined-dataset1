import h5py

# Load the .mat file
with h5py.File('stim 48 bl reref dt icfilt ica ar dc trl blk 209 but ch subj01.mat', 'r') as file:
    # Access the 'data' variable
    data = file['data']

    # Print the shape of 'data'
    print(data.shape)

    # Print a portion of 'data' (e.g., first 5 elements)
    print(data[:5])  # Adjust as needed based on data size
