import json
import matplotlib.pyplot as plt

# Load the data from the JSON file
with open('data/captions_and_categories.json', 'r') as file:
    data = json.load(file)

# Function to count occurrences of each supercategory and category
def count_categories(data):
    supercategory_counts = {}
    category_counts = {}

    for item in data:
        if 'categories' in item and item['categories'] is not None:
            unique_supercategories = set()
            unique_categories = set()
            for category in item['categories']:
                # Count supercategories, ensuring each supercategory is counted only once per image
                supercat_name = category['supercategory_name']
                if supercat_name not in unique_supercategories:
                    unique_supercategories.add(supercat_name)
                    supercategory_counts[supercat_name] = supercategory_counts.get(supercat_name, 0) + 1

                # Count categories, ensuring each category is counted only once per image
                cat_name = category['category_name']
                if cat_name not in unique_categories:
                    unique_categories.add(cat_name)
                    category_counts[cat_name] = category_counts.get(cat_name, 0) + 1

    return supercategory_counts, category_counts

# Count occurrences of each supercategory and category
supercategory_counts, category_counts = count_categories(data)

# Sort supercategory_counts by occurrence
sorted_supercategory_counts = dict(sorted(supercategory_counts.items(), key=lambda item: item[1], reverse=True))

# Get the top 20 categories by occurrence and sort them
top_categories = sorted(category_counts.items(), key=lambda item: item[1], reverse=True)[:20]
top_cat_names, top_cat_counts = zip(*top_categories)  # Unzipping the list of tuples

# top_supercategories = sorted(supercategory_counts.items(), key=lambda item: item[1], reverse=True)[:3]
# total_images = len(data)
# print(total_images)
# # Print the percentage of images with the top 3 supercategories
# for supercat, count in top_supercategories:
#     percentage = (count / total_images) * 100
#     print(f"{supercat}: {percentage:.2f}% of images")

# Set the font to Times New Roman for all text in the plots
plt.rcParams['font.family'] = 'Times New Roman'

# Plot for supercategories
plt.figure(figsize=(12, 6))  # Make figure shorter and wider
plt.bar(sorted_supercategory_counts.keys(), sorted_supercategory_counts.values())
plt.xlabel('Supercategory', fontsize=26)  # Increase font size for x-axis title
plt.ylabel('Occurrences', fontsize=26)  # Increase font size for y-axis title
plt.xticks(rotation=45, ha='right', fontsize=22)  # Increase font size for x-axis ticks
plt.yticks(fontsize=14)  # Increase font size for y-axis ticks
plt.tick_params(axis='both', which='major', labelsize=14)  # Increase the font size of the tick labels
plt.subplots_adjust(bottom=0.25)  # Adjust bottom margin to prevent cutting off labels
plt.tight_layout()
plt.savefig('data/supercategories_histogram_larger.png')  # Save the figure
plt.show()

# Plot for top 20 categories
# plt.figure(figsize=(10, 8))
# plt.bar(top_cat_names, top_cat_counts)
# plt.yscale('log')  # Set the y-axis to a logarithmic scale
# plt.title('Top 20 Categories by Occurrence', fontsize=26, pad=20)  # Increase title font size and add padding
# plt.xlabel('Category', fontsize=18)  # Increase font size for x-axis title
# plt.ylabel('Occurrences (Log Scale)', fontsize=18)  # Increase font size for y-axis title
# plt.xticks(rotation=45, ha='right')
# plt.subplots_adjust(bottom=0.20)  # Adjust bottom margin to prevent cutting off labels
# plt.tight_layout()
# plt.savefig('data/categories_histogram.png')  # Save the figure
# plt.show()