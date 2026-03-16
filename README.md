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

## 📜 Leis Científicas Implementadas

| ID | Nome | Descrição |
| :--- | :--- | :--- |
| **SCI-001** | Data Leakage | Transformações de dados (fit/transform) ocorrendo antes do split. |
| **SCI-002** | Reprodutibilidade | Falta de `random_state` ou `seed` em modelos e processos aleatórios. |
| **SCI-003** | Multicolinearidade | Acesso a `feature_importances_` sem prova de análise de correlação. |

---

## 💡 Manifesto

O SciAudit nasceu para combater a **crise de reprodutibilidade** na ciência de dados. Acreditamos que a integridade deve ser automatizada e que todo modelo de alta performance deve ser, antes de tudo, um modelo de alta honestidade.

---
Desenvolvido com ❤️ para a comunidade científica.
