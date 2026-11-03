# Guia de trabalho: anotação de descrições de temperatura

**Etapa 2 — versão 1.0, de 29/10/2026**

## O que vamos construir

Vamos acrescentar uma camada de anotação ao corpus reunido na primeira etapa. Para cada descrição selecionada, identificaremos **que tipo de informação ela apresenta sobre temperatura** e copiaremos o trecho que sustenta essa classificação.

Uma descrição pode informar a temperatura em que uma enzima apresenta maior atividade, relatar perda de atividade após aquecimento ou apenas mencionar a temperatura de um ensaio. Essas informações precisam ser distinguidas antes que os textos possam ser usados para construir tabelas de propriedades ou avaliar métodos automáticos.

O produto desta etapa será um **primeiro conjunto de 100 descrições de temperatura anotadas**, acompanhado das regras utilizadas, das verificações e dos casos que precisam de revisão. As anotações farão parte dos dados do projeto e poderão ser ampliadas para uma avaliação científica posterior.

Trabalharemos com dois momentos de entrega:

- **Entrega intermediária:** as primeiras 20 descrições anotadas, pertencentes ao conjunto de 100, com as dúvidas identificadas.
- **Entrega desta etapa:** as 100 descrições examinadas, a tabela de anotações, o resumo e a documentação atualizada. Os casos ainda não resolvidos devem permanecer identificados.

O corpus da primeira etapa continuará intacto. As novas anotações ficarão em arquivos separados. Nesta etapa, o trabalho é produzir e conferir essas anotações; o treinamento e a comparação de modelos serão definidos depois.

## 1. Escolha a versão do corpus que será anotada

Use o **corpus completo da primeira etapa**, obtido a partir de uma única versão do UniProt e conferido conforme o guia anterior. O arquivo com as primeiras 100 descrições de pH e temperatura não será a base deste sorteio.

Registre no `README.md` desta etapa:

- O caminho do arquivo usado como fonte e sua data ou identificação de versão no repositório.
- A versão do UniProt e a quantidade total de descrições do corpus.
- O nome de quem fará a anotação e a versão deste guia.

Os arquivos originais e os identificadores da primeira etapa continuam sendo a referência. Para interpretar um caso, use o `text_original` salvo. A página atual do UniProt pode ter mudado desde a coleta.

Anotaremos **o que a descrição afirma**. Não será necessário procurar todos os artigos citados, refazer a curadoria do UniProt ou confirmar experimentalmente as afirmações. As evidências bibliográficas da fonte permanecem preservadas no corpus.

**Ao concluir este passo:** a versão que originará as anotações estará identificada e poderá ser recuperada.

## 2. Selecione as 100 descrições de temperatura

Faça a seleção desta forma:

1. Separe as linhas em que `property_type` seja `temperature_dependence`.
2. Ordene essas linhas por `description_id`.
3. Sorteie **100 descrições sem reposição**, usando a **semente 42**. Sem reposição significa que um mesmo identificador não pode ser sorteado duas vezes.
4. Guarde a lista sorteada e ordene-a novamente por `description_id` para trabalhar sempre na mesma sequência.

Se houver menos de 100 descrições elegíveis, use todas e registre a quantidade. A semente ajuda a repetir o sorteio, mas a lista de identificadores selecionados será a referência definitiva. Registre também o programa utilizado e sua versão.

Não escolha os textos pelo comprimento, pela facilidade ou por conterem uma palavra específica. Não force quantidades iguais das futuras categorias. Se uma categoria não aparecer, registre essa ausência.

Textos iguais associados a proteínas diferentes podem ser sorteados. Mantenha-os e informe a repetição no resumo. Uma proteína também pode contribuir com mais de uma descrição. Estamos selecionando descrições, não necessariamente 100 proteínas diferentes.

Salve a seleção em `amostra_temperatura.csv`, mantendo **as 11 colunas da primeira etapa**. O formato **CSV (Comma-Separated Values, valores separados por vírgulas)** permite abrir a tabela em um editor de planilhas. Preserve o conteúdo das células, inclusive textos, sequências e evidências.

