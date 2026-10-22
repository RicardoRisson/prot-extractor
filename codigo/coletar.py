import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

CONSULTA = "reviewed:true AND cc_bpcp:*"
URL = "https://rest.uniprot.org/uniprotkb/search?" + urlencode(
    {"query": CONSULTA, "format": "json", "size": 50, "sort": "accession asc"})
BPCP = "BIOPHYSICOCHEMICAL PROPERTIES"
CAMPOS = {"phDependence": "ph_dependence", "temperatureDependence": "temperature_dependence"}
RAIZ = Path(__file__).resolve().parent.parent
ORIGINAIS = RAIZ / "originais"
REGISTRO = ORIGINAIS / "coleta.json"
RESULTADOS = RAIZ / "resultados_json"


def agora():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def perguntar():
    while True:
        resposta = input("Descrições: ").strip().lower()
        if resposta == "max":
            return None
        if resposta.isdigit() and int(resposta) > 0:
            return int(resposta)
        print("Digite um número maior que zero ou max.")


def coletar(parar):
    ORIGINAIS.mkdir(exist_ok=True)
    if REGISTRO.exists():
        coleta = json.loads(REGISTRO.read_text(encoding="utf-8"))
    else:
        coleta = {"consulta": CONSULTA, "url_inicial": URL, "inicio": agora(), "versao_uniprot": None,
                  "data_versao": None, "total_registros_busca": None, "paginas": [], "proxima": URL}
    sessao = requests.Session()
    sessao.mount("https://", HTTPAdapter(max_retries=Retry(total=6, backoff_factor=2,
                                                           status_forcelist=[429, 500, 502, 503, 504])))
    try:
        while coleta["proxima"] and not parar(coleta):
            url = coleta["proxima"]
            r = sessao.get(url, timeout=120)
            r.raise_for_status()
            versao = r.headers.get("X-UniProt-Release")
            if coleta["versao_uniprot"] not in (None, versao):
                raise SystemExit(f"A versão do UniProt mudou ({coleta['versao_uniprot']} -> {versao}). "
                                 "Renomeie a pasta originais/ e rode de novo para começar uma coleta nova.")
            resultados = r.json().get("results")
            if not isinstance(resultados, list):
                raise SystemExit(f"Resposta sem a lista 'results' ({url}). Confira antes de continuar.")
            arquivo = f"pagina_{len(coleta['paginas']) + 1:04d}.json"
            (ORIGINAIS / arquivo).write_bytes(r.content)
            coleta["paginas"].append({"arquivo": arquivo, "url": url, "registros": len(resultados), "data": agora()})
            coleta.update(versao_uniprot=versao, data_versao=r.headers.get("X-UniProt-Release-Date"),
                          total_registros_busca=r.headers.get("X-Total-Results"),
                          proxima=r.links.get("next", {}).get("url"))
            temporario = REGISTRO.with_suffix(".tmp")
            temporario.write_text(json.dumps(coleta, ensure_ascii=False, indent=2), encoding="utf-8")
            temporario.replace(REGISTRO)
            print(f"{arquivo}: {len(resultados)} registros")
    except requests.RequestException as erro:
        print(f"Falha de acesso ({erro}). O que já foi baixado está salvo; rode de novo para continuar.")
    return coleta


