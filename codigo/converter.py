"""Converte os .jsonl do corpus em .csv. Listas (como evidences) viram JSON dentro da célula.
Depois de gravar, relê o CSV e confere se tem as mesmas linhas e o mesmo conteúdo.

Uso: python codigo/json_para_csv.py [arquivo.jsonl ...]
Sem argumentos, converte corpus.jsonl, corpus_amostra.jsonl e ocorrencias.jsonl da pasta atual.
"""
import csv
import json
import sys
from pathlib import Path


def celula(v):
    return json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else "" if v is None else str(v)


def converter(origem):
    with open(origem, encoding="utf-8") as f:
        linhas = [json.loads(l) for l in f if l.strip()]
    destino = origem.with_suffix(".csv")
    if not linhas:
        destino.write_text("", encoding="utf-8")
        return print(f"{origem.name}: vazio, {destino.name} criado sem linhas")
    colunas = list(dict.fromkeys(k for l in linhas for k in l))
    esperado = [{k: celula(l.get(k)) for k in colunas} for l in linhas]
    with open(destino, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=colunas)
        w.writeheader()
        w.writerows(esperado)
    with open(destino, newline="", encoding="utf-8") as f:
        if list(csv.DictReader(f)) != esperado:
            raise SystemExit(f"{destino.name} diverge de {origem.name}")
    print(f"{origem.name} -> {destino.name}: {len(linhas)} linhas, conteúdo conferido")


if __name__ == "__main__":
    for arq in map(Path, sys.argv[1:] or ["corpus.jsonl", "corpus_amostra.jsonl", "ocorrencias.jsonl"]):
        converter(arq) if arq.exists() else print(f"{arq}: não encontrado")