import numpy as np

def read_lw6(filename):
    with open(filename, 'rb') as file:
        file_content = file.read()

    # Try reading without reshaping
    data = np.frombuffer(file_content, dtype=np.float32)
    return data

file_path = 'subj06.lw6'
data = read_lw6(file_path)

print("Data shape:", data.shape)
print(data)
