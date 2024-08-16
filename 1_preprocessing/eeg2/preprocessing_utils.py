def epoching(args, seed):
	"""This function first converts the EEG data to MNE raw format, and
	performs channel selection, epoching, baseline correction and frequency
	downsampling. Then, it sorts the EEG data of each session according to the
	image conditions.

	Parameters
	----------
	args : Namespace
		Input arguments.
	seed : int
		Random seed.

	Returns
	-------
	epoched_data : list of float
		Epoched EEG data.
	img_conditions : list of int
		Unique image conditions of the epoched and sorted EEG data.
	ch_names : list of str
		EEG channel names.
	times : float
		EEG time points.

	"""

	import os
	import mne
	import numpy as np
	from sklearn.utils import shuffle

	### Loop across data collection sessions ###
	epoched_data = []
	img_conditions = []
	for s in range(args.n_ses):
		# Load the BDF file
		fif_file_path = os.path.join(args.project_dir, 'fif', "subj0" + str(args.sub) + "_session" + str(s+1) + "_eeg.fif") 
		raw = mne.io.read_raw_fif(fif_file_path, preload=True)
		montage = mne.channels.make_standard_montage('standard_1020')
		raw.set_montage(montage)

		# Rereferencing electrodes
		raw.set_eeg_reference('average', projection=False)

		# Epoch into events and drop channels
		events = mne.find_events(raw)
		epochs = mne.Epochs(raw, events, tmin=0.05, tmax=0.70, baseline=(0.05,0.1), preload=True) # Manually move trigger back 100ms
		epochs.drop_channels(['Status'])
		epochs.shift_time(tshift=-0.1, relative=True)
		ch_names = epochs.ch_names
		times = epochs.times

		data = epochs.get_data(copy=True)
		events = epochs.events[:,2]
		img_cond = np.unique(events) # this is sorted
		del epochs
		max_rep = 4

		epoched_data = []
		img_conditions = []

		# Sorted data matrix of shape:
		# Image conditions × EEG repetitions × EEG channels × EEG time points
		sorted_data = np.zeros((len(img_cond),max_rep,data.shape[1], data.shape[2]))
		for i in range(len(img_cond)):
			# Find the indices of the selected image condition
			idx = np.where(events == img_cond[i])[0]
			# Patch for when # events < max_rep
			if len(idx) < max_rep:
				# Repeat idx elements until it reaches or exceeds max_rep
				idx = np.resize(idx, max_rep)
			# Randomly select only the max number of EEG repetitions
			idx = shuffle(idx, random_state=seed, n_samples=max_rep)
			sorted_data[i] = data[idx]
		del data
		epoched_data.append(sorted_data[:, :, :, int(0.05*512):])
		img_conditions.append(img_cond)
		del sorted_data

	### Output ###
	return epoched_data, img_conditions, ch_names, times


def mvnn(args, epoched_test, epoched_train):
	"""Compute the covariance matrices of the EEG data (calculated for each
	time-point or epoch/repetitions of each image condition), and then average
	them across image conditions and data partitions. The inverse of the
	resulting averaged covariance matrix is used to whiten the EEG data
	(independently for each session).
	
	zero-score standardization also has well performance

	Parameters
	----------
	args : Namespace
		Input arguments.
	epoched_test : list of floats
		Epoched test EEG data.
	epoched_train : list of floats
		Epoched training EEG data.

	Returns
	-------
	whitened_test : list of float
		Whitened test EEG data.
	whitened_train : list of float
		Whitened training EEG data.

	"""

	import numpy as np
	from tqdm import tqdm
	from sklearn.discriminant_analysis import _cov
	import scipy

	### Loop across data collection sessions ###
	whitened_test = []
	whitened_train = []
	for s in range(args.n_ses):
		session_data = [epoched_test[s], epoched_train[s]]

		### Compute the covariance matrices ###
		# Data partitions covariance matrix of shape:
		# Data partitions × EEG channels × EEG channels
		sigma_part = np.empty((len(session_data),session_data[0].shape[2],
			session_data[0].shape[2]))
		for p in range(sigma_part.shape[0]):
			# Image conditions covariance matrix of shape:
			# Image conditions × EEG channels × EEG channels
			sigma_cond = np.empty((session_data[p].shape[0],
				session_data[0].shape[2],session_data[0].shape[2]))
			for i in tqdm(range(session_data[p].shape[0])):
				cond_data = session_data[p][i]
				# Compute covariace matrices at each time point, and then
				# average across time points
				if args.mvnn_dim == "time":
					sigma_cond[i] = np.mean([_cov(cond_data[:,:,t],
						shrinkage='auto') for t in range(cond_data.shape[2])],
						axis=0)
				# Compute covariace matrices at each epoch (EEG repetition),
				# and then average across epochs/repetitions
				elif args.mvnn_dim == "epochs":
					sigma_cond[i] = np.mean([_cov(np.transpose(cond_data[e]),
						shrinkage='auto') for e in range(cond_data.shape[0])],
						axis=0)
			# Average the covariance matrices across image conditions
			sigma_part[p] = sigma_cond.mean(axis=0)
		# # Average the covariance matrices across image partitions
		# sigma_tot = sigma_part.mean(axis=0)
		# ? It seems not fair to use test data for mvnn, so we change to just use training data
		sigma_tot = sigma_part[1]
		# Compute the inverse of the covariance matrix
		sigma_inv = scipy.linalg.fractional_matrix_power(sigma_tot, -0.5)

		### Whiten the data ###
		whitened_test.append(np.reshape((np.reshape(session_data[0], (-1,
			session_data[0].shape[2],session_data[0].shape[3])).swapaxes(1, 2)
			@ sigma_inv).swapaxes(1, 2), session_data[0].shape))
		whitened_train.append(np.reshape((np.reshape(session_data[1], (-1,
			session_data[1].shape[2],session_data[1].shape[3])).swapaxes(1, 2)
				@ sigma_inv).swapaxes(1, 2), session_data[1].shape))

	### Output ###
	return whitened_test, whitened_train


