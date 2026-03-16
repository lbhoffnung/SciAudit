# Guia de Contribuição: SciAudit

Obrigado por se interessar em tornar a ciência de dados mais íntegra! O SciAudit cresce através de novas "Leis Científicas".

## 🛠 Como adicionar uma nova Regra (Rule)

1.  **Escolha a Categoria**: As regras estão organizadas em `sciaudit/rules/`:
    - `leakage/`: Para vazamento de dados.
    - `reproducibility/`: Para reprodutibilidade.
    - `statistics/`: Para rigor estatístico.
    - `causal/`: Para interpretação e causalidade.

2.  **Crie a sua Classe**: Sua regra deve herdar de `ScientificRule`. 
    Obrigatório implementar:
    - `rule_id`: "SCI-XXX"
    - `rule_name`: Nome amigável (ex: "Data Leakage").
    - `default_severity`: `Severity.ERROR`, `WARNING` ou `INFO`.
    - `hint`: Uma dica acionável (ex: "Use train_test_split antes...").

    ```python
    from ..base import ScientificRule
    from ...core.models import Severity

    class MinhaNovaRegra(ScientificRule):
        @property
        def rule_id(self) -> str: return "SCI-XXX"
        @property
        def rule_name(self) -> str: return "Nome Curto"
        @property
        def default_severity(self) -> Severity: return Severity.WARNING
        
        def visit_Call(self, node):
            # Lógica AST
            self.add_violation(message="Detecção!", line=node.lineno, hint="Faça X.")
    ```

3.  **Registre a Regra**: Adicione sua regra no arquivo `sciaudit/cli/main.py` dentro da função `get_engine()`.

4.  **Adicione ao Corpus**: Crie exemplos positivos e negativos em `corpus/good/` e `corpus/bad/`.

## 🧪 Rodando Testes e Avaliação

### Testes Unitários
```bash
$env:PYTHONPATH="."
python -m unittest discover tests
```

### Avaliação de Corpus (Calibragem)
Para verificar se sua regra está disparando muitos falsos positivos ou se está detectando os casos reais corretamente:
```bash
python tools/eval_corpus.py
# Verifique rule_metrics.csv
```

## ⚖️ Critérios para novas regras
- Deve ser baseada em **análise estática** (AST).
- Deve focar em **metodologia científica**, não apenas estilo de código.
- Deve ter uma mensagem educativa explicando o "porquê" do erro.

---
*Vamos elevar o nível da ciência de dados juntos!*
