"""Coleta registros revisados do UniProt com propriedades biofísico-químicas e extrai as
descrições de pH e temperatura (uma linha por elemento textual).

Uso, a partir da raiz do projeto:
    python codigo/coletar.py --amostra   # coleta até ter 100 descrições com as duas categorias
    python codigo/coletar.py             # continua de onde parou até a última página
Com a coleta completa, rodar de novo só refaz a extração a partir de originais/ (sem rede).
Para uma coleta nova, use outra pasta: --saida coleta2.   Requer: pip install requests
"""
import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

CONSULTA = "reviewed:true AND cc_bpcp:*"
BASE = "https://rest.uniprot.org/uniprotkb/search"
BPCP = "BIOPHYSICOCHEMICAL PROPERTIES"
CAMPOS = {"phDependence": "ph_dependence", "temperatureDependence": "temperature_dependence"}
CHAVES_CONHECIDAS = {"commentType", "molecule", "absorption", "kineticParameters",
                     "phDependence", "redoxPotential", "temperatureDependence"}
N_AMOSTRA = 100


def agora():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def coletar(base, tamanho, parar):
    """Salva cada página sem alterações em originais/ e retoma da última página concluída."""
    orig = base / "originais"
    orig.mkdir(parents=True, exist_ok=True)
    reg = orig / "coleta.json"
    if reg.exists():
        man = json.loads(reg.read_text(encoding="utf-8"))
    else:
        url = f"{BASE}?" + urlencode({"query": CONSULTA, "format": "json", "size": tamanho, "sort": "accession asc"})
        man = {"consulta": CONSULTA, "url_inicial": url, "inicio": agora(), "versao_uniprot": None,
               "data_versao": None, "total_registros_busca": None, "paginas": [], "proxima": url}
    sessao = requests.Session()
    sessao.mount("https://", HTTPAdapter(max_retries=Retry(total=6, backoff_factor=2,
                                                           status_forcelist=[429, 500, 502, 503, 504])))
    try:
        while man["proxima"] and not parar(man):
            r = sessao.get(man["proxima"], timeout=120)
            r.raise_for_status()
            versao = r.headers.get("X-UniProt-Release")
            if man["versao_uniprot"] and versao != man["versao_uniprot"]:
                raise SystemExit(f"A versão do UniProt mudou ({man['versao_uniprot']} -> {versao}). "
                                 "Faça a nova coleta em outra pasta com --saida.")
            resultados = r.json().get("results")
            if not isinstance(resultados, list):
                raise SystemExit(f"Resposta sem a lista 'results' ({man['proxima']}). Confira antes de seguir.")
            arquivo = f"pagina_{len(man['paginas']) + 1:04d}.json"
            (orig / arquivo).write_bytes(r.content)
            man.update(versao_uniprot=versao, data_versao=r.headers.get("X-UniProt-Release-Date"),
                       total_registros_busca=r.headers.get("X-Total-Results"))
            man["paginas"].append({"arquivo": arquivo, "url": man["proxima"],
                                   "registros": len(resultados), "data": agora()})
            man["proxima"] = r.links.get("next", {}).get("url")
            tmp = reg.with_suffix(".tmp")
            tmp.write_text(json.dumps(man, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(reg)
            print(f"{arquivo}: {len(resultados)} registros")
    except requests.RequestException as e:
        print(f"Falha de acesso ({e}). O que já foi salvo está preservado; rode de novo para retomar.")
    return man


def extrair(base, man):
    """Lê os arquivos salvos e devolve (descrições, ocorrências, contagens)."""
    linhas, ocorr, vistos, n = [], [], set(), Counter()

    def ocorrencia(motivo, decisao, caminho=""):
        ocorr.append({"source_file": fonte, "indice_registro": k, "accession": acc,
                      "source_path": caminho, "motivo": motivo, "decisao": decisao})

    for pagina in man["paginas"]:
        fonte = f"originais/{pagina['arquivo']}"
        for k, reg in enumerate(json.loads((base / fonte).read_bytes())["results"]):
            n["registros"] += 1
            acc = reg.get("primaryAccession")
            seq = (reg.get("sequence") or {}).get("value")
            bpcp = [(i, c) for i, c in enumerate(reg.get("comments") or []) if c.get("commentType") == BPCP]
            if not bpcp:
                ocorrencia("sem comentário BPCP, embora a busca o exija", "nada extraído; conferir estrutura")
            textos = []
            for i, c in bpcp:
                if novas := sorted(set(c) - CHAVES_CONHECIDAS):
                    ocorrencia(f"campo desconhecido: {novas}", "descrições mantidas; conferir", f"comments[{i}]")
                for campo, tipo in CAMPOS.items():
                    for j, t in enumerate((c.get(campo) or {}).get("texts") or []):
                        textos.append((f"comments[{i}].{campo}.texts[{j}]", tipo, t))
            if not textos:
                n["sem_ph_nem_temperatura"] += 1
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
    return sorted(linhas, key=lambda l: l["description_id"]), ocorr, n


def pronta(linhas):
    return len(linhas) >= N_AMOSTRA and len({l["property_type"] for l in linhas}) == len(CAMPOS)


def amostra(linhas):
    """Primeiras 100 por description_id; se faltar uma categoria, a última linha vira a 1ª dela."""
    sel = linhas[:N_AMOSTRA]
    for tipo in CAMPOS.values():
        extra = next((l for l in linhas if l["property_type"] == tipo), None)
        if extra and extra not in sel:
            sel[-1] = extra
    return sel


def gravar_jsonl(caminho, linhas):
    with open(caminho, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(l, ensure_ascii=False) + "\n" for l in linhas)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--saida", type=Path, default=Path("."), help="pasta do projeto (padrão: a atual)")
    p.add_argument("--tamanho", type=int, default=50, help="registros por página, até 500 (só na 1ª execução)")
    p.add_argument("--amostra", action="store_true", help="parar quando houver descrições para a amostra")
    a = p.parse_args()

    parar = (lambda m: pronta(extrair(a.saida, m)[0])) if a.amostra else (lambda m: False)
    man = coletar(a.saida, a.tamanho, parar)
    linhas, ocorr, n = extrair(a.saida, man)

    gravar_jsonl(a.saida / "corpus.jsonl", linhas)
    gravar_jsonl(a.saida / "ocorrencias.jsonl", ocorr)
    arq_amostra = a.saida / "corpus_amostra.jsonl"
    if not arq_amostra.exists() and (pronta(linhas) or man["proxima"] is None):
        gravar_jsonl(arq_amostra, amostra(linhas))  # criada uma vez e depois preservada

    info = {"consulta": CONSULTA, "versao_uniprot": man["versao_uniprot"], "data_versao": man["data_versao"],
            "situacao": "completa" if man["proxima"] is None else "parcial", "paginas": len(man["paginas"]),
            "registros_na_busca": man["total_registros_busca"], "registros_processados": n["registros"],
            "registros_sem_ph_nem_temperatura": n["sem_ph_nem_temperatura"], "descricoes": len(linhas),
            "proteinas": len({l["accession"] for l in linhas}),
            "por_categoria": Counter(l["property_type"] for l in linhas),
            "ocorrencias": Counter(o["motivo"] for o in ocorr)}
    (a.saida / "extracao.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()