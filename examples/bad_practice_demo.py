# SciAudit Demo: Exemplos de Violações Críticas

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import scipy.stats as stats

df = pd.read_csv("data.csv")
# SCI-008: Label Leakage (Target usado para criar feature)
df['feature_suspeita'] = df['target'] * 1.5

X = df.drop('target', axis=1)
y = df['target']

X_train, X_test, y_train, y_test = train_test_split(X, y)

# SCI-007: Time Leakage (Sort após split)
X_test = X_test.sort_values(by='data')

# SCI-006: Test Set Contamination (Usando X_test no fit!)
model = RandomForestClassifier()
model.fit(X_test, y_test) 

# SCI-005: Overfitting Cego (Métrica sem Cross-Validation)
preds = model.predict(X_test)
acc = accuracy_score(y_test, preds)

# SCI-004: P-Hacking (Múltiplos testes sem correção)
stats.ttest_ind(X_train['a'], X_train['b'])
stats.ttest_ind(X_train['c'], X_train['d'])
stats.ttest_ind(X_train['e'], X_train['f'])
stats.ttest_ind(X_train['g'], X_train['h'])
stats.ttest_ind(X_train['i'], X_train['j'])

# SCI-014: Silent NaN Drop
df.dropna(inplace=True) # Nenhum print/log depois

# SCI-013: Causal Hubris
# Esta variável causa um impacto direto no lucro
lucro = model.predict(X_test)

print("Fim do script sujo.")
