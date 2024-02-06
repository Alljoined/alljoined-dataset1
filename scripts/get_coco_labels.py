import csv
import json

# Read the 1000 shared nsd ids from the json file and get additional info from the csv file
with open('data/coco_indices.json', 'r') as file:
    coco_idx = json.load(file)

csv_file_path = 'data/nsd_stim_info_merged.csv'
data = []
with open(csv_file_path, 'r') as file:
    for i, idx in enumerate(coco_idx):
        print(f"Reading index {idx}. Progress: {i+1}/{len(coco_idx)}")
        isFound = False
        for row in csv.DictReader(file):
            if row['nsdId'] == str(idx-1):
                data.append({'nsdId': row['nsdId'], 'cocoId': row['cocoId'], 'cocoSplit': row['cocoSplit']})
                isFound = True
                break
        if not isFound:
            print(f"Index {idx} not found in csv file.")
        file.seek(0)

# Read the JSON files
with open('data/annotations/captions_train2017.json', 'r') as file:
    captions_train2017 = json.load(file)['annotations']

with open('data/annotations/captions_val2017.json', 'r') as file:
    captions_val2017 = json.load(file)['annotations']

# Function to find caption by image_id
def find_caption(image_id, coco_split):
    if coco_split == 'train2017':
        caption_list = captions_train2017
    elif coco_split == 'val2017':
        caption_list = captions_val2017
    else:
        return None

    for caption in caption_list:
        if caption['image_id'] == int(image_id):
            return caption['caption']
    return None

# Add captions to the data
for item in data:
    caption = find_caption(item['cocoId'], item['cocoSplit'])
    if caption:
        item['caption'] = caption

# Save the final data to a JSON file
with open('data/captions.json', 'w') as file:
    json.dump(data, file)
