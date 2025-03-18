#!/usr/bin/env python3
"""
plugins/sample_plugin.py
------------------------
Dieses Beispiel-Plugin demonstriert eine zusätzliche Transformation.
Es fügt jedem Funktionsnamen ein Präfix "prod_" hinzu.
Dadurch wird verdeutlicht, wie Du eigene Plugins zur Erweiterung einbinden kannst.
"""

import ast

def apply(ast_tree: ast.AST) -> ast.AST:
    class SamplePlugin(ast.NodeTransformer):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
            # Falls der Funktionsname nicht bereits mit "prod_" beginnt, wird das Präfix hinzugefügt.
            if not node.name.startswith("prod_"):
                original_name = node.name
                node.name = "prod_" + node.name
                print(f"Plugin: Funktion umbenannt: {original_name} -> {node.name}")
            self.generic_visit(node)
            return node
    transformer = SamplePlugin()
    return transformer.visit(ast_tree)
