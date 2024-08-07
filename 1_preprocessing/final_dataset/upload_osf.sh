#!/bin/bash

# The local directory you want to upload
local_directory="/srv/eeg_reconstruction/shared/biosemi-dataset/final_hdf5"
# The OSF project ID
project_id="kqgs8"
# The destination directory in your OSF project
remote_directory=""

# Function to upload files recursively
function upload_directory {
    local source_path=$1
    local dest_path=$2
    for file in "$source_path"/*; do
        if [ -d "$file" ]; then
            # If it's a directory, recursive call
            upload_directory "$file" "$dest_path/$(basename "$file")"
        else
            # If it's a file, upload it
            echo "Uploading $file to $dest_path/"
            osf -p $project_id upload "$file" "$dest_path/$(basename "$file")"
        fi
    done
}

# Start the upload process
upload_directory "$local_directory" "$remote_directory"
