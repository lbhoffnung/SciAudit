# Guia de Contribuição: SciAudit

Obrigado por se interessar em tornar a ciência de dados mais íntegra! O SciAudit cresce através de novas "Leis Científicas".

## 🛠 Como adicionar uma nova Regra (Rule)

1.  **Escolha a Categoria**: As regras estão organizadas em `sciaudit/rules/`:
    - `leakage/`: Para vazamento de dados.
    - `reproducibility/`: Para reprodutibilidade.
    - `statistics/`: Para rigor estatístico.
    - `causal/`: Para interpretação e causalidade.

2.  **Crie a sua Classe**: Sua regra deve herdar de `ScientificRule` e implementar os métodos necessários.
    ```python
    from ..base import ScientificRule
    from ...core.models import Violation, Severity

    class MinhaNovaRegra(ScientificRule):
        @property
        def rule_id(self) -> str:
            return "SCI-XXX" # Próximo ID disponível

        @property
        def description(self) -> str:
            return "Breve descrição da violação."

        def visit_Call(self, node):
            # Sua lógica de detecção via AST aqui
            pass
    ```

3.  **Registre a Regra**: Adicione sua regra no arquivo `sciaudit/cli/main.py` na função `run_audit`.

4.  **Adicione Testes**: Crie um teste em `tests/test_rules.py` que valide sua detecção.

## 🧪 Rodando Testes Localmente

```bash
python -m unittest discover tests
```

## ⚖️ Critérios para novas regras
- Deve ser baseada em **análise estática** (AST).
- Deve focar em **metodologia científica**, não apenas estilo de código.
- Deve ter uma mensagem educativa explicando o "porquê" do erro.

---
*Vamos elevar o nível da ciência de dados juntos!*