Não refaça o sorteio durante a anotação. Se encontrar um problema, mantenha o identificador na seleção e registre o caso para revisão.

**Ao concluir este passo:** você terá uma seleção fixa, rastreável e reproduzível para anotar.

## 3. Use as categorias de informação abaixo

As categorias são convenções deste projeto. Elas descrevem o **conteúdo da afirmação**, enquanto `temperature_dependence` continua indicando o campo de origem no UniProt.

Os exemplos deste guia são **didáticos e fictícios**. Servem para mostrar o preenchimento; não devem ser acrescentados ao corpus.

| Categoria a usar no arquivo | Quando usar | Exemplo didático |
| --- | --- | --- |
| `temperatura_otima` | O texto informa uma temperatura ou intervalo como ótimo, ou afirma que ali ocorre um máximo de atividade. | “Optimum temperature is 50 degrees Celsius.” |
| `atividade_em_temperatura` | O texto descreve atividade, ausência de atividade ou sua variação com a temperatura, sem afirmar um ótimo e sem relatar um efeito de exposição térmica sobre a estabilidade. | “Relative activity is 40% at 20 degrees Celsius.” |
| `estabilidade_termica` | O texto descreve estabilidade, termolabilidade, desnaturação térmica ou manutenção/perda de atividade após exposição a uma temperatura. Inclui observações qualitativas. | “Retains 80% activity after incubation for 30 minutes at 60 degrees Celsius.” |
| `condicao_experimental` | O texto informa uma temperatura utilizada em um procedimento, sem apresentar ali um resultado de atividade ótima ou estabilidade. | “Activity was measured at 25 degrees Celsius.” |
| `outra_informacao` | A informação é compreensível, mas não corresponde às quatro categorias acima. Explique brevemente o caso em `observacao`. | “Optimum growth temperature of the organism is 37 degrees Celsius.” |
| `indefinida` | Não é possível escolher uma categoria com segurança a partir do texto disponível. Use junto com o status `pendente`. | “Temperature: 50 degrees Celsius.” |

`outra_informacao` não significa erro da fonte. Por exemplo, a temperatura de crescimento do organismo não deve ser convertida em temperatura ótima de atividade da proteína.

### Distinções que orientam a anotação

- **Temperatura ótima:** refere-se ao máximo de atividade informado nas condições avaliadas. Uma proteína estar ativa a 50 °C não demonstra que essa seja sua temperatura ótima.
- **Atividade em determinada temperatura:** descreve quanto a proteína funciona naquela condição. Isso, sozinho, não informa por quanto tempo ela resiste ao aquecimento.
- **Estabilidade térmica:** pode ser descrita por manutenção de função após exposição, perda de atividade ao longo do tempo ou alterações da estrutura. Essas observações pertencem a uma categoria ampla nesta etapa, mas não são medidas equivalentes.
- **Condição experimental:** informa como o procedimento foi realizado. Armazenar uma proteína a 4 °C não demonstra, por si só, que ela permaneceu estável.

Se aparecer **Tm (temperatura de transição térmica, frequentemente chamada de temperatura de melting)**, preserve o termo e o contexto na categoria `estabilidade_termica`. Não transforme automaticamente uma frase como “stable up to 60 degrees Celsius” em uma medida de Tm. O tempo de exposição e o método de avaliação podem mudar o significado do resultado.

Palavras isoladas ajudam a localizar informações, mas a decisão depende da afirmação completa. Não classifique apenas porque encontrou “optimum”, “stable” ou um número seguido de uma unidade.

**Ao concluir este passo:** use esses nomes de categoria na tabela, sem criar categorias adicionais por conta própria. Casos não previstos podem ser registrados e discutidos sem interromper os demais.

## 4. Defina o que será uma anotação

**Cada linha da tabela de anotações corresponderá a uma afirmação textual de um dos tipos definidos no passo 3.** Ela estará ligada à descrição original pelo `description_id`.

