# Corpus de descrições de proteínas

## O que foi feito

O presente trabalho reuniu textos do UniProt (Swiss-Prot) que descrevem como a atividade ou a estabilidade de proteínas depende do pH e da temperatura, organizados em JSON Lines (um registro JSON por linha) e em CSV. O objetivo desta etapa foi coletar, organizar, conferir e descrever esses textos, sem treinar modelos.

A coleta usou a consulta `reviewed:true AND cc_bpcp:*` na API do UniProt (`https://rest.uniprot.org/uniprotkb/search`), em formato JSON, com páginas de 50 registros ordenados pelo identificador. Todas as 253 páginas vieram da versão 2026_03 do UniProt, de 02/09/2026; o `coletar.py` interrompe a coleta se essa versão mudar, para não misturar versões. A coleta começou em 2026-10-28, às 10:04 (UTC), e terminou quando não havia mais uma “próxima página”. Cada resposta foi salva sem edição em `originais/`, junto com o `coleta.json`, que registra a consulta, as datas, a versão e quantos registros vieram em cada página.

A amostra de 100 descrições da primeira entrega (59 de pH e 41 de temperatura, de 63 proteínas, sem ocorrências) foi mantida em `corpus_amostra.csv` e `corpus_amostra.jsonl` como registro do desenvolvimento.

## Como uma descrição vira uma linha

Os textos ficam nos comentários de propriedades biofísicas e químicas de cada registro, em `phDependence.texts` e `temperatureDependence.texts`. Cada elemento dessas listas vira uma linha do corpus, e a categoria (`ph_dependence` ou `temperature_dependence`) vem do campo de origem, sem reclassificação. Um texto com várias frases continua sendo uma linha só, e dois elementos no mesmo campo viram duas linhas. O registro A0A023I7E1, por exemplo, gera duas linhas: “Optimum pH is 5.5.” e “Optimum temperature is 50 degrees Celsius.”

Cada linha guarda o texto original sem alteração, uma cópia com espaços padronizados, a sequência, o organismo, a versão do registro, as evidências do próprio elemento e a posição exata de onde o texto foi retirado (`source_path`, como `comments[3].phDependence.texts[0]`). O identificador da descrição junta o identificador da proteína e essa posição.

A amostra foi formada pelas primeiras 100 descrições em ordem de `description_id`, com a regra de trocar a última linha por uma descrição da categoria ausente caso uma das categorias não aparecesse. Por isso, ela não é aleatória.

## Resultados principais

Os números abaixo descrevem o corpus completo e vêm de `resultados_txt/resumo.txt` e `resultados_json/extracao.json`.

| | |
| --- | --- |
| Registros do UniProt processados | 12612 |
| Registros sem texto de pH nem de temperatura | 6363 |
| Descrições no corpus | 8987 |
| Proteínas distintas | 6249 |
| Organismos distintos | 1704 |
| Descrições de pH | 5703 |
| Descrições de temperatura | 3284 |
| Proteínas com as duas categorias | 2725 |
| Comprimento mediano dos textos (caracteres) | 42 |
| Descrições sem evidência no próprio elemento | 659 |
| Textos distintos de pH | 2305 |
| Textos distintos de temperatura | 1633 |

O arquivo `resultados_graficos/graficos.png` mostra a quantidade de descrições por categoria e a distribuição do comprimento dos textos, ambos referentes ao corpus completo.

## Repetições

Os três textos mais frequentes tratam do pH ótimo: “Optimum pH is 7.5.” (316 descrições em 315 proteínas), “Optimum pH is 8.0.” (237 descrições em 237 proteínas) e “Optimum pH is 7.0.” (224 descrições em 224 proteínas). Textos iguais em proteínas diferentes permanecem no corpus, como prevê o critério de inclusão; uma frase repetida não indica erro.

No primeiro caso, a diferença entre descrições e proteínas ocorre porque uma proteína apresenta a mesma frase em dois elementos distintos, que viram duas linhas. Não se trata de erro de processamento, pois todos os identificadores de descrição são únicos e nenhum registro foi contado em mais de uma página.

## Verificações e conferência manual

O `verificar.py` conferiu o corpus e a amostra inteiros: identificadores únicos, campos obrigatórios preenchidos, cada descrição localizada no arquivo de origem, texto original, categoria, sequência, organismo, versão do registro e evidências iguais à origem, texto padronizado de acordo com a regra e CSV idêntico ao JSONL. Também confirmou que a amostra está contida no corpus e segue a regra de seleção, que extrair de novo os arquivos de `originais/` reproduz o corpus e que nenhum registro apareceu em mais de uma página. Todas as verificações tiveram resultado ok, registrado em `resultados_txt/verificacao.txt`; o programa encerra com erro se alguma falhar.

O total de registros recebidos nas páginas (12612) é igual ao total informado pela busca (12612).

A conferência manual foi feita em duas rodadas de 20 descrições, uma na amostra e outra no corpus completo, cada uma com 10 de pH e 10 de temperatura, sorteadas pelo `sortear.py` com semente 42. Em cada caso, identificador, categoria, texto, sequência e evidências foram comparados com o registro salvo em `originais/`. Nas duas rodadas, as 20 descrições foram consideradas corretas, sem problemas encontrados e sem correções. O registro da rodada do corpus está em `resultados_csv/conferencia.csv`; o da rodada da amostra não foi preservado.

## Exclusões e ocorrências

Ficaram de fora 6363 registros sem texto em nenhum dos dois campos, conforme os critérios de inclusão; eles estão contados em `registros_sem_ph_nem_temperatura`, no `extracao.json`. Nenhuma descrição foi separada por problemas: o `ocorrencias.jsonl` está vazio (`total_ocorrencias` = 0).

## Arquivos originais

Uma versão anterior do `organiza_json.py` reescrevia os arquivos de `originais/` com quebras de linha e recuo, mas não alterava o conteúdo: cada resposta continua em `originais/` com o conteúdo sem edição.

## Limitações e pontos de atenção

O corpus não é uma tabela de medidas: os textos não foram convertidos em valores numéricos padronizados, e o corpus não está dividido em treino e teste. A sequência guardada é a do registro, mas o texto pode se referir a uma variante, a um domínio ou a outra forma da proteína. A ausência de anotação não significa ausência da propriedade, porque uma proteína sem descrição de pH pode apenas não ter sido estudada nesse aspecto. Um registro revisado também não significa que toda afirmação foi demonstrada experimentalmente; por isso, as evidências da fonte foram preservadas, e o corpus não é tratado como um conjunto de dados experimentais. Por fim, o número de registros retornado pela busca não é o número de descrições do corpus.