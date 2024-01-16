function ORE_EEG_2(SUBJ, SESSION_NUMBER)


% load in default values if arguments are not set when running the function
if nargin < 2
    SESSION_NUMBER = '1'; % default run number is 1
end
if nargin < 1 
    SUBJ = '99'; % default subject number is 99f
end

% obtain and clarify participant information
answer = inputdlg({'Subject #', 'Session number'}, 'Parameters', 1, {num2str(SUBJ), num2str(SESSION_NUMBER)});
[SUBJ, SESSION_NUMBER] = deal(answer{:}); % write the user input to specified variables
SESSION_NUMBER = str2double(SESSION_NUMBER); % current run number

% stimulus parameters 
IMG_WIDTH = 425; % the width of the image 
IMG_HEIGHT = 425; % scaling the height of the image 
NIMAGES = 60;
 
% setup trial and block parameters 
DISPLAY_TIME = 0.3; % the time the stimulus is displayed on screen 
BLANK_TIME = 0.3; % the minimum blank time 
BLANK_BUFFER = 0.05; % the temporal jitter that may be added to the blank time
CUE_TIME = 0.1; % the time the cue is presented on screen

% setup trigger information
START_RECORD = 198; % the trigger to start the EEG recording 
STOP_RECORD = 199; % the trigger to stop the EEG recording 
CORRECT_HIT = 254; % the trigger that records a correct hit to a catch stimulus 
FALSE_ALARM = 253; % the trigger that records a false hit to an experimental stimulus 
CORRECT_REJ = 252; % the trigger that records a correct no-key to an experiment stimulus 
MISS = 251; % the trigger that records a false no-key to a catch stimulus 

% setup system and colour palette
quit = 0; % monitors if the user initiates script termination
rng('shuffle'); % shuffle the random seed generator
WHITE = [255 255 255]; % generate white colour palette
GREY = [128 128 128]; % generate gray colour palette
BLACK = [0 0 0]; % generate black colour palette
HideCursor; % remove cursor from the screen
clc; % clear command window
%sessionID = TriggerInit(SESSION_NUMBER); % comment this out
%sessionID = TriggerInit(RUN_NUMBER); % retrieve session ID from trigger initiator
 
% setup screen information
Screen('Preference', 'SkipSyncTests', 1); %THIS SHOULD BE SET FROM 1 to 0
% For local computer, disabling sync, delete later
Screen('Preference', 'ConserveVRAM', 64);
[w, wRect] = Screen('OpenWindow', max(Screen('Screens')), BLACK); % open a new screen in the max window
Screen('TextFont', w, 'Arial'); % Set text font
Screen('TextSize', w, 50); % set text size
[xMid, yMid] = RectCenter(wRect);% Get the center coordinates
 
% set up keyboard configurations
KbQueueCreate(); % create keyboard listening queue
KbName('UnifyKeyNames'); % unifies key names across operating systems
BREAKKEY = KbName({'q'}); % to break out of the program prematurely
BLOCKSKIPKEY = KbName({'s'}); % skip a block by going to the n-1th trial of that block
SPACEKEY = KbName({'SPACE'}); % general selection key
SKIPKEY = KbName(96);
KbQueueStart(); % start the listening queue

% this section sets up coordinate positions for ensembles and single images_
disp ('Ordering trials'); % display loading to console

% Load the stimulus file
nsdData = load('stimulus/nsd_expdesign.mat');

% Essentially, we have 8 subjects and each subject has 10 sessions.
% Within each session, we have 10 blocks in a session.
% Each block contains 100 indices.
% For example, if we are on trial 2, session 3, block 4, we want the indices in nsdData.subjectim[23401:23500]
% We iterate over ten blocks and create an array that repeats an index 4 times.
% We randomly add -1, 24 times within each array.
% Therefore, we should have an array of 424 elements of indices from nsdData.subjectim[10000*SUBJ + 1000*SESSION_NUMBER + 100*(block-1) +1:10000*SUBJ + 1000*SESSION_NUMBER + 100*block +1].
% The outputted array should randomly order these indices, and no index should be repeated twice in a row. The first two indices can not be -1.
NODDBALLS = 24; % number of oddball trials
NUM_BLOCKS = 16; % total number of blocks per session
IMGS_PER_BLOCK = 60;
COORDS = [xMid-(IMG_WIDTH/2), yMid-(IMG_HEIGHT/2), xMid+(IMG_WIDTH/2), yMid+(IMG_WIDTH/2)];