Uma descrição pode gerar várias anotações. Por exemplo:

> Optimum temperature is 50 degrees Celsius. Retains 80% activity after incubation for 30 minutes at 60 degrees Celsius.

Esse texto gera uma anotação de `temperatura_otima` e uma de `estabilidade_termica`. A descrição permanece uma única linha no corpus original.

O foco são as afirmações relacionadas à temperatura. Não abra anotações separadas apenas para nomes de organismos, citações ou condições que acompanham um resultado. Use `outra_informacao` para afirmações sobre temperatura fora das categorias principais ou quando a descrição inteira só trouxer outro assunto.

Para separar as informações:

- Se duas frases apresentarem afirmações diferentes, anote cada uma separadamente, mesmo que tenham a mesma categoria.
- Se uma frase misturar ótimo e estabilidade, separe as duas afirmações quando for possível identificá-las no texto.
- Um intervalo ou uma comparação dentro da mesma afirmação pode ficar em uma única anotação. Não crie uma linha para cada número.
- Preserve comparações entre proteína original e variante, ou entre condições diferentes, com contexto suficiente para saber a quem cada resultado se refere.
- Se houver apenas informação fora das categorias principais, registre `outra_informacao`. Se o sentido não estiver claro, registre `indefinida` e a dúvida. Nenhuma descrição sorteada deve desaparecer da entrega.

### Não duplique as condições que fazem parte de um resultado

Na frase sobre retenção de 80% da atividade após 30 minutos a 60 °C, o tempo e a temperatura fazem parte da observação de estabilidade. Mantenha tudo na mesma anotação. Não acrescente outra linha de `condicao_experimental` só porque a frase contém essas condições.

Use `condicao_experimental` quando existir uma afirmação própria sobre o procedimento, como “Activity was measured at 25 degrees Celsius.”

**Ao concluir este passo:** cada informação terá sua própria linha, com ligação explícita à descrição de origem.

## 5. Copie o trecho que sustenta cada anotação

O `trecho_evidencia` será uma cópia literal de uma parte contínua do `text_original`. Se a descrição inteira for necessária para entender a afirmação, copie o texto inteiro.

Use o trecho mais curto que ainda permita interpretar corretamente a informação. Preserve:

- O que está sendo afirmado e a quem se refere.
- Números, intervalos, unidades e expressões de comparação.
- Negações e qualificadores, como “not”, “approximately”, “above” e “below”.
- Tempo de exposição, **pH (potencial hidrogeniônico)**, substrato ou outras condições presentes na afirmação.

Não traduza o trecho, não substitua “degrees Celsius” por “°C” e não junte partes distantes como se fossem um trecho contínuo. Anotações diferentes podem compartilhar parte do texto quando isso for necessário para preservar o contexto.

Se o mesmo trecho aparecer duas vezes na descrição, amplie a seleção para distinguir a ocorrência. Se isso não resolver, indique em `observacao` qual ocorrência está sendo anotada.

O nome `trecho_evidencia` se refere à **evidência textual da classificação**. Ele não substitui a coluna `evidences` do corpus, que contém as evidências fornecidas pelo UniProt. Não redistribua automaticamente as referências bibliográficas entre as novas anotações.

Não preencha condições ausentes com conhecimento externo. Nesta etapa, também não transforme os números em uma tabela de medidas padronizadas: os valores permanecem nos trechos, com seu contexto.

**Ao concluir este passo:** outra pessoa poderá ler cada anotação, localizar o trecho na descrição e entender por que aquela categoria foi escolhida.

## 6. Organize a tabela de anotações

Use o arquivo `anotacoes_temperatura.csv`, com estas colunas:

