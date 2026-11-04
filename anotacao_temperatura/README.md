# Etapa 2: anotação de descrições de temperatura

## Fonte

| | |
| --- | --- |
| Arquivo de origem | `resultados_json/corpus.jsonl` |
| Versão do corpus usada | tag `etapa1`, na branch `corpus` (commit `9e2ac44`) |
| Versão do UniProt | 2026_03 |
| Descrições no corpus | 8987 (3284 de temperatura) |
| Anotador | Ricardo Risson Machado |
| Guia | `guia_anotacao_temperatura_etapa2.md`, versão 1.0, de 29/10/2026 |

## Sorteio

As descrições com `property_type` igual a `temperature_dependence` foram ordenadas por `description_id`, e 100 foram sorteadas sem reposição com semente 42, pelo `codigo/sortear_temperatura.py` (Python 3.14.8). A lista sorteada, reordenada por `description_id`, está em `amostra_temperatura.csv` e é a referência definitiva da seleção.

## Uso de IA

A IA Claude Opus 5.5  foi usada para revisar erros de digitação na tabela (identificadores e numeração das anotações), sem alterar categorias ou escrita qualquer diretamente.

## Verificações

Serão registradas ao final das 100 descrições.

## Decisões de revisão

Nenhuma até o momento.

## Pendências

| Anotação | Trecho | Dúvida |
| --- | --- | --- |
| `A0A261GRE4:comments[6].temperatureDependence.texts[0]:a02` | Maintains 60-50% of activity between 40 and 65 degrees Celsius and retains 30% of activity at 72 degrees Celsius | Não menciona incubação nem tempo; atividade nessas temperaturas ou estabilidade? |
| `A1A3T0:comments[4].temperatureDependence.texts[0]:a02` | Retains 60% of its activity between 20 and 45 degrees Celsius | Não menciona incubação nem tempo; atividade nessas temperaturas ou estabilidade? |