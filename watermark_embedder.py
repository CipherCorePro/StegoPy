#!/usr/bin/env python3
"""
watermark_embedder.py
---------------------
Dieses Modul implementiert den Wasserzeicheneinbettungsprozess mittels AST-Manipulation.
Erweiterungen in dieser Version:
- Interaktiver Review-Modus.
- Fehlerkorrektur: Auswahl zwischen Hamming(7,4) und Reed-Solomon (konfigurierbar).
- Verschlüsselung: AES-Verschlüsselung (EAX-Modus) mit separaten Schlüsseln.
- Plugin-System: Externe Plugins (z. B. aus dem Verzeichnis "plugins") können zusätzliche Transformationen durchführen.
- Erweiterte Transformationen: Namensänderungen (camelCase, PascalCase, Random Prefix/Suffix).
Verwendete Python-Version: 3.12
"""

import ast
import astor
import yaml
import json
import random
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from error_correction import encode_error_correction

# Verschlüsselung mit AES
def encrypt_watermark(bitstring: str, key: str) -> str:
    """Verschlüsselt den Bitstring mit AES (EAX-Modus) und gibt den verschlüsselten Binärstring zurück."""
    data = bitstring.encode('utf-8')
    key_bytes = key.encode('utf-8')
    if len(key_bytes) < 16:
        key_bytes = key_bytes.ljust(16, b'0')
    else:
        key_bytes = key_bytes[:16]
    cipher = AES.new(key_bytes, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(pad(data, AES.block_size))
    combined = cipher.nonce + tag + ciphertext
    return ''.join(format(b, '08b') for b in combined)

def generate_watermark_bits(config: dict) -> str:
    """
    Generiert den Wasserzeichen-Binärstring basierend auf der Konfiguration.
    Dabei werden folgende Schritte durchgeführt:
      1. Erzeugung eines Master-Strings (Projektname, Jahr, UUID).
      2. Umwandlung in einen Binärstring.
      3. Anwendung eines Fehlerkorrekturcodes (Hamming oder Reed-Solomon, wählbar).
      4. Verschlüsselung des Bitstrings, falls ein Schlüssel vorhanden ist.
      5. Optionale zufällige Bit-Zuordnung.
    """
    master_str = config['projektname'] + str(config['copyright']['jahr']) + config['uuid']
    bits = ''.join(format(ord(c), '08b') for c in master_str)
    # Fehlerkorrektur: Methode wird aus der Konfiguration ausgelesen (Standard: "hamming")
    error_method = config.get("error_correction", "hamming")
    bits = encode_error_correction(bits, method=error_method)
    # Verschlüsselung: Nutze embedder-spezifischen Schlüssel aus Konfiguration oder ENV.
    key = config.get("encryption_key_embedder", os.environ.get("ENCRYPTION_KEY"))
    if key:
        bits = encrypt_watermark(bits, key)
    if config.get("random_bit_assignment", False):
        bit_list = list(bits)
        random.shuffle(bit_list)
        bits = "".join(bit_list)
    return bits

def transform_to_camel(name: str) -> str:
    """Transformiert snake_case in camelCase."""
    parts = name.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])

def transform_to_pascal(name: str) -> str:
    """Transformiert snake_case in PascalCase."""
    parts = name.split('_')
    return ''.join(word.capitalize() for word in parts)

def transform_name(name: str, bit: str, alternate: bool) -> str:
    """
    Transformiert einen Namen basierend auf dem Bit-Wert.
    Bei Bit '1' wird entweder camelCase oder PascalCase verwendet, ggf. mit zufälligem Präfix/Suffix.
    Bei Bit '0' bleibt der Name unverändert.
    """
    if bit == '1':
        if alternate and random.choice([True, False]):
            new_name = transform_to_pascal(name)
            if random.random() < 0.5:
                new_name = "x_" + new_name
            else:
                new_name = new_name + "_x"
            return new_name
        else:
            new_name = transform_to_camel(name)
            if random.random() < 0.5:
                new_name = "x_" + new_name
            else:
                new_name = new_name + "_x"
            return new_name
    else:
        return name