| Coluna | O que guardar |
| --- | --- |
| `annotation_id` | Identificador único da anotação. Use o `description_id` seguido de `:a01`, `:a02` e assim por diante, na ordem em que as informações aparecem no texto. |
| `description_id` | Identificador da descrição, copiado da amostra sem alterações. |
| `tipo_informacao` | Uma das seis categorias do passo 3. Use uma categoria por linha. |
| `trecho_evidencia` | Trecho literal e contínuo do `text_original` que sustenta a anotação. |
| `status` | `anotado`, `pendente` ou `revisado`, conforme as regras abaixo. |
| `observacao` | Justificativa de uma dúvida, explicação de `outra_informacao` ou registro de uma decisão de revisão. Pode ficar vazia nos casos claros. |

Use os status assim:

- **`anotado`:** você leu o texto e atribuiu uma categoria com base neste guia.
- **`pendente`:** existe uma dúvida que pode alterar a categoria ou a escolha do trecho. Descreva a dúvida em `observacao`. Pode ser usado com uma categoria provisória ou com `indefinida`.
- **`revisado`:** a anotação foi conferida por outra pessoa ou discutida comigo e a decisão foi registrada. Sua própria releitura não transforma o status em `revisado`.

Uma anotação marcada como `indefinida` permanece `pendente` até que uma decisão seja tomada. Não use `outra_informacao` apenas para esconder uma dúvida.

### Exemplo de preenchimento

Considere estas três descrições fictícias:

| Identificador abreviado | Texto original |
| --- | --- |
| D1 | Optimum temperature is 50 degrees Celsius. Retains 80% activity after incubation for 30 minutes at 60 degrees Celsius. |
| D2 | Activity was measured at 25 degrees Celsius. |
| D3 | Temperature: 50 degrees Celsius. |

A tabela de anotações ficaria assim:

| annotation_id | description_id | tipo_informacao | trecho_evidencia | status | observacao |
| --- | --- | --- | --- | --- | --- |
| D1:a01 | D1 | temperatura_otima | Optimum temperature is 50 degrees Celsius. | anotado | |
| D1:a02 | D1 | estabilidade_termica | Retains 80% activity after incubation for 30 minutes at 60 degrees Celsius. | anotado | |
| D2:a01 | D2 | condicao_experimental | Activity was measured at 25 degrees Celsius. | anotado | |
| D3:a01 | D3 | indefinida | Temperature: 50 degrees Celsius. | pendente | O texto não informa o significado da temperatura. |

Nos arquivos reais, use os identificadores completos da amostra. D1, D2 e D3 são apenas abreviações deste exemplo. Mantenha uma célula vazia quando não houver observação; não é necessário preencher com “n/a”.

**Ao concluir este passo:** a tabela estará pronta para receber as anotações sem modificar as 11 colunas do corpus.

## 7. Anote o primeiro lote e registre os casos difíceis

Comece pelas primeiras **20 descrições da amostra já ordenada**. Elas fazem parte das 100 e continuarão no conjunto final.

Para cada descrição:

1. Leia o texto completo antes de escolher uma categoria.
2. Identifique todas as afirmações relevantes e separe-as conforme o passo 4.
3. Copie os trechos e preencha as linhas correspondentes.
4. Releia o conjunto para conferir se alguma afirmação ficou sem anotação.
5. Marque as dúvidas como `pendente` e registre exatamente o que precisa ser decidido.

Use estas regras nos casos frequentes:

| Caso encontrado | Como tratar |
| --- | --- |
| “Thermostable.” ou “Thermolabile.” | Use `estabilidade_termica`. A ausência de número não impede a anotação. |
| Há atividade em uma temperatura, sem menção a um ótimo. | Use `atividade_em_temperatura`; não conclua que ali está o máximo de atividade. |
| Há perda ou retenção de atividade depois de incubação ou aquecimento. | Use `estabilidade_termica` e mantenha tempo, temperatura e resultado no trecho. |
| O texto diz “retains activity”, mas não esclarece se houve exposição térmica anterior. | Se a descrição inteira não resolver o sentido, registre a dúvida como `pendente`. Não suponha um procedimento. |
| A proteína foi armazenada a determinada temperatura. | Use `condicao_experimental` se o texto só relatar o armazenamento. Se informar estabilidade durante o armazenamento, use `estabilidade_termica`. |
| O texto diz que não foi determinado um ótimo. | Registre `outra_informacao`, explicando a ausência de um ótimo determinado. Não anote como se houvesse um resultado de temperatura ótima. |
| Há resultados para uma variante, domínio ou complexo. | Preserve essa identificação no trecho. Não atribua o resultado automaticamente à sequência completa do registro. |
| Há uma observação somente sobre pH ou sobre crescimento do organismo. | Use `outra_informacao` e explique o motivo. Não exclua a descrição sorteada. |

