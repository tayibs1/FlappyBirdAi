import optuna
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import f1_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Load the prepared data from the .pkl file
X_train_resampled, y_train_resampled, X_test, y_test = joblib.load("prepared_data.pkl")

# Define the objective function for Optuna
def objective(trial):
    # Suggest hyperparameters for Random Forest
    n_estimators = trial.suggest_int("n_estimators", 10, 100)
    max_depth = trial.suggest_int("max_depth", 3, 20)
    min_samples_split = trial.suggest_int("min_samples_split", 2, 20)
    min_samples_leaf = trial.suggest_int("min_samples_leaf", 1, 10)
    class_weight = trial.suggest_categorical("class_weight", [None, "balanced"])

    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        min_samples_leaf=min_samples_leaf,
        class_weight=class_weight,
        random_state=42
    )
    model.fit(X_train_resampled, y_train_resampled)

    y_pred = model.predict(X_test)
    return f1_score(y_test, y_pred, pos_label=1)


# Create and run the Optuna study
study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=50)

# Best hyperparameters
print("Best Hyperparameters:", study.best_params)

# Train the model with the best hyperparameters
best_params = study.best_params
final_model = RandomForestClassifier(**best_params, random_state=42)
final_model.fit(X_train_resampled, y_train_resampled)

# Save the optimized model to a new .pkl file
joblib.dump(final_model, "optimized_decision_tree_model.pkl")
print("Optimized Decision Tree model saved to 'optimized_decision_tree_model.pkl'")
