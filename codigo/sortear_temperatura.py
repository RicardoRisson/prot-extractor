import csv
import json
import platform
import random
from pathlib import Path

from converter import celula

RAIZ = Path(__file__).resolve().parent.parent
CORPUS = RAIZ / "resultados_json" / "corpus.jsonl"
PASTA = RAIZ / "anotacao_temperatura"
AMOSTRA = PASTA / "amostra_temperatura.csv"
SEMENTE = 42
QUANTIDADE = 100
CATEGORIA = "temperature_dependence"


def main():
    if not CORPUS.exists():
        raise SystemExit(f"{CORPUS.parent.name}/{CORPUS.name} não encontrado. Rode antes o coletar.py.")
    if AMOSTRA.exists():
        raise SystemExit(f"{PASTA.name}/{AMOSTRA.name} já existe. Nada foi alterado, "
                         "porque o sorteio não deve ser refeito durante a anotação.")

    with open(CORPUS, encoding="utf-8") as f:
        linhas = [json.loads(l) for l in f if l.strip()]
    elegiveis = sorted((l for l in linhas if l["property_type"] == CATEGORIA), key=lambda l: l["description_id"])
    if not elegiveis:
        raise SystemExit(f"Nenhuma descrição de {CATEGORIA} no corpus.")
    sorteadas = sorted(random.Random(SEMENTE).sample(elegiveis, min(QUANTIDADE, len(elegiveis))),
                       key=lambda l: l["description_id"])
    if len(elegiveis) < QUANTIDADE:
        print(f"Atenção: só há {len(elegiveis)} descrições de {CATEGORIA}; todas foram incluídas.")

    PASTA.mkdir(exist_ok=True)
    with open(AMOSTRA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sorteadas[0]))
        w.writeheader()
        w.writerows({k: celula(v) for k, v in l.items()} for l in sorteadas)

    for l in sorteadas:
        print(l["description_id"])
    print(f"{len(sorteadas)} de {len(elegiveis)} descrições de {CATEGORIA} sorteadas com semente {SEMENTE} "
          f"(Python {platform.python_version()}) e gravadas em {PASTA.name}/{AMOSTRA.name}.")


if __name__ == "__main__":
    main()