Envie a tabela com esse primeiro lote e as pendências identificadas. Esse envio serve para ajustar o procedimento enquanto o conjunto ainda é pequeno. Você pode continuar os casos claros das demais descrições enquanto discutimos as dúvidas.

Quando uma regra mudar, atualize a versão do guia e confira as anotações anteriores que possam ser afetadas. Não é necessário recomeçar todo o trabalho. Preserve a versão anterior da tabela no histórico do repositório e registre a decisão no `README.md`.

**Ao concluir este passo:** as primeiras 20 descrições estarão incorporadas à tabela, e as decisões necessárias estarão localizadas por identificador.

## 8. Complete as 100 descrições e confira a entrega

Continue a anotação das descrições restantes usando as mesmas regras. Não substitua os casos difíceis por outros mais fáceis e não preencha uma categoria apenas para eliminar uma pendência.

Ao terminar, confira:

- A amostra mantém as descrições sorteadas e os textos originais.
- Todos os `annotation_id` são únicos e apontam para um `description_id` existente na amostra.
- Cada descrição da amostra tem pelo menos uma linha na tabela, inclusive os casos pendentes ou fora das categorias principais.
- As categorias e os status pertencem às listas definidas neste guia.
- Cada `trecho_evidencia` pode ser localizado literalmente no `text_original` correspondente.
- Não há linhas repetidas por engano. Repetições legítimas no texto precisam estar identificadas.
- Todos os casos `pendente` e `outra_informacao` têm uma observação explicativa.
- Os casos com status `revisado` têm uma revisão registrada, com responsável e data no `README.md` ou no histórico de revisão.

Essas verificações podem ser automatizadas. A presença de um trecho na fonte confirma que ele foi copiado corretamente; não garante que a categoria esteja correta. Faça também uma releitura das 100 descrições, comparando cada texto com todas as suas anotações para procurar informações omitidas e classificações inconsistentes.

Não aplique uma correção em apenas um caso se a mesma decisão afetar outros. Localize os casos semelhantes, confira-os e registre a mudança.

**Ao concluir este passo:** todas as descrições terão sido examinadas, e será possível separar as anotações prontas das decisões ainda pendentes.

## 9. Faça um resumo das anotações

Prepare `resumo_anotacao.csv` com as seguintes contagens:

1. Número de descrições selecionadas, proteínas distintas e textos normalizados diferentes.
2. Número total de anotações produzidas.
3. Número de anotações de cada categoria.
4. Número de descrições distintas que contêm cada categoria.
5. Número de descrições com mais de uma categoria.
6. Número de anotações em cada status e número de descrições com pelo menos uma pendência.

Para os itens 3, 4 e 5, conte as anotações `anotado` e `revisado`. Apresente as classificações provisórias com status `pendente` separadamente, sem tratá-las como decisões finais.

Você pode organizar o resumo nas colunas `medida`, `categoria_ou_status` e `quantidade`. Quando a medida for geral, use `total` na segunda coluna.

O número de anotações pode ser maior que 100, pois uma descrição pode gerar várias linhas. Da mesma forma, a soma das descrições por categoria pode ultrapassar 100, porque as categorias podem coexistir no mesmo texto. Se apresentar porcentagens, informe sempre qual foi o denominador.

Essas contagens descrevem a amostra anotada. Não representam a distribuição das propriedades de todas as proteínas do UniProt nem a frequência dessas propriedades na natureza.

