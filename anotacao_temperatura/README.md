# Etapa 2: anotação de descrições de temperatura

## Fonte

| | |
| --- | --- |
| Arquivo de origem | `resultados_json/corpus.jsonl` |
| Versão no repositório | tag `etapa1` (commit `XXXXXXX`) |
| Versão do UniProt | 2026_03 |
| Descrições no corpus | 8987 (3284 de temperatura) |
| Anotador | [seu nome] |
| Guia | `guia_anotacao_temperatura_etapa2.md`, versão 1.0, de 29/10/2026 |

## Sorteio

As descrições com `property_type` igual a `temperature_dependence` foram ordenadas por `description_id`, e 100 foram sorteadas sem reposição com semente 42, pelo `codigo/sortear_temperatura.py` (Python 3.14.8). A lista sorteada, reordenada por `description_id`, está em `amostra_temperatura.csv` e é a referência definitiva da seleção.

## Uso de IA

Nenhuma sugestão automática foi usada na classificação.

## Verificações

_preencher ao final_

## Decisões de revisão

_responsável, data e decisão de cada caso revisado_

## Pendências

_description_id e a dúvida de cada caso pendente_