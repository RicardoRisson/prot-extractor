import csv
import json
from collections import defaultdict
from statistics import median

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from coletar import RAIZ, REGISTRO, RESULTADOS

SAIDA_TXT = RAIZ / "resultados_txt"
SAIDA_CSV = RAIZ / "resultados_csv"
SAIDA_GRAFICOS = RAIZ / "resultados_graficos"
CATEGORIAS = {"ph_dependence": "pH", "temperature_dependence": "temperatura"}
VERSOES = [("corpus", "corpus.jsonl"), ("amostra", "corpus_amostra.jsonl")]


def ler_jsonl(caminho):
    with open(caminho, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def indicadores(linhas):
    categorias_por_proteina, grupos = defaultdict(set), defaultdict(list)
    for l in linhas:
        categorias_por_proteina[l["accession"]].add(l["property_type"])
        grupos[(l["property_type"], l["text_normalized"])].append(l["accession"])
    mediana = median(len(l["text_original"]) for l in linhas) if linhas else 0

    itens = [("descrições", len(linhas)),
             ("proteínas distintas", len(categorias_por_proteina)),
             ("organismos distintos", len({l["organism"] for l in linhas if l["organism"]}))]
    itens += [(f"descrições de {nome}", sum(l["property_type"] == tipo for l in linhas))
              for tipo, nome in CATEGORIAS.items()]
    itens += [("proteínas nas duas categorias",
               sum(len(c) == len(CATEGORIAS) for c in categorias_por_proteina.values())),
              ("comprimento mediano dos textos (caracteres)", int(mediana) if mediana == int(mediana) else mediana),
              ("descrições sem evidência", sum(not l["evidences"] for l in linhas))]
    itens += [(f"textos diferentes de {nome}",
               len({l["text_normalized"] for l in linhas if l["property_type"] == tipo}))
              for tipo, nome in CATEGORIAS.items()]

    mais_repetidos = sorted(grupos.items(), key=lambda g: (-len(g[1]), g[0]))[:10]
    repetidos = [f"{CATEGORIAS[tipo]} | descrições: {len(acessos)} | proteínas: {len(set(acessos))} | {texto}"
                 for (tipo, texto), acessos in mais_repetidos]
    return itens, repetidos


def graficos(linhas, legenda):
    fig, (eixo_barras, eixo_hist) = plt.subplots(1, 2, figsize=(11, 4.5))
    barras = eixo_barras.bar(list(CATEGORIAS.values()),
                             [sum(l["property_type"] == tipo for l in linhas) for tipo in CATEGORIAS])
    eixo_barras.bar_label(barras)
    eixo_barras.set(title="Descrições por categoria", ylabel="descrições")
    eixo_hist.hist([len(l["text_original"]) for l in linhas], bins=30)
    eixo_hist.set(title="Comprimento dos textos", xlabel="caracteres", ylabel="descrições")
    fig.suptitle(legenda)
    SAIDA_GRAFICOS.mkdir(exist_ok=True)
    fig.savefig(SAIDA_GRAFICOS / "graficos.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    caminho_extracao = RESULTADOS / "extracao.json"
    for caminho in (REGISTRO, caminho_extracao):
        if not caminho.exists():
            raise SystemExit(f"{caminho.parent.name}/{caminho.name} não encontrado. Rode antes o coletar.py.")
    coleta = json.loads(REGISTRO.read_text(encoding="utf-8"))
    extracao = json.loads(caminho_extracao.read_text(encoding="utf-8"))
    registros = sum(p["registros"] for p in coleta["paginas"])
    if extracao.get("registros_processados") != registros:
        raise SystemExit("resultados_json/extracao.json está desatualizado em relação a originais/coleta.json. "
                         "Rode de novo o coletar.py e depois o resumo.py.")

    geral = [("versão do UniProt", coleta["versao_uniprot"]),
             ("coleta completa (todas as páginas baixadas)", "sim" if coleta["proxima"] is None else "não")]
    secoes = [("coleta", "coleta", [("registros UniProt processados", registros),
                                    ("registros sem os campos de interesse",
                                     extracao["registros_sem_ph_nem_temperatura"])], [])]
    for titulo, arquivo in VERSOES:
        if (RESULTADOS / arquivo).exists():
            linhas = ler_jsonl(RESULTADOS / arquivo)
            secoes.append((titulo, f"{titulo} ({RESULTADOS.name}/{arquivo})", *indicadores(linhas)))
            if titulo == "corpus" and linhas:
                situacao = "coleta completa" if coleta["proxima"] is None else "coleta parcial"
                graficos(linhas, f"Corpus ({situacao}): {len(linhas)} descrições, UniProt {coleta['versao_uniprot']}")

    texto = ["RESUMO DO CORPUS"] + [f"{r}: {v}" for r, v in geral] + [""]
    for _, cabecalho, itens, repetidos in secoes:
        texto += [f"== {cabecalho} =="] + [f"{r}: {v}" for r, v in itens] + [""]
        if repetidos:
            texto += ["dez textos mais repetidos:"] + [f"{i}. {r}" for i, r in enumerate(repetidos, 1)] + [""]
    SAIDA_TXT.mkdir(exist_ok=True)
    (SAIDA_TXT / "resumo.txt").write_text("\n".join(texto), encoding="utf-8")

    SAIDA_CSV.mkdir(exist_ok=True)
    with open(SAIDA_CSV / "resumo.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["versao", "indicador", "valor"])
        w.writerows(("geral", r, v) for r, v in geral)
        for versao, _, itens, repetidos in secoes:
            w.writerows((versao, r, v) for r, v in itens)
            w.writerows((versao, f"texto repetido {i}", r) for i, r in enumerate(repetidos, 1))

    print("\n".join(texto))
    print(f"Gravados {SAIDA_TXT.name}/resumo.txt, {SAIDA_CSV.name}/resumo.csv e {SAIDA_GRAFICOS.name}/graficos.png")


if __name__ == "__main__":
    main()