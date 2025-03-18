#!usrbinenv python3

    """plugin_manager.py
-----------------
Dieses Modul implementiert ein vollwertiges Plugin-System.
Es lädt alle Plugins aus dem Verzeichnis plugins und wendet sie auf einen gegebenen AST an.
Jedes Plugin muss eine Funktion apply(ast_tree ast.AST) - ast.AST implementieren.
"""

import os
import importlib.util
import ast

class PluginManager
    def __init__(self, plugins_dir str = plugins)
        # Das Verzeichnis, in dem die Plugins abgelegt sind
        self.plugins_dir = plugins_dir
        self.plugins = self.load_plugins()

    def load_plugins(self) - list
        Lädt alle Plugins aus dem angegebenen Verzeichnis.
        plugins = []
        if not os.path.exists(self.plugins_dir)
            print(fPlugin-Verzeichnis '{self.plugins_dir}' nicht gefunden. Keine Plugins geladen.)
            return plugins
        for filename in os.listdir(self.plugins_dir)
            if filename.endswith(.py)
                plugin_path = os.path.join(self.plugins_dir, filename)
                module_name = os.path.splitext(filename)[0]
                spec = importlib.util.spec_from_file_location(module_name, plugin_path)
                if spec is None
                    continue
                module = importlib.util.module_from_spec(spec)
                try
                    spec.loader.exec_module(module)
                    if hasattr(module, apply)
                        plugins.append(module)
                        print(fPlugin '{module_name}' geladen.)
                    else
                        print(fPlugin '{module_name}' hat keine 'apply'-Funktion. Übersprungen.)
                except Exception as e
                    print(fFehler beim Laden von Plugin '{module_name}' {e})
        return plugins

    def apply_plugins(self, ast_tree ast.AST) - ast.AST
        Wendet alle geladenen Plugins nacheinander auf den AST an.
        for plugin in self.plugins
            try
                ast_tree = plugin.apply(ast_tree)
                print(fPlugin '{plugin.__name__}' angewendet.)
            except Exception as e
                print(fFehler beim Anwenden von Plugin '{plugin.__name__}' {e})
        return ast_tree
