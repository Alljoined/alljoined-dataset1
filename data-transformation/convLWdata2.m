%% convert letswave data into Matlab and organize it for SVM later

clear; % clear workspace
tic % start time
%% subject number
subjNo = 'subj01';

%% preprocessed save structure from letswave
PREFIX_1 = 'bl reref dt icfilt ica ar dc trl blk';

PREFIX_2 = 'but ch';

%% starting to organize data of the participant, must be in "EEG_data" folder
disp (['Starting Subject ' subjNo(end-1:end)]);
cd (['participants/' subjNo]);


%% information about preprocessed trials
STIMULI = 60;
BLOCKS = 201:216;
N_SESSIONS = 1;

%% load data from information above
loadOrder = cell(STIMULI, length(BLOCKS)*N_SESSIONS); % stimuli x blocks 
rawData = loadOrder; % put final data in here
sIndex = 1;
    for stim = 1:STIMULI % go through each stim within each race
        bIndex = 1; %block index
        for sess = 1 %1:N_SESSIONS %go through each session 
            for b = 1:length(BLOCKS) %go through every block        
                stimNum = stim ; % get stimuli number               
                filename = ['stim ' num2str(stimNum) ' ' PREFIX_1 ' ' num2str(BLOCKS(b)) ' ' PREFIX_2 ' ' subjNo '.lw6']; % get filename of each stimuli in each block from EEG data
                disp(['Loading: "' filename '"'])
                [lwdata.header, lwdata.data] = LW_load(filename); % load the dataset using built-in letswave function
                lwdata.data = squeeze(lwdata.data); % get rid of singleton dimensions

                if ndims(lwdata.data) < 3 %#ok<ISMAT> % if there's no repetitions because those trials were dropped, create a singleton dimension
                    tmp(1,:,:) = lwdata.data;
                    lwdata.data = tmp;
                end
                
                loadOrder{sIndex, bIndex} = filename; % add filenames to the big matrix 
                rawData{sIndex, bIndex} = lwdata.data; % add data to big data matrix
                bIndex = bIndex + 1;
            end
        end
        sIndex = sIndex + 1;
    end

%% 
% the final rawData is a 2D cell matrix (unique stimuli by blocks). 
% that is, 60 unique stimuli (30 Asian, 30 Caucasian) by 32 blocks (16 in two sessions).
% each cell has a 3D matrix (number of repetitions by channels by time; ideally 4, by 64x512).

%% z scores all stimuli (including repetitions) for a given block, timepoint, and channel
disp ('z scoring data: all stimuli (including repetitions) at a given block, timepoint, and channel');
rawDataZ = zscore_iden_and_iter(rawData, 3);

%% averages stimulus repetitions and returns a 4D matrix (channels by stimuli by blocks by timepoints)
disp ('Averaging data: averaging reptitions of unique within a block');
rawDataAvg = average_eeg(rawDataZ);


%% save
disp ('Saving data');
cd ../..; % return to main directory
cd EEG_preprocessed; % enter raw data directory to save data

save ([num2str(subjNo) '_output.mat'], 'rawDataAvg'); % save the output variable. This should be 64 x 60 x 16 x 512 (electode, by stimulus, by block, by time)

cd ..; % return to main directory

disp(['time elapased: ' num2str(toc/60) ' minutes'])  % end time

