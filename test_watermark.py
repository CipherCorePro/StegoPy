"""
test_watermark.py
-----------------
Dieses Modul enthält Unit-Tests zur Überprüfung der Funktionalität des Wasserzeicheneinbettungsprozesses.
Es werden unter anderem die korrekte Generierung des Wasserzeichens, die fehlerfreie Transformation
des Quellcodes und die Ausführbarkeit des transformierten Codes getestet.
"""

import unittest
import ast
from watermark_embedder import WatermarkEmbedder, generate_watermark_bits
import yaml

class TestWatermarkEmbedder(unittest.TestCase):
    def setUp(self):
        self.config = {
            'projektname': "TestProject",
            'copyright': {'jahr': 2023},
            'uuid': "12345678-1234-5678-1234-567812345678",
            'mapping': {
                'variable_namen': { "0": "snake_case", "1": "camelCase" },
                'code_struktur': { "0": "for_loop", "1": "list_comprehension" }
            },
            'random_bit_assignment': False,
            'alternate_naming': False
        }
        self.watermark_bits = generate_watermark_bits(self.config)
        self.variable_whitelist = ["example_function", "example_var"]
        self.code_section_whitelist = ["for_loop"]

    def test_generate_watermark_bits(self):
        bits = generate_watermark_bits(self.config)
        self.assertIsInstance(bits, str)
        self.assertTrue(all(c in "01" for c in bits))

    def test_transform_function(self):
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
        compiled = compile(new_tree, filename="<ast>", mode="exec")
        exec(compiled, {})
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
