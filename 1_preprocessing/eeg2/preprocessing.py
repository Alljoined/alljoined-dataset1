import mne
import argparse
from preprocessing_utils import epoching
from preprocessing_utils import mvnn
from preprocessing_utils import save_prepr

mne.set_log_level('WARNING')

# =============================================================================
# Input arguments
# =============================================================================
parser = argparse.ArgumentParser()
parser.add_argument('--sub', default=1, type=int)
parser.add_argument('--n_ses', default=1, type=int)
parser.add_argument('--sfreq', default=512, type=int)
parser.add_argument('--mvnn_dim', default='epochs', type=str)
parser.add_argument('--project_dir', default='/srv/eeg_reconstruction/shared/biosemi-dataset', type=str)
parser.add_argument('--lo_freq', default=0.1, type=float)
parser.add_argument('--hi_freq', default=100, type=float)
args = parser.parse_args()

print('>>> EEG data preprocessing <<<')
print('\nInput arguments:')
for key, val in vars(args).items():
	print('{:16} {}'.format(key, val))
# Set random seed for reproducible results
seed = 20200220

# =============================================================================
# Epoch and sort the data
# =============================================================================
# Channel selection, epoching, baseline correction and frequency downsampling of
# the test and training data partitions.
# Then, the conditions are sorted and the EEG data is reshaped to:
# Image conditions × EGG repetitions × EEG channels × EEG time points
# This step is applied independently to the data of each partition and session.
epoched, img_conds, ch_names, _ = epoching(args, seed)

# TEMP HACK: We assume epoched is len 1, (we look at only 1)
num_train = int(len(epoched[0]) * 0.8)
epoched_train = [epoched[0][:num_train]]
img_conditions_train = [img_conds[0][:num_train]]
epoched_test = [epoched[0][num_train:]]

# =============================================================================
# Multivariate Noise Normalization
# =============================================================================
# MVNN is applied independently to the data of each session.
whitened_test, whitened_train = mvnn(args, epoched_test, epoched_train)
del epoched_test, epoched_train

# =============================================================================
# Merge and save the preprocessed data
# =============================================================================
# In this step the data of all sessions is merged into the shape:
save_prepr(args, whitened_test, whitened_train, img_conditions_train, ch_names, seed)