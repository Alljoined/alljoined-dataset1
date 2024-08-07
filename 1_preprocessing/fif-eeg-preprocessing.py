import mne
from mne.preprocessing import ICA
from autoreject import get_rejection_threshold, compute_thresholds, AutoReject
import os
import numpy as np 
import argparse

# experiment with 0.5/125, 55/95, 14/70, 5/95
DATA_PATH="/srv/eeg_reconstruction/shared/biosemi-dataset"
LOW_FREQ = 0.5
HI_FREQ = 125
output_path = os.path.join(DATA_PATH, 'final_eeg', str(LOW_FREQ).replace('.', '') + "_" + str(HI_FREQ))

parser = argparse.ArgumentParser(description='Preprocess EEG data')
parser.add_argument('input_file', type=str, help='Input file name', default='subj04_session2_eeg.fif')
args = parser.parse_args()

# Load the BDF file
fif_file_path = os.path.join(DATA_PATH, 'fif', args.input_file) 
raw = mne.io.read_raw_fif(fif_file_path, preload=True)

# Apply standard montage
montage = mne.channels.make_standard_montage('standard_1020')
raw.set_montage(montage)

# Filter data (Step 9)
raw.filter(l_freq=LOW_FREQ, h_freq=HI_FREQ)
raw.notch_filter(freqs=60)

# ICA for artifact correction (Steps 14 and 15)
# As is typically done with ICA, the data are first scaled to unit variance and whitened using principal components analysis (PCA)
# before performing the ICA decomposition. It uses the # of components needed to explain 95% of the variance
ica = ICA(n_components=0.95, random_state=97)
ica.fit(raw)
ica.exclude = [1]
ica.apply(raw)

# Detect events and Epoching (Step 10)
events = mne.find_events(raw)
epochs = mne.Epochs(raw, events, event_id=None, tmin=-0.05, tmax=0.60, preload=True)
picks = mne.pick_types(epochs.info, eeg=True, stim=False, exclude='bads')

# Automated Artifact Rejection (Step 12): Setting threshold using autoreject
#TODO: they choose these hyperparams w/o explanation in docs -> https://autoreject.github.io/stable/auto_examples/plot_auto_repair.html
n_interpolates = np.array([1, 4, 32])
consensus_percs = np.linspace(0, 1.0, 11)

ar = AutoReject(n_interpolates, consensus_percs, picks=picks, thresh_method='random_search', random_state=42)

epochs = ar.fit_transform(epochs)

epochs.average().plot()

# Remove 'Status' channel (Step 8). 
# Removing it here because you need this channel for earlier steps like creating epochs
epochs.drop_channels(['Status'])

# Rereferencing (Step 17)
epochs.set_eeg_reference('average')

# Baseline correction (Step 18)
# Baseline correction before ICA is not recommended by the MNE-Python developers, as it doesn’t guarantee optimal results.
epochs.apply_baseline(baseline=(-0.05, 0)) # look at time interval from 50ms from start to 0 seconds from start

# Saving the preprocessed data
root_name = os.path.splitext(args.input_file)[0][:-4]
preprocessed_file_path = os.path.join(output_path, f"{root_name}_epo.fif" )
os.makedirs(os.path.dirname(preprocessed_file_path), exist_ok=True)
epochs.save(preprocessed_file_path, overwrite=True)