def save_prepr(args, whitened_test, whitened_train, img_conditions_train, ch_names, seed):
	"""Merge the EEG data of all sessions together, shuffle the EEG repetitions
	across sessions and reshaping the data to the format:
	Image conditions × EGG repetitions × EEG channels × EEG time points.
	Then, the data of both test and training EEG partitions is saved.

	Parameters
	----------
	args : Namespace
		Input arguments.
	whitened_test : list of float
		Whitened test EEG data.
	whitened_train : list of float
		Whitened training EEG data.
	img_conditions_train : list of int
		Unique image conditions of the epoched and sorted train EEG data.
	ch_names : list of str
		EEG channel names.
	seed : int
		Random seed.

	"""

	import numpy as np
	from sklearn.utils import shuffle
	import os
	import pickle

	### Merge and save the test data ###
	for s in range(args.n_ses):
		if s == 0:
			merged_test = whitened_test[s]
		else:
			merged_test = np.append(merged_test, whitened_test[s], 1)
	del whitened_test
	# Shuffle the repetitions of different sessions
	idx = shuffle(np.arange(0, merged_test.shape[1]), random_state=seed)
	merged_test = merged_test[:,idx]
	# Insert the data into a dictionary
	test_dict = {
		'preprocessed_eeg_data': merged_test,
		'ch_names': ch_names,
	}
	del merged_test
	# Saving directories
	save_dir = os.path.join(args.project_dir, 'eeg2','preprocessed_eeg', 'sub-'+format(args.sub,'02'))
	file_name_test = 'preprocessed_eeg_test.npy'
	file_name_train = 'preprocessed_eeg_training.npy'
	# Create the directory if not existing and save the data
	if os.path.isdir(save_dir) == False:
		os.makedirs(save_dir)
	# np.save(os.path.join(save_dir, file_name_test), test_dict)
	save_pic = open(os.path.join(save_dir, file_name_test), 'wb')
	pickle.dump(test_dict, save_pic, protocol=4)
	save_pic.close()
	del test_dict

	### Merge and save the training data ###
	for s in range(args.n_ses):
		if s == 0:
			white_data = whitened_train[s]
			img_cond = img_conditions_train[s]
		else:
			white_data = np.append(white_data, whitened_train[s], 0)
			img_cond = np.append(img_cond, img_conditions_train[s], 0)
	del whitened_train, img_conditions_train

	# Data matrix of shape:
	# Image conditions × EGG repetitions × EEG channels × EEG time points
	merged_train = np.zeros((len(np.unique(img_cond)), white_data.shape[1], white_data.shape[2], white_data.shape[3]))
	for i in range(len(np.unique(img_cond))):
		# Find the indices of the selected category
		idx = np.where(img_cond == i+1)[0]
		for r in range(len(idx)):
			if r == 0:
				ordered_data = white_data[idx[r]]
			else:
				ordered_data = np.append(ordered_data, white_data[idx[r]], 0)
		merged_train[i] = ordered_data
	# Shuffle the repetitions of different sessions
	idx = shuffle(np.arange(0, merged_train.shape[1]), random_state=seed)
	merged_train = merged_train[:,idx]
	# Insert the data into a dictionary
	train_dict = {
		'preprocessed_eeg_data': merged_train,
		'ch_names': ch_names,
	}
	del merged_train
	# Create the directory if not existing and save the data
	if os.path.isdir(save_dir) == False:
		os.makedirs(save_dir)
	# np.save(os.path.join(save_dir, file_name_train),
	# 	train_dict)
	save_pic = open(os.path.join(save_dir, file_name_train), 'wb')
	pickle.dump(train_dict, save_pic, protocol=4)
	save_pic.close()
	del train_dict
