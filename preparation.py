import pandas as pd
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import joblib

# Step 1: Load the cleaned and normalized data
data = pd.read_csv("cleaned_gameplay_data.csv")

# Step 2: Split the data into features (X) and target labels (y)
X = data[["bird_y", "bird_velocity", "pipe_x", "pipe_height"]]
y = data["action"]

# Step 3: Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Balance the training set using SMOTE
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

# Step 5: Save the prepared datasets using joblib
joblib.dump((X_train_resampled, y_train_resampled, X_test, y_test), "prepared_data.pkl")

# Print confirmation
print("Prepared datasets saved to 'prepared_data.pkl'")
