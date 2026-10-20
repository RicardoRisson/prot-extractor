import csv
import json
import sys
from pathlib import Path

ENTRADA = Path("resultados_json")
SAIDA = Path("resultados_csv")
# cabeçalho usado quando o arquivo não tem linhas (ex.: nenhuma ocorrência)
COLUNAS_SE_VAZIO = {"ocorrencias": ["source_file", "indice_registro", "accession",
                                    "source_path", "motivo", "decisao"]}


def celula(v):
    return json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else "" if v is None else str(v)


def converter(origem):
    with open(origem, encoding="utf-8") as f:
        linhas = [json.loads(l) for l in f if l.strip()]
    destino = SAIDA / f"{origem.stem}.csv"
    if not linhas:
        with open(destino, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(COLUNAS_SE_VAZIO.get(origem.stem, []))
        return print(f"{origem.name}: nenhuma linha; {destino} criado só com o cabeçalho")
    colunas = list(dict.fromkeys(k for l in linhas for k in l))
    esperado = [{k: celula(l.get(k)) for k in colunas} for l in linhas]
    with open(destino, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=colunas)
        w.writeheader()
        w.writerows(esperado)
    with open(destino, newline="", encoding="utf-8") as f:
        if list(csv.DictReader(f)) != esperado:
            raise SystemExit(f"{destino} diverge de {origem}")
    print(f"{origem} -> {destino}: {len(linhas)} linhas, conteúdo conferido")


if __name__ == "__main__":
    SAIDA.mkdir(exist_ok=True)
    arquivos = [Path(a) for a in sys.argv[1:]] or sorted(ENTRADA.glob("*.jsonl"))
    if not arquivos:
        print(f"Nenhum .jsonl em {ENTRADA}/. Rode antes: python codigo/coletar.py")
    for arq in arquivos:
        converter(arq) if arq.exists() else print(f"{arq}: não encontrado")