import csv
import json

# Read the JSON files
with open('data/annotations/captions_train2017.json', 'r') as file:
    captions_train2017 = json.load(file)['annotations']

with open('data/annotations/captions_val2017.json', 'r') as file:
    captions_val2017 = json.load(file)['annotations']

# Load the JSON files for instances and categories
with open('data/annotations/instances_train2017.json', 'r') as file:
    instances_train2017 = json.load(file)
    categories_train2017 = instances_train2017['categories']
    instances_train2017 = instances_train2017['annotations']

with open('data/annotations/instances_val2017.json', 'r') as file:
    instances_val2017 = json.load(file)
    categories_val2017 = instances_val2017['categories']
    instances_val2017 = instances_val2017['annotations']


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


# Function to find categories by image_id
def find_categories(image_id, coco_split):
    # Decide which split to use for annotations and categories
    if coco_split == 'train2017':
        annotations = instances_train2017
        categories_list = categories_train2017
    elif coco_split == 'val2017':
        annotations = instances_val2017
        categories_list = categories_val2017
    else:
        return None

    # Find annotations for the specified image
    image_annotations = [ann for ann in annotations if ann['image_id'] == int(image_id)]

    # Extract category IDs and get category names and supercategories
    categories = [{'category_id': ann['category_id'], 
                   'category_name': next((cat['name'] for cat in categories_list if cat['id'] == ann['category_id']), None), 
                   'supercategory_name': next((cat['supercategory'] for cat in categories_list if cat['id'] == ann['category_id']), None)} 
                  for ann in image_annotations]

    return categories


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

# Add captions and categories to the data
for item in data:
    item['caption'] = find_caption(item['cocoId'], item['cocoSplit'])
    categories = find_categories(item['cocoId'], item['cocoSplit'])
    if categories:
        item['categories'] = categories
    else:
        item['categories'] = None

# Save the final data to a JSON file
with open('data/captions_and_categories.json', 'w') as file:
    json.dump(data, file)
