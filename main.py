#!/usr/bin/env python3
"""
main.py
-------
Dies ist der Haupteinstiegspunkt für das erweiterte Wasserzeichen-System.
Über die Kommandozeile kann zwischen Wasserzeicheneinbettung (embed) und -erkennung (detect) gewählt werden.
Zusätzlich werden hier die Konfiguration geladen, der Key Vault initialisiert und der Plugin Manager genutzt.
"""

import argparse
import yaml
import os
import ast
import astor
from watermark_embedder import WatermarkEmbedder, generate_watermark_bits
from watermark_detector import WatermarkDetector
from plugin_manager import PluginManager
from key_vault import KeyVault

def load_config(config_file: str = "config.yaml") -> dict:
    """Lädt die Konfiguration aus der YAML-Datei."""
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config

def main():
    parser = argparse.ArgumentParser(description="Erweitertes Wasserzeichen-System")
    parser.add_argument("mode", choices=["embed", "detect"], help="Modus: 'embed' für Einbettung, 'detect' für Erkennung")
    parser.add_argument("file", help="Pfad zur Eingabedatei (Python-Quelldatei)")
    args = parser.parse_args()

    config = load_config()

    # Initialisiere das Key Vault
    try:
        key_vault = KeyVault()
    except Exception as e:
        print(f"Key Vault Fehler: {e}")
        key_vault = None

    if args.mode == "embed":
        # Wasserzeicheneinbettung
        if key_vault:
            config["encryption_key_embedder"] = key_vault.get_key("embedder")
        # Generiere Wasserzeichen-Bits (inklusive Fehlerkorrektur und Verschlüsselung)
        watermark_bits = generate_watermark_bits(config)
        print("Erzeugte Wasserzeichen-Bits:", watermark_bits)
        # Lese den zu transformierenden Code ein
        with open(args.file, "r", encoding="utf-8") as f:
            code = f.read()
        tree = ast.parse(code)
        # Lade die Whitelist (Liste kritischer Variablen/Funktionen) aus der JSON-Datei
        import json
        with open("whitelist.json", "r", encoding="utf-8") as f:
            whitelist = json.load(f)
        variable_whitelist = [var["name"] for var in whitelist.get("variables", [])]
        code_section_whitelist = [section["type"] for section in whitelist.get("code_sections", [])]
        # Plugin Manager initialisieren und Plugins anwenden
        plugin_manager = PluginManager()
        tree = plugin_manager.apply_plugins(tree)
        # Wasserzeichen-Embedder instanziieren und AST transformieren
        embedder = WatermarkEmbedder(watermark_bits, variable_whitelist, code_section_whitelist,
                                      review_mode=True, alternate_naming=config.get("alternate_naming", False))
        new_tree = embedder.visit(tree)
        new_code = astor.to_source(new_tree)
        if embedder.review_mode:
            print("Die folgenden Änderungen wurden vorgenommen:")
            for change in embedder.changes:
                print(" -", change)
            confirmation = input("Möchtest Du die Änderungen übernehmen? (j/n): ")
            if confirmation.lower() != 'j':
                print("Keine Änderungen übernommen.")
                return
        with open("file_transformed.py", "w", encoding="utf-8") as f:
            f.write(new_code)
        print("Transformierter Code wurde in 'file_transformed.py' gespeichert.")
    elif args.mode == "detect":
        # Wasserzeichenerkennung
        if key_vault:
            config["encryption_key_detector"] = key_vault.get_key("detector")
        with open(args.file, "r", encoding="utf-8") as f:
            code = f.read()
        tree = ast.parse(code)
        import json
        with open("whitelist.json", "r", encoding="utf-8") as f:
            whitelist = json.load(f)
        variable_whitelist = [var["name"] for var in whitelist.get("variables", [])]
        detector = WatermarkDetector(variable_whitelist)
        detector.visit(tree)
        extracted_bits = "".join(detector.detected_bits)
        from error_correction import decode_error_correction
        error_method = config.get("error_correction", "hamming")
        extracted_bits = decode_error_correction(extracted_bits, method=error_method)
        print("\nExtrahierte Wasserzeichen-Bits aus dem Code:")
        print(extracted_bits)
        full_watermark_bits = generate_watermark_bits(config)
        if key_vault or config.get("encryption_key_detector"):
            # Entschlüsseln, falls Schlüssel vorhanden sind
            from watermark_detector import decrypt_watermark
            full_watermark_bits = decrypt_watermark(full_watermark_bits, config.get("encryption_key_detector", ""))
        full_watermark_bits = decode_error_correction(full_watermark_bits, method=error_method)
        print("\nErwartetes Wasserzeichen (Prefix des vollständigen Musters):")
        expected_bits = full_watermark_bits[:len(extracted_bits)]
        print(expected_bits)
        match_count = len([b for b, e in zip(extracted_bits, expected_bits) if b == e])
        confidence = (match_count / len(expected_bits) * 100) if expected_bits else 0
        if extracted_bits == expected_bits:
            print("\nWasserzeichen erkannt: Der Code enthält dein eingebettetes Wasserzeichen.")
        else:
            print(f"\nWasserzeichen teilweise erkannt: {confidence:.2f}% der Bits stimmen überein.")
            print("Wasserzeichen NICHT vollständig erkannt oder unvollständig.")

if __name__ == "__main__":
    main()
