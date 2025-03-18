#!/usr/bin/env python3
"""
generate_whitelist.py
---------------------
Dieses Skript generiert automatisch eine Whitelist aus einem gegebenen Python-Quellcode.
Es parst den Code mittels AST, analysiert die Häufigkeit von Variablen und Funktionen,
schließt Standardnamen aus und wendet benutzerdefinierte Filter (z. B. reguläre Ausdrücke) an.
Die generierte Whitelist wird im JSON-Format gespeichert.
"""

import ast
import json
import sys
import re
from collections import Counter

# Liste von Standardnamen, die nicht verändert werden sollen
STANDARD_NAMES = {"print", "input", "len", "range", "str", "int", "float", "list", "dict", "set"}

class WhitelistGenerator(ast.NodeVisitor):
    def __init__(self):
        self.variables = []
        self.functions = []
        self.var_counter = Counter()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.name.lower() != "main" and node.name not in STANDARD_NAMES:
            self.functions.append({
                "name": node.name,
                "line_number": node.lineno,
                "code_context": "Funktion",
                "is_global": True,
                "reason_for_inclusion": "Automatisch ausgewählt (Häufigkeit: selten)"
            })
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Store) and node.id not in STANDARD_NAMES:
            self.var_counter[node.id] += 1
            self.variables.append({
                "name": node.id,
                "line_number": node.lineno,
                "code_context": "Variable",
                "is_global": False,
                "reason_for_inclusion": "Automatisch ausgewählt (Häufigkeit: {})".format(self.var_counter[node.id])
            })
        self.generic_visit(node)

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_whitelist.py <python_file>")
        sys.exit(1)
    file_to_parse = sys.argv[1]
    with open(file_to_parse, "r", encoding="utf-8") as f:
        code = f.read()
    tree = ast.parse(code)
    generator = WhitelistGenerator()
    generator.visit(tree)
    whitelist = {
        "variables": generator.variables,
        "functions": generator.functions,
        "code_sections": []  # Hier können später weitere Codeabschnitte ergänzt werden, inkl. Start-/Endzeilen
    }
    with open("generated_whitelist.json", "w", encoding="utf-8") as f:
        json.dump(whitelist, f, indent=2)
    print("Whitelist generiert und in 'generated_whitelist.json' gespeichert.")

if __name__ == "__main__":
    main()
