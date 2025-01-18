import pandas as pd

# Load the data from CSV
data = pd.read_csv("gameplay_data.csv")

# Display the first few rows
print(data.head())

# Check for missing or invalid data
print(data.info())