No `README.md`, acrescente um relato curto das principais decisões, das limitações e do que permanece pendente. Nesta etapa, a tabela de resumo é suficiente; não é necessário produzir gráficos adicionais.

**Ao concluir este passo:** as dimensões e o estado de revisão do conjunto estarão claros para quem for utilizá-lo.

## 10. Como deve ficar a entrega final

Mantenha os arquivos desta etapa em uma pasta própria, por exemplo `anotacao_temperatura/`, no mesmo repositório do projeto.

| Material | Conteúdo esperado |
| --- | --- |
| `amostra_temperatura.csv` | As 100 descrições sorteadas, ou todas as disponíveis se forem menos de 100, com as 11 colunas da primeira etapa. |
| `anotacoes_temperatura.csv` | Uma linha por afirmação anotada, com as seis colunas do passo 6. |
| `resumo_anotacao.csv` | Contagens da amostra, das categorias e dos status, conforme o passo 9. |
| `README.md` | Fonte da amostra, procedimento e semente do sorteio, versões, responsáveis, verificações realizadas, decisões de revisão e pendências. |
| `guia_anotacao_temperatura_etapa2.md` | A versão das regras utilizada na anotação, preservando o histórico de eventuais mudanças. |

Se utilizar programas para selecionar a amostra ou conferir a tabela, mantenha-os no repositório com a informação necessária para executá-los. Não é preciso construir uma interface de anotação: uma planilha ou editor de tabelas é suficiente, desde que preserve os textos e os identificadores.

### Quando esta etapa estará concluída?

- A seleção está registrada e pode ser recuperada.
- Todas as descrições selecionadas foram lidas e representadas na tabela.
- As categorias seguem uma versão identificada deste guia.
- Os trechos foram conferidos com os textos originais.
- As dúvidas e as decisões de revisão estão registradas.
- O resumo corresponde à versão entregue dos arquivos.

O resultado será um **conjunto anotado inicial**, reutilizável nas próximas etapas do projeto. Cem descrições não constituem, por si só, um conjunto suficiente para publicação ou uma avaliação definitiva de métodos.

Depois desta entrega, definiremos a ampliação da anotação e uma revisão independente de parte dos dados. Isso permitirá avaliar a consistência das regras antes de preparar os experimentos com modelos. A revisão feita em conjunto não deve ser apresentada como concordância entre anotadores independentes.

Quando houver uma divisão para treinamento e teste, será preciso considerar descrições da mesma proteína e textos repetidos ou muito semelhantes. A organização dessa avaliação ficará para a próxima etapa; por enquanto, preserve essas relações nos dados.

## Dúvidas e ferramentas de apoio

Você pode usar **IA (inteligência artificial)** para estudar conceitos, organizar o trabalho, revisar código e preparar verificações dos arquivos. Para este primeiro conjunto, faça a leitura e a atribuição das categorias antes de consultar sugestões automáticas de classificação. Isso ajuda a construir uma referência humana que não dependa das respostas do método que poderemos avaliar depois.

Não use IA para completar condições ausentes, reescrever os trechos ou criar evidências. Se alguma sugestão automática influenciar uma decisão de anotação, registre essa assistência no `README.md` e identifique os casos envolvidos. Uma sugestão de IA não conta como segunda revisão humana.

Pode me enviar dúvidas por e-mail durante o trabalho. Inclua o `description_id`, o texto e a decisão que precisa ser discutida. Marcaremos reuniões conforme a necessidade; você pode continuar as demais anotações enquanto os casos pendentes são resolvidos.

## Fontes de consulta

- [Manual do UniProt](https://web.expasy.org/docs/userman.html), especialmente a seção *BIOPHYSICOCHEMICAL PROPERTIES*. O campo de dependência de temperatura pode reunir informações de atividade e de estabilidade.
- [Almeida e Marana (2019): *Optimum temperature may be a misleading parameter in enzyme characterization and application*](https://doi.org/10.1371/journal.pone.0212977). Referência para compreender por que a temperatura ótima depende das condições de avaliação.

