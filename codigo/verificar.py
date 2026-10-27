import csv
import json
import re
from collections import Counter, defaultdict

from coletar import CAMPOS, RAIZ, REGISTRO, RESULTADOS, extrair, selecionar
from converter import SAIDA as PASTA_CSV, celula

SAIDA = RAIZ / "resultados_txt"
VERIFICACOES = ["identificadores únicos", "campos obrigatórios preenchidos", "descrições localizadas na origem",
                "texto original igual à origem", "demais colunas iguais à origem",
                "categoria igual ao campo de origem", "texto padronizado segue a regra"]


def ler(nome):
    caminho = RESULTADOS / f"{nome}.jsonl"
    if not caminho.exists():
        return None
    with open(caminho, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def resolver(registro, caminho):
    valor = registro
    for chave, indice in re.findall(r"(\w+)|\[(\d+)\]", caminho):
        valor = valor[chave] if chave else valor[int(indice)]
    return valor


def resultado(nome, ids):
    return f"{nome}: ok" if not ids else f"{nome}: falhou em {len(ids)} (ex.: {', '.join(map(str, ids[:3]))})"


def conferir_csv(nome, linhas):
    arquivo = PASTA_CSV / f"{nome}.csv"
    if not arquivo.exists():
        return f"CSV igual ao JSONL: {PASTA_CSV.name}/{arquivo.name} não encontrado; rode o converter.py"
    with open(arquivo, newline="", encoding="utf-8") as f:
        tabela = list(csv.DictReader(f))
    if len(tabela) != len(linhas):
        return f"CSV igual ao JSONL: falhou ({len(tabela)} linhas no CSV e {len(linhas)} no JSONL)"
    return resultado("CSV igual ao JSONL", [l.get("description_id") for l, t in zip(linhas, tabela)
                                            if t != {k: celula(v) for k, v in l.items()}])


def verificar(nome, linhas):
    problemas = defaultdict(list)
    problemas["identificadores únicos"] = [i for i, n in Counter(l.get("description_id") for l in linhas).items()
                                           if n > 1]
    por_fonte = defaultdict(list)
    for l in linhas:
        did, texto = l.get("description_id"), l.get("text_original")
        if not (l.get("accession") and l.get("sequence") and l.get("property_type") in CAMPOS.values()
                and isinstance(texto, str) and texto.strip()):
            problemas["campos obrigatórios preenchidos"].append(did)
        elif l.get("text_normalized") != " ".join(texto.split()):
            problemas["texto padronizado segue a regra"].append(did)
        por_fonte[l.get("source_file")].append(l)

    for fonte, grupo in por_fonte.items():
        try:
            registros = {r.get("primaryAccession"): r for r in json.loads((RAIZ / fonte).read_bytes())["results"]}
        except (OSError, TypeError, ValueError, KeyError):
            registros = {}
        for l in grupo:
            did = l.get("description_id")
            try:
                reg = registros[l["accession"]]
                elemento = resolver(reg, l["source_path"])
                campo = l["source_path"].split(".")[1]
                valor = elemento["value"]
            except (KeyError, IndexError, TypeError):
                problemas["descrições localizadas na origem"].append(did)
                continue
            if valor != l["text_original"]:
                problemas["texto original igual à origem"].append(did)
            if CAMPOS.get(campo) != l["property_type"]:
                problemas["categoria igual ao campo de origem"].append(did)
            esperado = {"description_id": f"{l['accession']}:{l['source_path']}",
                        "sequence": (reg.get("sequence") or {}).get("value"),
                        "organism": (reg.get("organism") or {}).get("scientificName"),
                        "entry_version": (reg.get("entryAudit") or {}).get("entryVersion"),
                        "evidences": elemento.get("evidences") or []}
            if any(l.get(k) != v for k, v in esperado.items()):
                problemas["demais colunas iguais à origem"].append(did)

    return [resultado(v, problemas[v]) for v in VERIFICACOES] + [conferir_csv(nome, linhas)]


def main():
    if not REGISTRO.exists():
        raise SystemExit("originais/coleta.json não encontrado. Rode antes o coletar.py.")
    coleta = json.loads(REGISTRO.read_text(encoding="utf-8"))
    corpus, amostra = ler("corpus"), ler("corpus_amostra")
    if corpus is None:
        raise SystemExit("resultados_json/corpus.jsonl não encontrado. Rode antes o coletar.py.")

    texto = ["VERIFICAÇÃO DO CORPUS",
             f"versão do UniProt: {coleta['versao_uniprot']}",
             f"coleta completa (todas as páginas baixadas): {'sim' if coleta['proxima'] is None else 'não'}",
             ""]
    for titulo, nome, linhas in (("corpus", "corpus", corpus), ("amostra", "corpus_amostra", amostra)):
        if linhas is not None:
            texto += [f"== {titulo} ({RESULTADOS.name}/{nome}.jsonl): {len(linhas)} descrições =="]
            texto += verificar(nome, linhas) + [""]

    texto.append("== consistência ==")
    if amostra is not None:
        no_corpus = {l["description_id"]: l for l in corpus}
        texto.append(resultado("amostra contida no corpus",
                               [l.get("description_id") for l in amostra if no_corpus.get(l.get("description_id")) != l]))
        texto.append(f"amostra segue a regra do passo 6: {'ok' if selecionar(corpus, len(amostra)) == amostra else 'falhou'}")
    texto.append(f"reextração a partir de originais/ igual ao corpus: {'ok' if extrair(coleta)[0] == corpus else 'falhou'}")

    SAIDA.mkdir(exist_ok=True)
    (SAIDA / "verificacao.txt").write_text("\n".join(texto) + "\n", encoding="utf-8")
    print("\n".join(texto))
    print(f"Gravado em {SAIDA.name}/verificacao.txt")
    falhas = [linha for linha in texto if ": falhou" in linha]
    if falhas:
        raise SystemExit(f"{len(falhas)} verificações falharam.")


if __name__ == "__main__":
    main()