for k = 1:NUM_BLOCKS
    %start_idx = IMGS_PER_BLOCK*(k-1) + 1;
    %end_idx = IMGS_PER_BLOCK*k;
    start_idx = 1;
    end_idx = IMGS_PER_BLOCK;

    facePairs = [repmat(start_idx:end_idx, 1,4)'; zeros(NODDBALLS,1)-1]; % each block has 60 images repeated four times and 24 oddballs = 264 images
    NTRIALS = length(facePairs); % total number of trials including oddballs (264)

    % this section sorts all the trials, ensuring the same face is never repeated twice
    countErrors = 1001; % automatic reset the trial sorting variables
    indexChosen = zeros(NTRIALS,1); % keeps record of whether an index was chosen during the sort. Makes sure duplicate indices aren't chosen
    nSorts = 0; % record how many resorts took place
    while sum(indexChosen) ~= NTRIALS % as long as all the indices have not been sorted yet
        if countErrors > 1000 % if a lot of errors take place in sorting, reset the sort because it may be stuck on an impossible sort
            indexAt = 1; % set the index as the first index to be sorted
            countErrors = 0; % reset the number of counted errors
            indexChosen = zeros(NTRIALS,1); % reset the indices which have been sorted out
            trialSort = zeros(NTRIALS,1); % reset the array holding all the randomly sorted indices
            nSorts = nSorts + 1; % record the number of resorts
        end % if checking for errors
        
        if indexAt < 3 % for the first two trials, cannot choose a oddball trial
            getIndex = randi([1,IMGS_PER_BLOCK*4]); 
        else
            getIndex = randi([1,NTRIALS]); % select a random index (inclusive of oddball trials)
        end
        
        if ~indexChosen(getIndex) % if that index has not been chosen yet
            if indexAt == 1 % for the first index (trial 1 being sorted), no need to check order of trials yet
                indexChosen(getIndex) = 1; % set the randomly selected index as chosen
                trialSort(indexAt) = getIndex; % set the first sorted index as the randomly chosen index
                indexAt = indexAt + 1; % count up number of indices which have been chosen
            else % if the index at is after the first trial
                if facePairs(getIndex,1) ~= facePairs(trialSort(indexAt-1), 1) %&& facePairs(getIndex,2) ~= facePairs(trialSort(indexAt-1), 2)% && facePairs(getIndex,1) ~= facePairs(trialSort(indexAt-1), 2) && facePairs(getIndex,2) ~= facePairs(trialSort(indexAt-1), 1)
                    indexChosen(getIndex) = 1; % set the randomly selected index as chosen
                    trialSort(indexAt) = getIndex; % set that sorted index as the randomly chosen index
                    indexAt = indexAt + 1; % count up number of indices which have been chosen
                else % if they are the same, count up number of errors taking place in case an impossible sort took place
                    countErrors = countErrors + 1;
                end % if which checks if trial sets are the same or not
            end % if which checks if we're on the first index
        end % if which checks if the index has already been chosen before proceeding to sorting it
    end % infinite loop which ensures all trials are sorted before exiting

    shuffledFaces = facePairs(trialSort, :); % length of 424, array of indices between start_idx and end_idx, with 24 -1s
    
    finalOrder(:,k) = shuffledFaces; 
end


% Load the first numPreloadedImages images only if they haven't been loaded yet
% preloadedImages = cell(numPreloadedImages, 1);
% numPreloadedImages = 60;
% for j = 1:numPreloadedImages
%     subjectimIdx = nsdData.subjectim(str2double(SUBJ), j);
%     im = permute(h5read('../../stimulus/nsd_stimuli.hdf5', '/imgBrick', [1 1 1 subjectimIdx], [3 425 425 1]), [3, 2, 1]);
%     preloadedImages{j} = im;
% end

% function stimImg = getImg(i)
%     % Check if the requested index is within the preloaded range
%     if i <= numPreloadedImages
%         im = preloadedImages{i};
%     else
%         subjectimIdx = nsdData.subjectim(str2double(SUBJ), i);
%         im = permute(h5read('../../stimulus/nsd_stimuli.hdf5', '/imgBrick', [1 1 1 subjectimIdx], [3 425 425 1]), [3, 2, 1]);
%     end

%     stimImg = Screen('MakeTexture', w, im);
% end


load coco_file_224_shared.mat;

for i = 1:length(coco_file)
    STIM_IMAGE{i} = Screen('MakeTexture', w, coco_file{i}); 
end


% load (or generate) appropriate directories for the subjects 
if exist(['subj' SUBJ], 'dir') ~= 7 % if the subject directory doesn't exist yet
    mkdir(['subj' SUBJ]); % create the directory 
end
cd(['subj' SUBJ]); % enter the directory
mkdir(['session' num2str(SESSION_NUMBER)]); % generate a directory for the run number 
cd(['session' num2str(SESSION_NUMBER)]); % enter the directory
save(['finalOrder' num2str(SUBJ) '.mat'],'finalOrder');
%load(['finalOrder' num2str(SUBJ) '.mat']);

blockTime = zeros(NUM_BLOCKS,1); % records the time it took for each block

% this section runs the main experiment, all trials across all blocks for the run, including generating block-specific variables at the beginning of each block
runTime = GetSecs(); % get the current time to be used to calculate the run time at the end
for blockNumber = 1:NUM_BLOCKS % go through all the blocks in the run
    
    triggerMonitor = {'Trigger' 'TimeStamp' 'IntervalStamp'}; % setup list to record every trigger for each trial

    % generate multiple arrays which hold trial-specific information 
    trialRT = zeros(NTRIALS,1); % the reaction time 
    trialBlankTime = zeros(NTRIALS,1); % the blank period before the cue, has some random jitter
    trialTrigger = zeros(NTRIALS,1); % the trigger for each trial
    trialAccuracy = zeros(NTRIALS,1); % the go/no-go accuracy for each trial
    trialTiming = zeros(NTRIALS,1); % records the length of time for a trial

    % set the trial parameters for the particular block being run
    for i = 1:NTRIALS
        trialBlankTime(i) = BLANK_TIME + (randi([0,4]) * (BLANK_BUFFER/4)); % the jitter for the blank time
        trialTrigger(i) = finalOrder(i, blockNumber); % the trigger sent for the type of stimulus being shown (-1 = oddball)
    end
    
    % this section opens a splash screen and shows catch stimuli. This only runs for the beginning of the first block
    instructionScreen = 1;
    while blockNumber == 1 && ~quit % infinite loop for as long as no quit has been selected and we're only on the first block
        if instructionScreen == 1 % display instructions to participants (two instruction screens, one blank flash screen between)
            DrawFormattedText(w, ['Welcome to session ',num2str(SESSION_NUMBER),' of the study.',...
                '\n\nIn this session, you will complete a perception task.',...
                '\nThis session consists of one training block and 16 experimental blocks.',...
                '\n\nYou will see sequences of faces appearing on the screen, your task is to ',...
                '\npress the space bar when you see a face appear twice in a row.',...
                '\n\nPress the space bar to continue.'], 'center', 200, WHITE, 80, [], [], 1.5); % instructions to start experiment
        elseif instructionScreen == 3 % second instruction screen
            DrawFormattedText(w, ['This is the training block.',...
                '\n\nYou will see sequences of faces appearing on the screen, your task is to ',...
                '\npress the space bar when you see a face appear twice in a row.',...
                '\n\nWhen you are ready, press the space bar to start.'], 'center', 200, WHITE, 80, [], [], 1.5); % instructions to start experiment
        end
        %DrawFormattedText(w, '+', 'center', 'center', GREY, 80, [], [], 1.5); % draw the fixation cross
       
         if instructionScreen == 2 % put a blank flash screen between the two instructions so it doesn't flash so quickly
            WaitSecs(0.5);
            instructionScreen = 3; % set to the second instruction screen
        end
        
        Screen('Flip', w); % flip the screen image
        WaitSecs(0.01); % have some delay to avoid overwhelming the display processor 
              
        [~, keyCode] = KbQueueCheck(); % check the keyboard input
        if keyCode(SPACEKEY) % if the user initiates the experiment to start 
            KbQueueFlush(); % flush the keyboard input
            
            if instructionScreen == 1
                instructionScreen = 2; 
            elseif instructionScreen == 3
                break;
            end

        elseif keyCode(BREAKKEY) % if the user initiates to break out of the experiment
            KbQueueFlush(); % flush the keyboard input 
            quit = 1; % declare quit parameter 
            break; % break from the inifite loop
        end % end keyboard check
    end % loop that displays the splash screen
    
    % this section runs the main experiment loop
    % triggerMonitor = recordTrigger(sessionID, START_RECORD, triggerMonitor); % send and record the start trigger
    WaitSecs(0.5);
    %triggerMonitor = recordTrigger(sessionID, 200+blockNumber, triggerMonitor);
    trialPhase = 'startBlank'; % start with a blank trial (not included in the other trials)
    iTrial = 0; % begin at trial 0 (the start blank)
    setupTrial = 0; % boolean toggle to setup a new trial 
    blockTime(blockNumber) = GetSecs(); % record the block time
    trialStartTime = blockTime; % record the trial start time to monitor the length of the trial
    while ~quit % main experiment block loop: run as long as a quit isn't initiated
        if setupTrial % if the setup trial toggle has been activated 
            setupTrial = 0; % turn off the toggle 
            iTrial = iTrial + 1; % count up number of passed trials 
                       
            if iTrial > NTRIALS % check if the current trial has exceeded the total number of trials for the block 
                break; % break out of the block loop
            end
            
            trialPhase = 'display'; % declare the trial phase as the display phase
            if trialTrigger(iTrial) == -1
                % triggerMonitor = recordTrigger(sessionID, 100+trialTrigger(iTrial-1), triggerMonitor); % record the trial trigger
            else % for non-oddball trials, the accuray is 1 because they correctly abstained from a keypress (correct abstinence)
                % triggerMonitor = recordTrigger(sessionID, trialTrigger(iTrial), triggerMonitor); % record the trial trigger
            end
            
            trialStartTime = GetSecs(); % record the trial start time 
        end % if statement that monitors boolean toggle to setup trials
        
        % this section records the elapsed time and displays appropriate stimuli
        elapsedTime = GetSecs() - trialStartTime; % elapsed time to monitor the length of the trial and set trial phases
        switch trialPhase % check trial phase 
            case 'startBlank' % for the start blank
                DrawFormattedText(w, '+', 'center', 'center', GREY, 80, [], [], 1.5); % draw the center fixation cross
                if elapsedTime > DISPLAY_TIME + BLANK_TIME % if the elapsed time is greater than the display and blank time
                    trialPhase = 'cue'; % switch to the cue for the first trial 
                end
            case 'display' % for the stimulus display phase 
                
                if trialTrigger(iTrial) == -1 % for oddbal trials, repeat the image from the previous trial
                    Screen('DrawTexture', w, STIM_IMAGE{trialTrigger(iTrial-1)}, [], COORDS);
                else % else, draw the image associated with that trial (called based off the trigger)
                    Screen('DrawTexture', w, STIM_IMAGE{trialTrigger(iTrial)}, [], COORDS);
                    %% 
                end
                
                if elapsedTime > DISPLAY_TIME % if the elapsed time is greater than the display time
                    trialPhase = 'blank'; % switch to the post-display blank
                end
            case 'blank' % for the post-display blank 
                DrawFormattedText(w, '+', 'center', 'center', GREY, 80, [], [], 1.5); % draw the fixation cross 
                
                if elapsedTime > DISPLAY_TIME + trialBlankTime(iTrial) % if the elapsed time is greater than the display and declared blank period for the trial
                    trialPhase = 'cue'; % switch to the cue phase to remove iconic memory and cue the next trial
                    if iTrial > 0 && trialRT(iTrial) == 0 % if the current trial is not the start blank and no key input was recorded for the trial
                        if trialTrigger(iTrial) == -1 % if it's an oddball trial, the accuracy is 0 because they should have pressed a key (miss)
                            trialAccuracy(iTrial) = 0;
                        else % for non-oddball trials, the accuray is 1 because they correctly abstained from a keypress (correct abstinence)
                            trialAccuracy(iTrial) = 1;
                        end
                        
                        %triggerMonitor = recordTrigger(sessionID, (trialAccuracy(iTrial)*CORRECT_REJ)+(~trialAccuracy(iTrial)*MISS), triggerMonitor); % send the trigger as a function of the accuracy compared to miss or correct rejection
                    end                    
                end 
            case 'cue' % cueing for the next trial
                DrawFormattedText(w, '+', 'center', 'center', WHITE, 80, [], [], 1.5); % draw the fixation cross brighter to cue the next trial
                
                if iTrial > 0 % if the trial is not the start blank
                    if elapsedTime > DISPLAY_TIME + trialBlankTime(iTrial) + CUE_TIME % if the elapsed time is greater than the display, blank, and cue time
                        setupTrial = 1; % toggle on the setup boolean to initiate the next trial
                        trialTiming(iTrial) = GetSecs() - trialStartTime; % record the time the trial took
                    end 
                else % if the trial is the start blank 
                    if elapsedTime > DISPLAY_TIME + BLANK_TIME + CUE_TIME % if theelapsed time is greater than the display time, blank (without buffer), and cue time
                        setupTrial = 1; % toggle on the setup boolean to initiate the next trial 
                    end
                end
        end % end switch statement to check the trial phase 
        
        Screen('Flip', w); % flip the screen image
        
        [~, keyCode] = KbQueueCheck(); % check the keyboard input
        if keyCode(SPACEKEY) && iTrial > 0 && trialRT(iTrial) == 0 && (strcmp(trialPhase, 'display') || strcmp(trialPhase, 'blank')) % if there is a user input, and the trial is not the start blank and is on either the display or the blank
            KbQueueFlush(); % flush the keyboard input
            trialRT(iTrial) = elapsedTime; % record the trial RT as the elapsed time (display onset)
            
            if trialTrigger(iTrial) == -1 % if they hit an oddball, set the accuracy to 1 (correct hit)
                trialAccuracy(iTrial) = 1;
            else % else, if they hit a regular trial thatisn't an oddball, set the accuracy to 0 (false alarm)
                trialAccuracy(iTrial) = 0;
            end
            
            %triggerMonitor = recordTrigger(sessionID, (trialAccuracy(iTrial)*CORRECT_HIT)+(~trialAccuracy(iTrial)*FALSE_ALARM), triggerMonitor); % send the trigger as a function of accuracy compared to false alarm and correct hit
        elseif keyCode(BREAKKEY) % if the user initiates termination of the script
            KbQueueFlush(); % flush the keyboard input 
            quit = 1; % set the quit toggle to active 
            break; % break out of the main experiment loop
        elseif keyCode(SKIPKEY) && iTrial > 0 % debug option to skip a trial, and does not occur for the start blank
            KbQueueFlush(); % flush the keyboard input 
            trialRT(iTrial) = -1; % set the RT as -1 to show this trial was skipped 
            setupTrial = 1; % boolean toggle to setup next trial
        elseif keyCode(BLOCKSKIPKEY) && iTrial > 0 % skip the block
            KbQueueFlush(); % flush the keyboard input 
            setupTrial = 1;
            trialRT(iTrial) = -2; % sets the RT as -2 to show the whole block was skipped
            iTrial = NTRIALS;
        end % end keyboard check
    end % main experiment loop
    blockTime(blockNumber) = GetSecs() - blockTime(blockNumber); % update the block time recording
        
    % this section initiates the rest break
    secsPassed = 0; % how many full seconds have passed during the rest break
    secStart = GetSecs(); % initial time counter to count how many seconds have passed 
    restTime = secStart; % how long the rest time lasts 
    while ~quit && blockNumber ~= NUM_BLOCKS % as long as no quit is initiated and the current block is not the last block
        elapsedTime = GetSecs() - secStart; % get the elapsed time (resets every second)
        
        if blockNumber == 1 % for the first block, tell them they completed the training 
            DrawFormattedText(w, ['You have completed the training block.\nNow we will start the ' num2str(NUM_BLOCKS-1) ' testing blocks.\nTake a short rest'], 'center', 200, WHITE, 80, [], [], 1.5); % display the break prompt as well as how many trials have passed
        else % for the ramining blocks, tell them how many they completed (minus 1 for the training)
            DrawFormattedText(w, ['You have completed ' num2str(blockNumber-1) ' out of ' num2str(NUM_BLOCKS-1) ' blocks.\nTake a short rest'], 'center', 200, WHITE, 80, [], [], 1.5); % display the break prompt as well as how many trials have passed
        end
        
        if secsPassed > 4 % if 5 or more seconds have passed, prompt that they can continue the experiment
            DrawFormattedText(w, 'Press space whenever you wish to continue', 'center', yMid+200, WHITE, 80, [], [], 1.5); % cue participants to start at any time
        end
        DrawFormattedText(w, '+', 'center', 'center', GREY, 80, [], [], 1.5); % draw the fixation cross 
        
        % when a second passes, monitor changes and send stop-trigger after the fifth second 
        if elapsedTime > 1 % if a second has passed
            secsPassed = secsPassed + 1; % count up how many seconds have passed
            secStart = GetSecs(); % reset secsStart where elapsed time is calculated relative to
            if secsPassed == 5 % if five seconds have passed (where participants are now allowed to exit from the break)
                %triggerMonitor = recordTrigger(sessionID, STOP_RECORD, triggerMonitor); % record the stop trigger 
            end 
        end % if to check how much time has passed
         
        Screen ('Flip', w); % flip the screen image
        WaitSecs(0.01); % some delay to avoid overwhelming the display processor
        
        [~, keyCode] = KbQueueCheck(); % check the keyboard input
        if keyCode(SPACEKEY) && secsPassed > 4 % if the user presses space and more than 4 seconds have passed 
            KbQueueFlush(); % flush the keyboard input 
            break; % break from the rest loop
        elseif keyCode(BREAKKEY) % if the user initiates to quit the script 
            KbQueueFlush(); % flush the keyboard input 
            quit = 1; % set the quit toggle to active 
            break; % exit from the rest loop
        end % end keyboard check
    end % end rest loop
    restTime = GetSecs() - restTime; % update how much time the rest took
    
    % in case a stop trigger was not recorded as the last trigger, make sure it is
    if triggerMonitor{size(triggerMonitor,1),1} ~= STOP_RECORD % check to make sure the last trigger of the block was a stop trigger (won't be the case if there was a user-initiated termination)
        % triggerMonitor = recordTrigger(sessionID, STOP_RECORD , triggerMonitor); % send stop trigger
    end
    
    % this section saves block data
    blockSave = blockNumber + (NUM_BLOCKS * (SESSION_NUMBER - 1)); % the save number (count is based on completion of previous runs)
    save(['b' num2str(blockSave) 'metadata.mat']); % save the entire workspace in the metadata
    
    % setup trial data in a mixed structure matrix
    for t = 1:NTRIALS % go through all trials and log each relevant trial parameter
        trialData(t).trigger = trialTrigger(t);  %#ok<*AGROW>
        trialData(t).timing = trialTiming(t);
        trialData(t).blankTime = trialBlankTime(t);
        trialData(t).RT = trialRT(t);
        trialData(t).accuracy = trialAccuracy(t);
    end
    
    % saves general parameters for the block
    params.blockNumber = blockNumber;
    params.blockTime = blockTime(blockNumber);
    params.restTime = restTime;
    params.lastTrial = iTrial - 1;
    params.nSorts = nSorts;
    
    % generate raw data structure with the organized variables
    rawData.trialData = trialData; % record the trial data in the raw data structure 
    rawData.params = params; % record the parameter data in the raw data structure 
    rawData.triggerRecord = triggerMonitor; % record the trigger monitor for the block 
    
    save(['b' num2str(blockSave) '.mat'], 'rawData'); % save the rawData for the block 
    clear trialData params rawData; % clear the data structure so it's free during the next block section
    
    if quit % before re-iterating the loop, check if there was a termination procedure
        break; 
    end
end % for loop that goes through all blocks in the run
runTime = GetSecs() - runTime; % update the run time

save(['r' num2str(SESSION_NUMBER) 'metadata.mat']); % save the metadata for the run 

cd ..; % return to subject directory from run directory 
if exist(['runData_s' SUBJ '.mat'], 'file') == 2 % if a data file for the run already exists 
    load(['runData_s' SUBJ '.mat']); % load the run data
end

% save general run-specific data to the runData structure 
runData.(['r' num2str(SESSION_NUMBER)]).completedBlocks = blockNumber;
runData.(['r' num2str(SESSION_NUMBER)]).displayTime = DISPLAY_TIME;
runData.(['r' num2str(SESSION_NUMBER)]).blankTime = BLANK_TIME;
runData.(['r' num2str(SESSION_NUMBER)]).blankBuffer = BLANK_BUFFER;
runData.(['r' num2str(SESSION_NUMBER)]).cueTime = CUE_TIME;
runData.(['r' num2str(SESSION_NUMBER)]).coords = COORDS;
runData.(['r' num2str(SESSION_NUMBER)]).faceHeight = IMG_HEIGHT;
runData.(['r' num2str(SESSION_NUMBER)]).faceWidth = IMG_WIDTH;
runData.(['r' num2str(SESSION_NUMBER)]).startRecordTrigger = START_RECORD;
runData.(['r' num2str(SESSION_NUMBER)]).stopRecordTrigger = STOP_RECORD;
runData.(['r' num2str(SESSION_NUMBER)]).correctHitTrigger = CORRECT_HIT;
runData.(['r' num2str(SESSION_NUMBER)]).falseAlarmTrigger = FALSE_ALARM;
runData.(['r' num2str(SESSION_NUMBER)]).missTrigger = MISS;
runData.(['r' num2str(SESSION_NUMBER)]).userTerminated = quit;
runData.(['r' num2str(SESSION_NUMBER)]).runTime = runTime; %#ok<*STRNU>
runData.(['r' num2str(SESSION_NUMBER)]).blockTime = blockTime; 
save(['runData_s' SUBJ '.mat'], 'runData'); % save the runData structure

% close everything
cd ..; % return from subject directory to the main directory
KbQueueStop(); % stop queuing keyboard
KbQueueRelease(); % release keyboard queue
Screen('CloseAll'); % close any texture
sca; % close everything 
end % end main function 

% Todo: add double trigger
function monitor = recordTrigger(session, triggerNumber, monitor) % function to monitor and send triggers
SendTrigger(session, triggerNumber); % send the trigger 
monitor = [monitor; {triggerNumber, GetSecs(), NaN}]; % record the trigger 
disp (['Trigger ' num2str(triggerNumber)]); % display the trigger to the command window

monitorIndex = size(monitor,1); % get the size of the trigger monitor index 
if monitorIndex > 2 % if this is not the first logged trigger 
    monitor{monitorIndex,3} = monitor{monitorIndex,2} - monitor{monitorIndex-1, 2}; % get the time difference between both triggers 
end 
end % end record trigger function