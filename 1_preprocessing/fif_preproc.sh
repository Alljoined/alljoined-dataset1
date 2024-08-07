#!/bin/bash
# Script to do preprocessing for all .fif files in one go

# Array of .fif files
fif_files=(
    "subj01_session1_eeg.fif"
    "subj01_session2_eeg.fif"
    "subj02_session1_eeg.fif"
    "subj03_session2_eeg.fif"
    "subj04_session1_eeg.fif"
    "subj04_session2_eeg.fif"
    "subj05_session1_eeg.fif"
    "subj06_session1_eeg.fif"
    "subj06_session2_eeg.fif"
    "subj07_session1_eeg.fif"
    "subj08_session1_eeg.fif"
)

# Loop through each .fif file and run the Python script
for file in "${fif_files[@]}"; do
    python fif-eeg-preprocessing.py "$file"
    status=$?
    if [ $status -ne 0 ]; then
        echo "Error processing $file - Exiting script"
        exit $status
    fi
done
