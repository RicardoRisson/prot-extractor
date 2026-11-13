import csv
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "anotacao_temperatura"
AMOSTRA = PASTA / "amostra_temperatura.csv"
ANOTACOES = PASTA / "anotacoes_temperatura.csv"
SAIDA = PASTA / "resumo_anotacao.csv"
CATEGORIAS = ["temperatura_otima", "atividade_em_temperatura", "estabilidade_termica",
              "condicao_experimental", "outra_informacao", "indefinida"]
STATUS = ["anotado", "pendente", "revisado"]
DECIDIDOS = {"anotado", "revisado"}


def ler(caminho):
    if not caminho.exists():
        raise SystemExit(f"{PASTA.name}/{caminho.name} não encontrado.")
    with open(caminho, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    amostra, anotacoes = ler(AMOSTRA), ler(ANOTACOES)
    textos = Counter(l["text_normalized"] for l in amostra)
    decididas = [a for a in anotacoes if a["status"] in DECIDIDOS]
    pendentes = [a for a in anotacoes if a["status"] == "pendente"]
    categorias_da_descricao = defaultdict(set)
    for a in decididas:
        categorias_da_descricao[a["description_id"]].add(a["tipo_informacao"])
    por_categoria = Counter(a["tipo_informacao"] for a in decididas)
    descricoes_por_categoria = Counter(c for cs in categorias_da_descricao.values() for c in cs)
    provisorias = Counter(a["tipo_informacao"] for a in pendentes)
    por_status = Counter(a["status"] for a in anotacoes)

    linhas = [("descricoes_selecionadas", "total", len(amostra)),
              ("proteinas_distintas", "total", len({l["accession"] for l in amostra})),
              ("textos_normalizados_diferentes", "total", len(textos)),
              ("descricoes_com_texto_repetido", "total", sum(n for n in textos.values() if n > 1)),
              ("anotacoes", "total", len(anotacoes))]
    linhas += [("anotacoes_por_categoria", c, por_categoria[c]) for c in CATEGORIAS]
    linhas += [("descricoes_por_categoria", c, descricoes_por_categoria[c]) for c in CATEGORIAS]
    linhas.append(("descricoes_com_mais_de_uma_categoria", "total",
                   sum(len(cs) > 1 for cs in categorias_da_descricao.values())))
    linhas += [("anotacoes_por_status", s, por_status[s]) for s in STATUS]
    linhas.append(("descricoes_com_pendencia", "total", len({a["description_id"] for a in pendentes})))
    linhas += [("pendentes_por_categoria_provisoria", c, provisorias[c]) for c in CATEGORIAS]

    with open(SAIDA, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["medida", "categoria_ou_status", "quantidade"])
        w.writerows(linhas)
    for medida, chave, n in linhas:
        print(f"{medida:<38} {chave:<26} {n}")
    print(f"Gravado em {PASTA.name}/{SAIDA.name}. Categorias e descrições por categoria contam só "
          "anotações anotado e revisado; as pendentes aparecem à parte.")


if __name__ == "__main__":
    main()