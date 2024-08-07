# alljoined_preprocessing

## Folder Structure

Below is a description of the main files and directories:

    ├── eeg_data/                       # Data files are stored here
        ├── bdf/                        # Raw bdf files
            ├── subj01_session1.bdf
            ├── ...
        └── raw_csv/                    # The stimulus data retrieved from bdf
            ├── subj01_session1.csv
            ├── ...
        └── parsed_csv/                 # Parsed stimulus data with double triggers merged
            ├── subj01_session1.csv
            ├── ...
        └── fif/                        # Parsed stimulus data converted to .fif format
            ├── subj01_session1_eeg.fif
            ├── ...
        └── final_eeg/                  # Final preprocessed and epoched EEG data in .fif format
            ├── 05_125/                 # A frequency range of our filtering
                ├── subj01_session1_epo.fif
                ├── ...
            ├── ...
        └── final_hdf5/                 # Preprocessed EEG data, stimulus info as pd dataframes saved in hdf5 format
            ├── 05_125/
                ├── subj01_session1.h5
                ├── ...
            ├── ...
    ├── parse-bdf-event-codes-to-fif.ipynb  # Script to convert bdf to fif and merge double triggers
    ├── fif-eeg-preprocessing.py            # Script to clean our EEG data
    ├── final_dataset                   # Working folder to create huggingface dataset
        ├── data/                       # Folder for final CSV file
            ├── final_dataset_subj04_session2.csv
        ├── main_dataset.py             # Script to combine our preprocessed, cleaned EEG data and map to coco image ids
        ├── nsd_coco_conversion.csv     # File that maps from NSD image id to coco id
        ├── nsd_expdesign.mat           # File that describes which images were shown to which subject
        ├── create_huggingface_dataset.py   # Script that uploads CSV dataset to huggingface
        ├── download_coco.py            # Script that downloads coco images used in our dataset
        ├── data/                       # Folder for downloaded coco images
        ├── behavioural_dataset.py      # Script to create a dataset for just our behavioural data
        ├── huggingface/                # Huggingface cache dir for our new dataset
    └── README.md           # The file you're reading now

## Preprocessing pipeline

1. Set up your environment, by creating a conda or mamba env from the environment.yml file.
2. Get the raw bdf file from Biosemi device. Link to the datasets is [here](https://drive.google.com/drive/u/0/folders/1yPFhX04nh2EnHBSEAjHyBmnWpP7oJQ21).
   1. You should download all the .bdf files for each subject and session
   2. Move them to /eeg_data/bdf
3. Run the first part of parse-bdf-event-codes-to-fif.ipynb to retrieve stimulus data
4. Run the second part of parse-bdf-event-codes-to-fif.ipynb to merge the double trigger data into a combined format. We use double trigger because BioSemi only supports 8 bits.
   1. The script may come across a phantom event, in the a format like `Error in line 10: 101 254`. Navigate to that line to resolve the issues around that line.
5. Run the third part of parse-bdf-event-codes-to-fif.ipynb to convert parsed_csv to fif format.
6. Upload the preprocessed .fif file to https://drive.google.com/drive/u/0/folders/1gI9csmnCwedRrlDoRy-jCqK4bclVN6mD.

We need to create a dataset for each of the frequency ranges: 0.5/125, 55/95, 14/70, 5/95. You should have been assigned one of these four to continue.

1. Modify the frequency in fif-eeg-preprocessing.py, on this line:
   `LOW_FREQ = 0.5 HI_FREQ = 125`
2. Run fif-eeg-preprocessing.py to preprocess the .fif data. This performs band filtering, epoch detection, PCA, eye blink removal, and baseline correction. The output is saved in /eeg_data/final_eeg.
3. In final_dataset/main_dataset.py, change `DATA_FOLDER` to be your data directory. Then change `LO_HI` to the right range e.g. `LO_HI = "05_125"`
4. Run final_dataset/main_dataset.py to create a CSV of all the data for that frequency range
5. Update csv_file_path to the csv path you create above in final_dataset/create_huggingface_dataset.py
6. Create .env file ini /final_dataset, set HF_PUSH to your hugginface access token
7. In final_dataset/create_huggingface_dataset.py, set DSET_NAME and then run the script to create and upload the huggingface dataset
