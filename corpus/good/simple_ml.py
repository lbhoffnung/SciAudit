import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier

# Load data correctly
data = load_iris()
X = pd.DataFrame(data.data, columns=data.feature_names)
y = data.target

# Split before any processing
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

# Use cross-validation for evaluation
clf = RandomForestClassifier(random_state=42)
print(f"CV Accuracy: {cross_val_score(clf, X_tr, y_tr, cv=5).mean():.2f}")

# Final fit
clf.fit(X_tr, y_tr)
print(f"Test Accuracy: {clf.score(X_te, y_te):.2f}")
