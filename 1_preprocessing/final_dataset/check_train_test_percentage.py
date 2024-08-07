import json
from collections import defaultdict

def load_data(filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data

def organize_by_supercategory(data):
    supercategory_images = defaultdict(set)
    for index, item in enumerate(data):
        for category in item['categories']:
            supercategory = category['supercategory_name']
            supercategory_images[supercategory].add(index)
    return supercategory_images

# Load the original data to recreate the supercategory_images mapping
data = load_data('data/captions_and_categories.json')
supercategory_images = organize_by_supercategory(data)

# Load the test indices from the JSON file
with open('data/test_indices_fixed.json', 'r') as file:
    test_indices = set(json.load(file))

# Calculate the percentage of each supercategory in the test indices
supercategory_percentage = {}
for supercategory, indices in supercategory_images.items():
    test_count = len(test_indices & indices)
    supercategory_percentage[supercategory] = (test_count / len(indices)) * 100

# Print the percentage of test images for each supercategory
for supercategory, percentage in supercategory_percentage.items():
    print(f"Supercategory: {supercategory}, Test Percentage: {percentage:.2f}%")