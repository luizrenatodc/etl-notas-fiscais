"""Lê XMLs de nota fiscal, valida e carrega em SQLite sem duplicar."""
import sqlite3
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def extrair(caminho):
    raiz = ET.parse(caminho).getroot()
    pega = lambda campo: (raiz.findtext(campo) or "").strip()
    return {"chave": pega("chave"), "emitente": pega("emitente/nome"), "emissao": pega("emissao"), "total": pega("total")}


def validar(nota):
    if len(nota["chave"]) != 44 or not nota["chave"].isdigit():
        return "chave inválida"
    if not nota["emitente"]:
        return "emitente vazio"
    try:
        if float(nota["total"]) <= 0:
            return "total inválido"
    except ValueError:
        return "total inválido"
    return None


def preparar(banco):
    banco.execute("CREATE TABLE IF NOT EXISTS notas (chave TEXT PRIMARY KEY, emitente TEXT, emissao TEXT, total REAL)")


def carregar(banco, pasta):
    resumo = {"carregadas": 0, "duplicadas": 0, "rejeitadas": []}
    for arquivo in sorted(Path(pasta).glob("*.xml")):
        try:
            nota = extrair(arquivo)
        except ET.ParseError:
            resumo["rejeitadas"].append((arquivo.name, "XML malformado"))
            continue
        erro = validar(nota)
        if erro:
            resumo["rejeitadas"].append((arquivo.name, erro))
            continue
        c = banco.execute("INSERT OR IGNORE INTO notas VALUES (:chave, :emitente, :emissao, :total)", nota)
        resumo["carregadas" if c.rowcount else "duplicadas"] += 1
    banco.commit()
    return resumo


if __name__ == "__main__":
    raiz = Path(__file__).parent
    banco = sqlite3.connect(raiz / "notas.db")
    preparar(banco)
    print(carregar(banco, sys.argv[1] if len(sys.argv) > 1 else raiz / "exemplos"))
