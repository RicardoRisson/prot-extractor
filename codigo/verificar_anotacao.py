import csv
import json
import random
import re
from collections import Counter, defaultdict

from converter import celula
from sortear_temperatura import AMOSTRA, CATEGORIA, CORPUS, PASTA, QUANTIDADE, SEMENTE

ANOTACOES = PASTA / "anotacoes_temperatura.csv"
README = PASTA / "README.md"
COLUNAS = ["annotation_id", "description_id", "tipo_informacao", "trecho_evidencia", "status", "observacao"]
CATEGORIAS = {"temperatura_otima", "atividade_em_temperatura", "estabilidade_termica",
              "condicao_experimental", "outra_informacao", "indefinida"}
STATUS = {"anotado", "pendente", "revisado"}


def ler_csv(caminho):
    if not caminho.exists():
        raise SystemExit(f"{caminho.parent.name}/{caminho.name} não encontrado.")
    with open(caminho, newline="", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        return leitor.fieldnames, list(leitor)


def resultado(nome, ids):
    return f"{nome}: ok" if not ids else f"{nome}: falhou em {len(ids)} (ex.: {', '.join(map(str, ids[:3]))})"


def main():
    if not CORPUS.exists():
        raise SystemExit(f"{CORPUS.parent.name}/{CORPUS.name} não encontrado.")
    with open(CORPUS, encoding="utf-8") as f:
        corpus = [json.loads(l) for l in f if l.strip()]
    _, amostra = ler_csv(AMOSTRA)
    colunas, anotacoes = ler_csv(ANOTACOES)
    textos = {l["description_id"]: l["text_original"] for l in amostra}

    elegiveis = sorted((l for l in corpus if l["property_type"] == CATEGORIA), key=lambda l: l["description_id"])
    sorteio = sorted(random.Random(SEMENTE).sample(elegiveis, min(QUANTIDADE, len(elegiveis))),
                     key=lambda l: l["description_id"])
    esperada = [{k: celula(v) for k, v in l.items()} for l in sorteio]

    por_descricao = defaultdict(list)
    for a in anotacoes:
        por_descricao[a["description_id"]].append(a)
    fora_de_ordem = []
    for d, grupo in por_descricao.items():
        grupo = sorted(grupo, key=lambda a: a["annotation_id"])
        numeros = [a["annotation_id"].rsplit(":", 1)[-1] for a in grupo]
        posicoes = [textos.get(d, "").find(a["trecho_evidencia"]) for a in grupo]
        if numeros != [f"a{i:02d}" for i in range(1, len(grupo) + 1)] or posicoes != sorted(posicoes):
            fora_de_ordem.append(d)
    repetidas = Counter((a["description_id"], a["tipo_informacao"], a["trecho_evidencia"])
                        for a in anotacoes if not a["observacao"].strip())
    readme = README.read_text(encoding="utf-8") if README.exists() else ""

    texto = ["VERIFICAÇÃO DAS ANOTAÇÕES",
             f"{len(amostra)} descrições na amostra e {len(anotacoes)} anotações", "",
             f"amostra igual ao sorteio refeito com semente {SEMENTE}: {'ok' if amostra == esperada else 'falhou'}",
             f"colunas da tabela de anotações: {'ok' if colunas == COLUNAS else 'falhou'}",
             resultado("annotation_id únicos", [i for i, n in Counter(a["annotation_id"] for a in anotacoes).items()
                                                if n > 1]),
             resultado("description_id existente na amostra",
                       [a["annotation_id"] for a in anotacoes if a["description_id"] not in textos]),
             resultado("annotation_id igual ao description_id seguido de :aNN",
                       [a["annotation_id"] for a in anotacoes
                        if not re.fullmatch(re.escape(a["description_id"]) + r":a\d{2}", a["annotation_id"])]),
             resultado("numeração em sequência e na ordem do texto", fora_de_ordem),
             resultado("toda descrição da amostra com pelo menos uma anotação",
                       [d for d in textos if d not in por_descricao]),
             resultado("categoria válida", [a["annotation_id"] for a in anotacoes
                                            if a["tipo_informacao"] not in CATEGORIAS]),
             resultado("status válido", [a["annotation_id"] for a in anotacoes if a["status"] not in STATUS]),
             resultado("trecho encontrado literalmente no text_original",
                       [a["annotation_id"] for a in anotacoes if not a["trecho_evidencia"].strip()
                        or a["trecho_evidencia"] not in textos.get(a["description_id"], "")]),
             resultado("sem linhas repetidas por engano", [k[0] for k, n in repetidas.items() if n > 1]),
             resultado("pendente e outra_informacao com observação",
                       [a["annotation_id"] for a in anotacoes if not a["observacao"].strip()
                        and (a["status"] == "pendente" or a["tipo_informacao"] == "outra_informacao")]),
             resultado("indefinida sempre como pendente",
                       [a["annotation_id"] for a in anotacoes
                        if a["tipo_informacao"] == "indefinida" and a["status"] != "pendente"]),
             resultado("revisado registrado no README",
                       [a["annotation_id"] for a in anotacoes
                        if a["status"] == "revisado" and a["description_id"].split(":")[0] not in readme])]

    print("\n".join(texto))
    falhas = [linha for linha in texto if ": falhou" in linha]
    if falhas:
        raise SystemExit(f"{len(falhas)} verificações falharam.")


if __name__ == "__main__":
    main()