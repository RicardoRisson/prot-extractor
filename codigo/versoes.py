import ast
import platform
import sys
from datetime import date
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import requests

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parent
SAIDA = RAIZ / "temp.txt"
URL = "https://rest.uniprot.org/uniprotkb/search?query=reviewed:true&size=1"


def versao_uniprot():
    r = requests.get(URL, timeout=60)
    r.raise_for_status()
    return r.headers.get("X-UniProt-Release")


def bibliotecas():
    locais = {arquivo.stem for arquivo in PASTA.glob("*.py")}
    nomes = set()
    for arquivo in PASTA.glob("*.py"):
        for no in ast.walk(ast.parse(arquivo.read_text(encoding="utf-8"))):
            if isinstance(no, ast.Import):
                nomes.update(a.name.split(".")[0] for a in no.names)
            elif isinstance(no, ast.ImportFrom) and no.level == 0:
                nomes.add(no.module.split(".")[0])
    linhas = []
    for nome in sorted(nomes - locais - set(sys.stdlib_module_names)):
        try:
            linhas.append(f"  {nome} {version(nome)}")
        except PackageNotFoundError:
            linhas.append(f"  {nome} (versão não encontrada)")
    return linhas


def main():
    texto = [f"versão do UniProt: {versao_uniprot()}",
             f"data: {date.today().isoformat()}",
             f"Python: {platform.python_version()}",
             "bibliotecas:"] + bibliotecas()
    SAIDA.write_text("\n".join(texto) + "\n", encoding="utf-8")
    print("\n".join(texto))
    print(f"Gravado em {SAIDA.name}")


if __name__ == "__main__":
    main()