# SciAudit: O Manifesto da Integridade Científica em Código

> "Se a sua ciência não é verificável, ela não é ciência. É opinião com dados."

## 1. O Problema
A "Crise de Reprodutibilidade" não é apenas sobre não ter o ambiente de software correto; é sobre **erros metodológicos invisíveis**. Scripts rodam, mas as conclusões são falsas porque o processo científico foi violado.

## 2. A Missão do SciAudit
Ser o padrão ouro de auditoria silenciosa. Uma ferramenta que:
1.  **Analisa a Genealogia do Dado**: Detecta quando o "futuro" informa o "passado" (Data Leakage).
2.  **Pune a Falta de Reprodutibilidade**: Exige sementes determinísticas e separação clara de pipelines.
3.  **Avalia o Processo, não o Resultado**: Não nos importa se o seu R² é 0.99 se o seu método é 0.0 em honestidade.

## 3. Os Princípios Core
- **Zero Dependência**: Uma biblioteca de integridade não pode sofrer de "Dependency Hell". Ela deve ser pura.
- **Transparência**: Toda regra de auditoria deve ter uma base teórica explicável.
- **Não-Invasivo**: O SciAudit lê o seu código, ele não o altera (Análise Estática).

## 4. O Sistema de Scoring
Projetos serão avaliados de **A+** a **F**, baseados no número de violações metodológicas detectadas.
- **A+ (Verificado)**: Perfeito para peer-review e produção crítica.
- **C (Alerta)**: Contém "smells" estatísticos que podem invalidar o modelo.
- **F (Vazamento)**: Violações críticas detectadas (ex: Target Leakage).
