import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Load the data from CSV
data = pd.read_csv("gameplay_data.csv")

# Step 2: Clean the Data

# 1. Remove Missing Data
data = data.dropna()

# 2. Remove Duplicate Rows
data = data.drop_duplicates()

# 3. Normalize Features
scaler = MinMaxScaler()
feature_columns = ["bird_y", "bird_velocity", "pipe_x", "pipe_height"]
data[feature_columns] = scaler.fit_transform(data[feature_columns])

# 4. Verify Cleaned Data
print(data.describe())

# Save the cleaned and normalized data to a new CSV file (optional)
data.to_csv("cleaned_gameplay_data.csv", index=False)
