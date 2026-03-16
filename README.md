# 🛡️ SciAudit

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen)](https://github.com/lbhoffnung/SciAudit)

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

---

## 🏭 Uso em Produção (CI/CD)

O SciAudit foi projetado para ser integrado ao seu fluxo de trabalho de desenvolvimento.

### ⚓ Pre-commit Hooks
Adicione isto ao seu `.pre-commit-config.yaml`:
```yaml
repos:
-   repo: local
    hooks:
    -   id: sciaudit
        name: SciAudit
        entry: sciaudit
        language: system
        types: [python]
        files: \.(py|ipynb)$
```

### 🤖 GitHub Actions
Exemplo de workflow para `.github/workflows/sciaudit.yml`:
```yaml
name: SciAudit CI
on: [push, pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.10' }
      - run: pip install sciaudit
      - run: sciaudit . --exit-code-strategy any-error
```

---

## ⚙️ Configuração (`.sciaudit.yml`)

Você pode personalizar o comportamento do SciAudit criando um arquivo `.sciaudit.yml` na raiz do seu projeto:

```yaml
rules:
  SCI-002: warning   # Forçar para warning
  SCI-003: off       # Desativar regra
  SCI-006: error     # Forçar para erro

paths:
  ignore:
    - "venv/"
    - "legacy_tests/"
    - "notebooks/backup/"
```

### Sugestões Detalhadas
Use a flag `--suggest-fix` para receber dicas acionáveis sobre como resolver cada violação:
```bash
sciaudit meu_script.py --suggest-fix
```

---

## 🎮 Perfis de Rigor (`--profile`)

Nem todo projeto exige o mesmo nível de rigor. O SciAudit oferece três perfis pré-definidos:

| Perfil | Descrição | Uso Ideal |
| :--- | :--- | :--- |
| `balanced` (Padrão) | Severidades padrão das regras. | Uso geral em Data Science. |
| `strict` | Eleva quase todas as regras para `ERROR`. | Projetos médicos, financeiros ou teses. |
| `relaxed` | Diminui o rigor de regras controversas. | Protipagem rápida e exploração. |

---

## 🧱 Modo Baseline (Adoção em código legado)

Se você está adotando o SciAudit em um projeto antigo com centenas de alertas, use o modo **baseline**. Ele permite ignorar violações antigas e focar apenas no que foi introduzido de novo:

1. **Crie o baseline inicial**:
   ```bash
   sciaudit . --create-baseline sciaudit-baseline.json
   ```
2. **Use o baseline no CI**:
   ```bash
   sciaudit . --baseline sciaudit-baseline.json
   ```
*Nota: O exit code retornará 0 se houver apenas violações presentes no baseline. Violações novas quebrarão o build.*

---

## ⚙️ Configuração (`.sciaudit.yml`)

Você pode personalizar o comportamento do SciAudit criando um arquivo `.sciaudit.yml` na raiz do seu projeto. A configuração no arquivo tem **precedência total** sobre os perfis.

```yaml
rules:
  SCI-002: warning   # Forçar para warning
  SCI-003: off       # Desativar regra
  SCI-006: error     # Forçar para erro

paths:
  ignore:
    - "venv/"
    - "legacy_tests/"
```

### Estratégias de Exit Code
- `--exit-code-strategy any-error` (Padrão): Falha no build se houver qualquer violação `ERROR` ou `WARNING` (não presente no baseline).
- `--exit-code-strategy errors-only`: Falha no build apenas em caso de violações `ERROR`.
- `--exit-code-strategy always-zero`: Nunca falha o build.

---

## 🎨 Exemplos Reais

### ❌ Exemplo de Código Ruim (`leakage.py`)
```python
import pandas as pd
from sklearn.preprocessing import StandardScaler

df = pd.read_csv("data.csv")
# VIOLAÇÃO SCI-001: Fit antes do split!
scaler = StandardScaler()
df_scaled = scaler.fit_transform(df)

train, test = train_test_split(df_scaled)
```

### 🖥️ Saída do SciAudit
```text
  ● SCI-001 [error] Data Leakage
    A função 'fit_transform' foi chamada antes de um split de dados ser detectado.
    ➔ Sugestão: Aplique o split (train_test_split) ANTES de qualquer fit/transform.
    Linha 7: df_scaled = scaler.fit_transform(df)
```

---

## ⚠️ Limitações e Isenção de Responsabilidade

- **Análise Estática**: O SciAudit usa AST (Abstract Syntax Tree). Ele não executa o código. Se você usar métodos altamente dinâmicos (`exec`, `getattr` complexos), a detecção pode ser limitada.
- **Falsos Positivos**: Algumas regras (especialmente SCI-008 e SCI-013) usam heurísticas textuais e de nomenclatura. Elas servem como alertas para revisão humana, não como verdades absolutas.
- **Não Substitui o Peer-Review**: Esta ferramenta é um assistente, não um juiz final. A integridade científica final é responsabilidade dos autores.

---

## 📜 Leis Científicas Implementadas (12+)

O SciAudit organiza suas regras em categorias críticas, cada uma com uma severidade padrão:

### 🔴 Leakage (Vazamento) - Severidade: ERROR
| ID | Nome | Descrição |
| :--- | :--- | :--- |
| **SCI-001** | Data Leakage | Transformações (fit/transform) ocorrendo antes do split. |
| **SCI-006** | Contaminação | Uso de `X_test` ou `y_test` dentro do método `fit()`. |
| **SCI-007** | Time Leakage | Reordenação (`sort_values`) de dados temporais após o split. |
| **SCI-008** | Label Leakage | Criação de features derivadas diretamente da variável alvo. |
| **SCI-017** | Time Shuffle | Embaralhamento de dados temporais em splits cronológicos. |

### 🟡 Estatística & Rigor - Severidade: WARNING
| ID | Nome | Descrição |
| :--- | :--- | :--- |
| **SCI-002** | Random Seed | Falta de `random_state` em funções estocásticas. |
| **SCI-004** | P-Value Hacking | Múltiplas comparações estatísticas sem correção de Bonferroni/FDR. |
| **SCI-005** | Overfitting Cego | Uso de métricas (`accuracy`, `r2`) sem Cross-Validation detectável. |
| **SCI-009** | Imbalance Ignored | Uso de acurácia em datasets desbalanceados sem checagem prévia. |
| **SCI-014** | Silent NaN Drop | Remoção de dados faltantes (`dropna`) sem log/print do impacto. |

### 🔵 Metodologia & Causalidade - Severidade: INFO
| ID | Nome | Descrição |
| :--- | :--- | :--- |
| **SCI-003** | Multicolinearidade | Interpretação de importância de features sem análise de correlação. |
| **SCI-013** | Causal Hubris | Afirmações de causalidade em comentários sem evidência de rigor. |

---

## 💡 Manifesto

O SciAudit nasceu para combater a **crise de reprodutibilidade** na ciência de dados. Acreditamos que a integridade deve ser automatizada e que todo modelo de alta performance deve ser, antes de tudo, um modelo de alta honestidade.

---
Desenvolvido com ❤️ por Lucas Hoffnung Bernardo ([@lbhoffnung](https://github.com/lbhoffnung)) para a comunidade científica.
