import json
import random
from collections import defaultdict

def load_data(filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data

def organize_by_supercategory(data):
    supercategory_images = defaultdict(set)
    image_supercategories = defaultdict(set)
    for index, item in enumerate(data):
        for category in item['categories']:
            supercategory = category['supercategory_name']
            supercategory_images[supercategory].add(index)
            image_supercategories[index].add(supercategory)
    return supercategory_images, image_supercategories

def select_test_images(supercategory_images, total_images_count):
    total_indices = set(range(total_images_count))
    test_indices = set()
    for supercategory, indices in sorted(supercategory_images.items(), key=lambda x: len(x[1])):
        needed_for_test = max(0, round(len(indices) * 0.2) - len(test_indices & indices))
        additional_test_indices = random.sample(indices - test_indices, min(needed_for_test, len(indices - test_indices)))
        test_indices.update(additional_test_indices)
    
    # Ensure overall 20% split
    overall_needed_for_test = round(total_images_count * 0.2) - len(test_indices)
    print("Overall needed for test: " + str(overall_needed_for_test))
    if overall_needed_for_test > 0:
        additional_overall_test_indices = random.sample(total_indices - test_indices, min(overall_needed_for_test, len(total_indices - test_indices)))
        test_indices.update(additional_overall_test_indices)
    
    return test_indices

data = load_data('data/captions_and_categories.json')
supercategory_images, _ = organize_by_supercategory(data)
test_indices = select_test_images(supercategory_images, len(data))

print(f"Selected indices for the test set: {sorted(test_indices)}")
print(f"Number of selected test images: {len(test_indices)}")

# Save the selected test indices to a JSON file
with open('data/test_indices.json', 'w') as file:
    json.dump(list(sorted(test_indices)), file)