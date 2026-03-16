import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

df = pd.read_csv("data.csv")
# X is derived only from non-target columns
X = df.drop("outcome", axis=1)
y = df["outcome"]

# Good Practice: Split BEFORE transform
X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = RandomForestClassifier(random_state=42)

# Use cross-validation on train set
print(f"CV Accuracy: {cross_val_score(model, X_tr, y_tr, cv=5).mean():.2f}")

model.fit(X_tr, y_tr)
print(f"Test Score: {model.score(X_te, y_te)}")