class WatermarkEmbedder(ast.NodeTransformer):
    """
    Diese Klasse transformiert den AST, um Wasserzeichen in den Code einzubetten.
    Funktions- und Variablennamen werden anhand von Wasserzeichen-Bits angepasst.
    """
    def __init__(self, watermark_bits: str, variable_whitelist: list, code_section_whitelist: list,
                 review_mode=False, alternate_naming=False):
        self.watermark_bits = watermark_bits
        self.bit_index = 0
        self.variable_whitelist = variable_whitelist
        self.code_section_whitelist = code_section_whitelist
        self.review_mode = review_mode
        self.alternate_naming = alternate_naming
        self.changes = []

    def next_bit(self) -> str:
        """Gibt das nächste Bit des Wasserzeichens zurück (zyklisch, falls nötig)."""
        if self.bit_index >= len(self.watermark_bits):
            print("Warnung: Wasserzeichen länger als verfügbare Code-Elemente – zyklische Wiederverwendung.")
            self.bit_index = 0
        bit = self.watermark_bits[self.bit_index]
        self.bit_index += 1
        return bit

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        """Besucht Funktionsdefinitionen und ändert den Namen, sofern dieser in der Whitelist steht."""
        if node.name in self.variable_whitelist:
            bit = self.next_bit()
            original_name = node.name
            new_name = transform_name(node.name, bit, self.alternate_naming)
            node.name = new_name
            msg = f"Funktion umbenannt: {original_name} -> {new_name}"
            self.changes.append(msg)
            print(msg)
        self.generic_visit(node)
        return node

    def visit_Name(self, node: ast.Name) -> ast.AST:
        """Besucht Variablennamen und ändert sie, falls sie in der Whitelist stehen."""
        if isinstance(node.ctx, ast.Store) and node.id in self.variable_whitelist:
            bit = self.next_bit()
            original_name = node.id
            new_name = transform_name(node.id, bit, self.alternate_naming)
            node.id = new_name
            msg = f"Variable umbenannt: {original_name} -> {new_name}"
            self.changes.append(msg)
            print(msg)
        return node

    def visit_For(self, node: ast.For) -> ast.AST:
        """Transformiert For-Schleifen in List Comprehensions, wenn dies in der Whitelist aktiviert ist."""
        if "for_loop" in self.code_section_whitelist:
            bit = self.next_bit()
            if bit == '1':
                original_target = node.target.id
                node.target.id = original_target + "_"
                new_node = ast.Expr(
                    value=ast.ListComp(
                        elt=ast.Name(id=node.target.id, ctx=ast.Load()),
                        generators=[ast.comprehension(
                            target=node.target,
                            iter=node.iter,
                            ifs=[],
                            is_async=0
                        )]
                    )
                )
                msg = f"For-Schleife in List Comprehension umgewandelt; Schleifenvariable '{original_target}' -> '{node.target.id}'."
                self.changes.append(msg)
                print(msg)
                return ast.copy_location(new_node, node)
        self.generic_visit(node)
        return node

def main():
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    with open('whitelist.json', 'r', encoding='utf-8') as f:
        whitelist = json.load(f)
    watermark_bits = generate_watermark_bits(config)
    print("Erzeugte Wasserzeichen-Bits:", watermark_bits)
    with open('file_to_transform.py', 'r', encoding='utf-8') as f:
        code = f.read()
    tree = ast.parse(code)
    variable_whitelist = [var['name'] for var in whitelist.get('variables', [])]
    code_section_whitelist = [section['type'] for section in whitelist.get('code_sections', [])]
    # Plugins werden extern über den Plugin Manager angewendet.
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
    with open('file_transformed.py', 'w', encoding='utf-8') as f:
        f.write(new_code)
    print("Transformierter Code wurde in file_transformed.py gespeichert.")

if __name__ == "__main__":
    main()
