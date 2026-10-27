import csv
import json
import random
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RESULTADOS = RAIZ / "resultados_json"
CONFERENCIA = RAIZ / "resultados_csv" / "conferencia.csv"
SEMENTE = 42
POR_CATEGORIA = 10
CATEGORIAS = ["ph_dependence", "temperature_dependence"]
ENTREGAS = {"amostra": "corpus_amostra.jsonl", "corpus": "corpus.jsonl"}
COLUNAS = ["description_id", "property_type", "source_file", "source_path", "entrega", "arquivo_sorteado",
           "semente", "resultado", "problemas", "correcao"]


def perguntar():
    while True:
        resposta = input("Conferência de qual entrega? (amostra ou corpus): ").strip().lower()
        if resposta in ENTREGAS:
            return resposta
        print("Digite amostra ou corpus.")


def main():
    entrega = perguntar()
    origem = RESULTADOS / ENTREGAS[entrega]
    if not origem.exists():
        raise SystemExit(f"{RESULTADOS.name}/{origem.name} não encontrado. Rode antes o coletar.py.")

    existentes = []
    if CONFERENCIA.exists():
        with open(CONFERENCIA, newline="", encoding="utf-8") as f:
            existentes = list(csv.DictReader(f))
        if any(l["entrega"] == entrega for l in existentes):
            raise SystemExit(f"{CONFERENCIA.name} já tem a conferência da entrega '{entrega}'. "
                             "Nada foi alterado, para não apagar os resultados já preenchidos.")

    with open(origem, encoding="utf-8") as f:
        linhas = [json.loads(l) for l in f if l.strip()]
    sorteio = random.Random(SEMENTE)
    novas = []
    for tipo in CATEGORIAS:
        grupo = [l for l in linhas if l["property_type"] == tipo]
        escolhidas = sorted(sorteio.sample(grupo, min(POR_CATEGORIA, len(grupo))), key=lambda l: l["description_id"])
        if len(grupo) < POR_CATEGORIA:
            print(f"Atenção: só há {len(grupo)} descrições de {tipo}; todas foram incluídas.")
        novas += [{"description_id": l["description_id"], "property_type": tipo, "source_file": l["source_file"],
                   "source_path": l["source_path"], "entrega": entrega, "arquivo_sorteado": f"{RESULTADOS.name}/{origem.name}",
                   "semente": SEMENTE, "resultado": "", "problemas": "", "correcao": ""} for l in escolhidas]

    CONFERENCIA.parent.mkdir(exist_ok=True)
    with open(CONFERENCIA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUNAS)
        w.writeheader()
        w.writerows(existentes + novas)

    for l in novas:
        print(f"{l['property_type']:<24} {l['description_id']}")
    print(f"{len(novas)} descrições sorteadas com semente {SEMENTE} e gravadas em "
          f"{CONFERENCIA.parent.name}/{CONFERENCIA.name}. Preencha a coluna resultado com confirmado ou errado.")


if __name__ == "__main__":
    main()