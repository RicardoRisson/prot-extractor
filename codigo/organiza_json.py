import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGINAIS = RAIZ / "originais"
SAIDA = RAIZ / "originais_formatados"


def main():
    arquivos = sorted(ORIGINAIS.glob("*.json"))
    if not arquivos:
        raise SystemExit("Nenhum .json em originais/. Rode antes o coletar.py.")
    SAIDA.mkdir(exist_ok=True)
    formatados = 0
    for arquivo in arquivos:
        dados = json.loads(arquivo.read_bytes())
        texto = json.dumps(dados, ensure_ascii=False, indent=2)
        if arquivo.read_text(encoding="utf-8") == texto:
            continue
        if json.loads(texto) != dados:
            raise SystemExit(f"{arquivo.name}: o conteúdo mudaria ao formatar; arquivo mantido como estava.")
        destino = SAIDA / f"{arquivo.stem}_formatado{arquivo.suffix}"
        temporario = destino.with_suffix(".tmp")
        temporario.write_text(texto, encoding="utf-8")
        temporario.replace(destino)
        formatados += 1
        print(f"{SAIDA.name}/{destino.name} formatado")
    print(f"{formatados} arquivos formatados, {len(arquivos) - formatados} já estavam formatados. "
          "O conteúdo continua idêntico.")


if __name__ == "__main__":
    main()