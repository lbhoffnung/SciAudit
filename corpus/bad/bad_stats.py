import pandas as pd
from sklearn.metrics import accuracy_score
import numpy as np

# Load imbalanced data
df = pd.DataFrame({
    'feature': np.random.randn(100),
    'target': [0]*95 + [1]*5
})

# Missing seed/random_state
X = df[['feature']]
y = df['target']

# Dropping NaNs silently
df.dropna(inplace=True)

# P-hacking: testing multiple thresholds until it looks "good"
for t in [0.1, 0.2, 0.3, 0.4, 0.5]:
    pred = (X > t).astype(int)
    # Ignoring class imbalance by only using accuracy
    acc = accuracy_score(y, pred)
    print(f"Threshold {t}: Accuracy {acc}")
