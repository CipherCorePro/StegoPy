"""
test_watermark.py
-----------------
Dieses Modul enthält Unit-Tests, um die Funktionalität des Wasserzeicheneinbetters zu überprüfen.
Es wird u. a. getestet, ob das Master-Wasserzeichen korrekt generiert und
ob die AST-Transformationen fehlerfrei durchgeführt werden.
"""

import unittest
import ast
from watermark_embedder import WatermarkEmbedder, generate_watermark_bits
import yaml

class TestWatermarkEmbedder(unittest.TestCase):
    def setUp(self):
        # Beispiel-Konfiguration
        self.config = {
            'projektname': "TestProject",
            'copyright': {'jahr': 2023},
            'uuid': "12345678-1234-5678-1234-567812345678",
            'mapping': {
                'variable_namen': { "0": "snake_case", "1": "camelCase" },
                'code_struktur': { "0": "for_loop", "1": "list_comprehension" }
            }
        }
        self.watermark_bits = generate_watermark_bits(self.config)
        # Beispiel-Whitelist: enthält die Namen, die transformiert werden sollen
        self.variable_whitelist = ["example_function", "example_var"]
        self.code_section_whitelist = ["for_loop"]

    def test_generate_watermark_bits(self):
        """
        Testet, ob die Funktion generate_watermark_bits einen Binärstring zurückgibt,
        der ausschließlich aus '0' und '1' besteht.
        """
        bits = generate_watermark_bits(self.config)
        self.assertIsInstance(bits, str)
        self.assertTrue(all(c in "01" for c in bits))

    def test_transform_function(self):
        """
        Testet die AST-Transformation an einem Beispielcode.
        Es wird geprüft, ob der Embedder ohne Fehler läuft und der Code ausführbar bleibt.
        """
        code = """
def example_function():
    example_var = 10
    for i in range(3):
        print(example_var)
    return example_var
"""
        tree = ast.parse(code)
        embedder = WatermarkEmbedder(self.watermark_bits, self.variable_whitelist, self.code_section_whitelist)
        new_tree = embedder.visit(tree)
        # Kompiliere und führe den transformierten Code aus, um Fehler zu erkennen.
        compiled = compile(new_tree, filename="<ast>", mode="exec")
        exec(compiled, {})
        self.assertTrue(True)  # Erreichbar, wenn keine Fehler auftreten.

if __name__ == '__main__':
    unittest.main()
