#!/usr/bin/env python3
"""
watermark_detector.py
---------------------
Dieses Skript überprüft einen Python-Quellcode auf das eingebettete Wasserzeichen.
Es extrahiert mittels AST die Wasserzeichen-Bits, wendet die Fehlerkorrektur (Hamming oder Reed-Solomon)
an und berechnet Robustheitsmetriken. Ist das Wasserzeichen verschlüsselt, erfolgt zuvor die Entschlüsselung.
Verwendete Python-Version: 3.12
"""

import ast
import sys
import yaml
import json
import os
from watermark_embedder import generate_watermark_bits
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from error_correction import decode_error_correction

def decrypt_watermark(encrypted_bitstring: str, key: str) -> str:
    """
    Entschlüsselt den verschlüsselten Bitstring mit AES (EAX-Modus).
    Dabei wird der Binärstring in Bytes umgewandelt, entschlüsselt und als Klartext zurückgegeben.
    """
    byte_array = []
    for i in range(0, len(encrypted_bitstring), 8):
        byte_array.append(int(encrypted_bitstring[i:i+8], 2))
    combined = bytes(byte_array)
    nonce = combined[:16]
    tag = combined[16:32]
    ciphertext = combined[32:]
    key_bytes = key.encode('utf-8')
    if len(key_bytes) < 16:
        key_bytes = key_bytes.ljust(16, b'0')
    else:
        key_bytes = key_bytes[:16]
    cipher = AES.new(key_bytes, AES.MODE_EAX, nonce=nonce)
    data = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return data.decode('utf-8')

def transform_name_candidate(original: str, bit: str) -> str:
    """Erstellt einen Kandidaten-Namen basierend auf der Transformation (camelCase) für Bit '1'."""
    if bit == '1':
        parts = original.split('_')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])
    else:
        return original

def detect_transformation(original: str, candidate: str) -> str | None:
    """
    Vergleicht den Originalnamen mit dem Kandidaten-Namen, um festzustellen,
    ob eine Transformation stattgefunden hat und gibt das entsprechende Bit zurück.
    """
    if candidate == original:
        return '0'
    camel = transform_name_candidate(original, '1')
    if candidate == camel:
        return '1'
    return None

class WatermarkDetector(ast.NodeVisitor):
    """
    Diese Klasse besucht den AST und extrahiert Wasserzeichen-Bits,
    indem sie Funktions- und Variablennamen vergleicht.
    """
    def __init__(self, variable_whitelist: list):
        self.variable_whitelist = variable_whitelist
        self.detected_bits = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        for original in self.variable_whitelist:
            bit = detect_transformation(original, node.name)
            if bit is not None:
                self.detected_bits.append(bit)
                print(f"Erkannt in Funktion '{original}': Bit {bit} (gefunden: {node.name})")
                break
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Store):
            for original in self.variable_whitelist:
                bit = detect_transformation(original, node.id)
                if bit is not None:
                    self.detected_bits.append(bit)
                    print(f"Erkannt in Variable '{original}': Bit {bit} (gefunden: {node.id})")
                    break
        self.generic_visit(node)

def main():
    if len(sys.argv) < 2:
        print("Usage: python watermark_detector.py <python_file>")
        sys.exit(1)
    file_to_check = sys.argv[1]
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    with open('whitelist.json', 'r', encoding='utf-8') as f:
        whitelist = json.load(f)
    variable_whitelist = [var['name'] for var in whitelist.get('variables', [])]
    # Generiere das erwartete Wasserzeichen
    full_watermark_bits = generate_watermark_bits(config)
    key = config.get("encryption_key_detector", os.environ.get("ENCRYPTION_KEY"))
    if key:
        full_watermark_bits = decrypt_watermark(full_watermark_bits, key)
    # Wähle die Fehlerkorrektur-Methode (Standard: "hamming")
    error_method = config.get("error_correction", "hamming")
    full_watermark_bits = decode_error_correction(full_watermark_bits, method=error_method)
    print("Vollständiges Wasserzeichen (als Binärstring):")
    print(full_watermark_bits)
    with open(file_to_check, 'r', encoding='utf-8') as f:
        code = f.read()
    tree = ast.parse(code)
    detector = WatermarkDetector(variable_whitelist)
    detector.visit(tree)
    extracted_bits = "".join(detector.detected_bits)
    extracted_bits = decode_error_correction(extracted_bits, method=error_method)
    print("\nExtrahierte Wasserzeichen-Bits aus dem Code:")
    print(extracted_bits)
    expected_bits = full_watermark_bits[:len(extracted_bits)]
    print("\nErwartete Wasserzeichen-Bits (Prefix des vollständigen Musters):")
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