def extrair(coleta):
    linhas, ocorrencias, vistos, sem_campos = [], [], set(), 0

    def ocorrencia(motivo, decisao, caminho=""):
        ocorrencias.append({"source_file": fonte, "indice_registro": k, "accession": acc,
                            "source_path": caminho, "motivo": motivo, "decisao": decisao})

    for pagina in coleta["paginas"]:
        fonte = f"originais/{pagina['arquivo']}"
        for k, reg in enumerate(json.loads((RAIZ / fonte).read_bytes())["results"]):
            acc = reg.get("primaryAccession")
            seq = (reg.get("sequence") or {}).get("value")
            comentarios = [(i, c) for i, c in enumerate(reg.get("comments") or []) if c.get("commentType") == BPCP]
            textos = [(f"comments[{i}].{campo}.texts[{j}]", tipo, t)
                      for i, c in comentarios for campo, tipo in CAMPOS.items()
                      for j, t in enumerate((c.get(campo) or {}).get("texts") or [])]
            if not comentarios:
                ocorrencia("sem comentário BPCP, embora a busca o exija", "nada extraído; conferir estrutura")
            if not textos:
                sem_campos += 1
            for caminho, tipo, t in textos:
                texto = t.get("value") if isinstance(t, dict) else None
                did = f"{acc}:{caminho}"
                motivo = ("sem identificador" if not acc else "sem sequência" if not seq else
                          "texto não interpretável" if not isinstance(texto, str) or not texto.strip() else
                          "descrição duplicada" if did in vistos else None)
                if motivo:
                    ocorrencia(motivo, "separada do corpus", caminho)
                    continue
                vistos.add(did)
                linhas.append({
                    "description_id": did, "accession": acc,
                    "organism": (reg.get("organism") or {}).get("scientificName"),
                    "sequence": seq, "entry_version": (reg.get("entryAudit") or {}).get("entryVersion"),
                    "property_type": tipo, "text_original": texto, "text_normalized": " ".join(texto.split()),
                    "evidences": t.get("evidences") or [], "source_file": fonte, "source_path": caminho})
    return sorted(linhas, key=lambda l: l["description_id"]), ocorrencias, sem_campos


def pronta(linhas, n):
    return len(linhas) >= n and len({l["property_type"] for l in linhas}) == len(CAMPOS)


def selecionar(linhas, n):
    selecao = linhas[:n]
    for tipo in CAMPOS.values():
        extra = next((l for l in linhas if l["property_type"] == tipo), None)
        if len(selecao) > 1 and extra and extra not in selecao:
            selecao[-1] = extra
    return selecao


def gravar_jsonl(caminho, linhas):
    with open(caminho, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(l, ensure_ascii=False) + "\n" for l in linhas)


def contar(linhas):
    return {"descricoes": len(linhas), "proteinas": len({l["accession"] for l in linhas}),
            "por_categoria": Counter(l["property_type"] for l in linhas)}


def main():
    n = perguntar()
    parar = (lambda coleta: False) if n is None else (lambda coleta: pronta(extrair(coleta)[0], n))
    coleta = coletar(parar)
    linhas, ocorrencias, sem_campos = extrair(coleta)

    RESULTADOS.mkdir(exist_ok=True)
    gravar_jsonl(RESULTADOS / "corpus.jsonl", linhas)
    gravar_jsonl(RESULTADOS / "ocorrencias.jsonl", ocorrencias)
    if n is not None:
        amostra = selecionar(linhas, n)
        gravar_jsonl(RESULTADOS / "corpus_amostra.jsonl", amostra)

    incompleta = coleta["proxima"] and (n is None or not pronta(linhas, n))
    resumo = {"pedido": "max" if n is None else n, "situacao": "parcial" if incompleta else "completa",
              "todas_as_paginas_baixadas": coleta["proxima"] is None,
              "versao_uniprot": coleta["versao_uniprot"], "data_versao": coleta["data_versao"],
              "paginas": len(coleta["paginas"]),
              "registros_processados": sum(p["registros"] for p in coleta["paginas"]),
              "registros_sem_ph_nem_temperatura": sem_campos,
              "corpus": contar(linhas), "amostra": contar(amostra) if n is not None else None,
              "total_ocorrencias": len(ocorrencias)}
    (RESULTADOS / "extracao.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resumo, ensure_ascii=False, indent=2))

    if not incompleta:
        if n is not None and len(linhas) < n:
            print(f"A consulta só tem {len(linhas)} descrições; todas foram gravadas na amostra.")
        for tipo in set(CAMPOS.values()) - {l["property_type"] for l in linhas}:
            print(f"Atenção: não há descrições de {tipo} nos resultados disponíveis.")


if __name__ == "__main__":
    main()
