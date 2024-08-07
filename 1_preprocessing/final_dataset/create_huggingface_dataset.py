import os
import pandas as pd
from datasets import Features, Dataset, DatasetDict, Sequence, Value
from dotenv import load_dotenv
import json

DSET_NAME = "fulltest"
DATASET_PATH = '/srv/eeg_reconstruction/shared/biosemi-dataset/final_hdf5/' + DSET_NAME

load_dotenv()
HF_PUSH = os.getenv("HF_PUSH")

file_path = 'test_indices.json'

with open(file_path, 'r') as file:
    split_array = json.load(file)

def generate_hf_dataset(df_path, split_criteria, split):
    df = pd.read_hdf(df_path, key="df")
    for _, row in df.iterrows():
        is_test = split_criteria(row['73k_id'])
        if (split == 'train' and not is_test) or (split == 'test' and is_test): 
            yield {
                'EEG': row["eeg"],
                'subject_id': row['subject_id'],
                'session': row['session'],
                'block': row['block'],
                'trial': row['trial'],
                '73k_id': row['73k_id'],
                'coco_id': row['coco_id'],
                'curr_time': row['curr_time'],
            }


def aggregate_hf_datasets(folder_path, split_criteria, split):
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".h5"):
            df_path = os.path.join(folder_path, file_name)
            yield from generate_hf_dataset(df_path, split_criteria, split)


print("Creating hf dataset")
dset_features = Features({
    'EEG': Sequence(feature=Sequence(feature=Value('float64'))),
    'subject_id': Value('int32'),
    'session': Value('int32'),
    'block': Value('int32'),
    'trial': Value('int32'),
    '73k_id': Value('int32'), #0-indexed
    'coco_id': Value('int32'),
    'curr_time': Value('float32'),
})

# img_id is 73k id, 0-indexed
# returns bool, true if it belongs in test set
def split_criteria(img_id):
    return img_id in split_array

train_dataset = Dataset.from_generator(generator=aggregate_hf_datasets, gen_kwargs={"folder_path": DATASET_PATH, "split_criteria": split_criteria, "split": "train"}, features=dset_features, cache_dir="huggingface")
test_dataset = Dataset.from_generator(generator=aggregate_hf_datasets, gen_kwargs={"folder_path": DATASET_PATH, "split_criteria": split_criteria, "split": "test"}, features=dset_features, cache_dir="huggingface")

dataset_dict = DatasetDict({
    'train': train_dataset,
    'test': test_dataset
})

dataset_dict.push_to_hub("Alljoined/" + DSET_NAME, token=HF_PUSH)