import sqlite3
import unittest
from pathlib import Path

from etl import carregar, preparar, validar

EXEMPLOS = Path(__file__).parent / "exemplos"


class TestEtl(unittest.TestCase):
    def setUp(self):
        self.banco = sqlite3.connect(":memory:")
        preparar(self.banco)

    def test_carrega_valida_e_rejeita_invalida(self):
        r = carregar(self.banco, EXEMPLOS)
        self.assertEqual(r["carregadas"], 1)
        self.assertEqual(r["rejeitadas"], [("nota-2-invalida.xml", "chave inválida")])

    def test_segunda_carga_nao_duplica(self):
        carregar(self.banco, EXEMPLOS)
        self.assertEqual(carregar(self.banco, EXEMPLOS)["duplicadas"], 1)
        self.assertEqual(self.banco.execute("SELECT COUNT(*) FROM notas").fetchone()[0], 1)

    def test_total_invalido(self):
        nota = {"chave": "1" * 44, "emitente": "x", "emissao": "", "total": "abc"}
        self.assertEqual(validar(nota), "total inválido")


if __name__ == "__main__":
    unittest.main()
