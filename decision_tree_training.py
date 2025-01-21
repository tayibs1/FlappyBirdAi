import joblib
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pandas as pd

# Step 1: Load the optimized model
model_path = "optimized_decision_tree_model.pkl"
optimized_model = joblib.load(model_path)
print("Optimized Decision Tree model loaded successfully!")

# Step 2: Load the prepared test data
data_path = "prepared_data.pkl"
_, _, X_test, y_test = joblib.load(data_path)
print("Test data loaded successfully!")

# Step 3: Make predictions
y_pred = optimized_model.predict(X_test)

# Step 4: Evaluate performance
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy on testing set: {accuracy:.2f}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:")
conf_matrix = confusion_matrix(y_test, y_pred)
print(conf_matrix)

# Optional: Save test results to a CSV file
results_df = pd.DataFrame({"Actual": y_test, "Predicted": y_pred})
results_df.to_csv("test_results.csv", index=False)
print("Test results saved to 'test_results.csv'")
