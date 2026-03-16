# 🛡️ SciAudit

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen)](https://github.com/seu-usuario/SciAudit)

> **"Seu paper/produção está pronto para o peer-review? O SciAudit diz sim ou não em 1 minuto."**

O **SciAudit** é o primeiro linter do mundo focado não na qualidade do código, mas na **integridade da ciência**. Ele escaneia seus scripts Python e Jupyter Notebooks em busca de violações metodológicas comuns que invalidam resultados de Data Science e Machine Learning.

---

## 🚀 Por que SciAudit?

A maioria dos linters (como Pylint ou Flake8) verifica se seu código é bonito. O SciAudit verifica se seu código é **honesto**.

- **Detecta Data Leakage**: Identifica se você "vazou" o futuro para o passado (ex: normalizar dados antes do split).
- **Garante Reprodutibilidade**: Exige sementes determinísticas (`random_state`) em funções estocásticas.
- **Evita o "Multicollinearity Trap"**: Alerta sobre interpretações de importância de features sem análise de correlação prévia.
- **Zero Dependências**: Funciona "out of the box" usando apenas a biblioteca padrão do Python.
- **Suporte a Notebooks**: Audita arquivos `.ipynb` diretamente.

---

## 📦 Instalação

Como o SciAudit não possui dependências, a instalação é instantânea:

```bash
pip install sciaudit
```

---

## 🛠️ Como Usar

### No Terminal
Audite um arquivo ou diretório inteiro:

```bash
# Rodar auditoria no diretório atual
sciaudit .

# Rodar em um script específico e gerar um laudo em Markdown
sciaudit meu_experimento.py --report
```

### O Laudo de Integridade
Ao usar a flag `--report`, o SciAudit gera um arquivo `SCIAUDIT_REPORT.md` contendo:
- **Score Global (A+ a F)**.
- **Tabela de Violações**.
- **Sugestões de Remediação** teóricas e práticas.
- **Badge de Integridade** para você colar no seu README.

---

## 📜 Leis Científicas Implementadas (12+)

O SciAudit organiza suas regras em categorias críticas:

### 🔴 Leakage (Vazamento)
| ID | Nome | Descrição |
| :--- | :--- | :--- |
| **SCI-001** | Data Leakage | Transformações (fit/transform) ocorrendo antes do split. |
| **SCI-006** | Contaminação | Uso de `X_test` ou `y_test` dentro do método `fit()`. |
| **SCI-007** | Time Leakage | Reordenação (`sort_values`) de dados temporais após o split. |
| **SCI-008** | Label Leakage | Criação de features derivadas diretamente da variável alvo. |

### 🟡 Estatística & Rigor
| ID | Nome | Descrição |
| :--- | :--- | :--- |
| **SCI-004** | P-Value Hacking | Múltiplas comparações estatísticas sem correção de Bonferroni/FDR. |
| **SCI-005** | Overfitting Cego | Uso de métricas (`accuracy`, `r2`) sem Cross-Validation detectável. |
| **SCI-009** | Imbalance Ignored | Uso de acurácia em datasets desbalanceados sem checagem prévia. |
| **SCI-014** | Silent NaN Drop | Remoção de dados faltantes (`dropna`) sem log/print do impacto. |

### 🟢 Metodologia & Causalidade
| ID | Nome | Descrição |
| :--- | :--- | :--- |
| **SCI-003** | Multicolinearidade | Interpretação de importância de features sem análise de correlação. |
| **SCI-013** | Causal Hubris | Afirmações de causalidade em comentários sem evidência de rigor. |
| **SCI-002** | Random Seed | Falta de `random_state` em funções estocásticas. |
| **SCI-017** | Time Shuffle | Embaralhamento de dados temporais que destrói a ordem cronológica. |

---

## 💡 Manifesto

O SciAudit nasceu para combater a **crise de reprodutibilidade** na ciência de dados. Acreditamos que a integridade deve ser automatizada e que todo modelo de alta performance deve ser, antes de tudo, um modelo de alta honestidade.

---
Desenvolvido com ❤️ para a comunidade científica.
