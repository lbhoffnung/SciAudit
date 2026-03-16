import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier

# Load data correctly
data = load_iris()
X = pd.DataFrame(data.data, columns=data.feature_names)
y = data.target

# Split before any processing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Use cross-validation for evaluation
clf = RandomForestClassifier(random_state=42)
scores = cross_val_score(clf, X_train, y_train, cv=5)
print(f"CV Accuracy: {scores.mean():.2f}")

# Final fit
clf.fit(X_train, y_train)
test_score = clf.score(X_test, y_test)
print(f"Test Accuracy: {test_score:.2f}")
