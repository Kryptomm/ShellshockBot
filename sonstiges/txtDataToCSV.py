import pandas as pd

# File paths
input_file = 'data/WindPixels.txt'
output_file = 'binary_data.csv'

# Read the text file
data = []
with open(input_file, 'r') as file:
    for line in file:
        # Split the line into features and label
        parts = line.strip().split()
        features = list(map(int, parts[2:]))  # Convert features to integers
        label = int(parts[0])  # Convert label to integer
        data.append(features + [label])

# Determine the number of features
num_features = len(data[0]) - 1

# Create a DataFrame
columns = [f'feature{i+1}' for i in range(num_features)] + ['label']
df = pd.DataFrame(data, columns=columns)

# Write to CSV
df.to_csv(output_file, index=False)

print(f"CSV file '{output_file}' created successfully.")
