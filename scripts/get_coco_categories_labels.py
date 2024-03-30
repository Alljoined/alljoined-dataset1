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


def find_captions(image_id, coco_split):
    if coco_split == 'train2017':
        caption_list = captions_train2017
    elif coco_split == 'val2017':
        caption_list = captions_val2017
    else:
        return None

    captions = [caption['caption'] for caption in caption_list if caption['image_id'] == int(image_id)]
    return captions


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

    # Use a set to store unique category IDs
    unique_category_ids = set()

    # Extract category IDs and get category names and supercategories
    categories = []
    for ann in image_annotations:
        category_id = ann['category_id']
        if category_id not in unique_category_ids:
            unique_category_ids.add(category_id)
            category = next((cat for cat in categories_list if cat['id'] == category_id), None)
            if category:
                category_info = {
                    'category_id': category_id,
                    'category_name': category['name'],
                    'supercategory_name': category['supercategory']
                }
                categories.append(category_info)

    return categories


# Read the 1000 shared nsd ids from the json file and get additional info from the csv file
with open('data/coco_indices.json', 'r') as file:
    coco_idx = json.load(file)

csv_file_path = 'data/nsd_stim_info_merged.csv'
data = []
image_counter = 0 
with open(csv_file_path, 'r') as file:
    for i, idx in enumerate(coco_idx):
        if image_counter >= 2:  # Check if 960 images have been read
            break  # Exit the loop if the limit is reached
        print(f"Reading index {idx}. Progress: {i+1}/{len(coco_idx)}")
        isFound = False
        for row in csv.DictReader(file):
            if row['nsdId'] == str(idx-1):
                data.append({'nsdId': row['nsdId'], 'cocoId': row['cocoId'], 'cocoSplit': row['cocoSplit']})
                isFound = True
                image_counter += 1  # Increment the counter for each image read
                break
        if not isFound:
            print(f"Index {idx} not found in csv file.")
        file.seek(0)

# Add captions and categories to the data
for item in data:
    item['captions'] = find_captions(item['cocoId'], item['cocoSplit'])  # Changed to 'captions' and 'find_captions'
    categories = find_categories(item['cocoId'], item['cocoSplit'])
    if categories:
        item['categories'] = categories
    else:
        item['categories'] = None

# Save the final data to a JSON file
with open('data/captions_and_categories_test.json', 'w') as file:
    json.dump(data, file)
