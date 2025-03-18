"""
watermark_embedder.py
---------------------
Dieses Modul implementiert den Wasserzeicheneinbettungsprozess mittels AST-Manipulation.
Es liest die Konfigurations- und Whitelist-Dateien ein, generiert das Master-Wasserzeichen,
parst den zu transformierenden Code und wendet die Wasserzeichen-Steganographie auf
Variablen-/Funktionsnamen sowie Code-Strukturen an.

Verwendete Python-Version: 3.12
"""

import ast
import astor  # Zum Zurückkonvertieren des AST in lesbaren Quellcode.
import yaml
import json

# -----------------------------------------------------------------------------
# Funktion: generate_watermark_bits
# -----------------------------------------------------------------------------
def generate_watermark_bits(config: dict) -> str:
    """
    Generiert das Master-Wasserzeichen als Binärstring aus den Konfigurationsdaten.
    
    Es werden der Projektname, das Copyright-Jahr und die UUID zusammengefügt
    und jedes Zeichen in eine 8-Bit-Binärdarstellung konvertiert.
    
    :param config: Das Konfigurations-Dictionary aus der YAML-Datei.
    :return: Binärstring des Wasserzeichens.
    """
    master_str = config['projektname'] + str(config['copyright']['jahr']) + config['uuid']
    bits = ''.join(format(ord(c), '08b') for c in master_str)
    return bits

# -----------------------------------------------------------------------------
# Klasse: WatermarkEmbedder
# -----------------------------------------------------------------------------
class WatermarkEmbedder(ast.NodeTransformer):
    """
    Diese Klasse übernimmt die Transformation des ASTs und bettet das Wasserzeichen
    in ausgewählte Code-Elemente ein.
    
    Die Transformation erfolgt in mehreren Schritten:
    1. Auswahl eines Bits aus dem Wasserzeichen.
    2. Änderung von Variablennamen oder Funktionsnamen basierend auf dem Bit:
       - Bit '1': Umwandlung in camelCase.
       - Bit '0': Beibehaltung (snake_case).
    3. Beispielhafte Umwandlung von for-Schleifen in List Comprehensions,
       wenn das entsprechende Bit und die Whitelist-Kriterien erfüllt sind.
    """
    def __init__(self, watermark_bits: str, variable_whitelist: list, code_section_whitelist: list):
        self.watermark_bits = watermark_bits
        self.bit_index = 0
        self.variable_whitelist = variable_whitelist
        self.code_section_whitelist = code_section_whitelist

    def next_bit(self) -> str | None:
        """
        Gibt das nächste Bit aus dem Wasserzeichen zurück und erhöht den Zähler.
        Falls alle Bits verwendet wurden, wird None zurückgegeben.
        """
        if self.bit_index < len(self.watermark_bits):
            bit = self.watermark_bits[self.bit_index]
            self.bit_index += 1
            return bit
        return None

    def transform_name(self, name: str, bit: str) -> str:
        """
        Transformiert den Namen basierend auf dem Wasserzeichen-Bit.
        
        Bei Bit '1' wird der Name in camelCase umgewandelt,
        bei Bit '0' bleibt der Name im snake_case.
        """
        if bit == '1':
            # Umwandlung in camelCase: Teile den Namen an '_' und verknüpfe.
            parts = name.split('_')
            return parts[0] + ''.join(word.capitalize() for word in parts[1:])
        else:
            # Bei '0' wird der Name nicht verändert (snake_case).
            return name

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        """
        Überschreibt die Behandlung von Funktionsdefinitionen.
        Falls der Funktionsname in der Whitelist enthalten ist, wird er anhand eines
        Wasserzeichen-Bits transformiert.
        """
        if node.name in self.variable_whitelist:
            bit = self.next_bit()
            if bit is not None:
                original_name = node.name
                node.name = self.transform_name(node.name, bit)
                print(f"Funktion umbenannt: {original_name} -> {node.name}")
        self.generic_visit(node)
        return node

    def visit_Name(self, node: ast.Name) -> ast.AST:
        """
        Überschreibt die Behandlung von Namen (Variablen).
        Wird nur bei Speicherung (Store-Kontext) angewendet, falls der Name in der Whitelist steht.
        """
        if isinstance(node.ctx, ast.Store) and node.id in self.variable_whitelist:
            bit = self.next_bit()
            if bit is not None:
                original_name = node.id
                node.id = self.transform_name(node.id, bit)
                print(f"Variable umbenannt: {original_name} -> {node.id}")
        return node

    def visit_For(self, node: ast.For) -> ast.AST:
        """
        Überschreibt die Behandlung von For-Schleifen.
        Wenn die Schleifenart in der Whitelist ist und das Wasserzeichen-Bit '1' lautet,
        wird die For-Schleife beispielhaft in eine List Comprehension umgewandelt.
        """
        if "for_loop" in self.code_section_whitelist:
            bit = self.next_bit()
            if bit == '1':
                # Vereinfachte Transformation: Erstelle eine List Comprehension,
                # die den Schleifeninhalt repräsentiert.
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
                print("For-Schleife in List Comprehension umgewandelt.")
                return ast.copy_location(new_node, node)
        self.generic_visit(node)
        return node

# -----------------------------------------------------------------------------
# Funktion: main
# -----------------------------------------------------------------------------
def main():
    """
    Hauptfunktion, die folgende Schritte ausführt:
    1. Laden der Konfigurations- und Whitelist-Dateien.
    2. Generierung des Wasserzeichen-Binärstrings.
    3. Einlesen des zu transformierenden Python-Codes (Beispiel: file_to_transform.py).
    4. AST-Transformation mittels WatermarkEmbedder.
    5. Speicherung des transformierten Codes in file_transformed.py.
    """
    # Lade Konfigurationsdatei
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Lade manuelle Whitelist
    with open('whitelist.json', 'r', encoding='utf-8') as f:
        whitelist = json.load(f)
    
    # Erzeuge Wasserzeichen-Bits aus der Konfiguration
    watermark_bits = generate_watermark_bits(config)
    print("Erzeugte Wasserzeichen-Bits:", watermark_bits)

    # Lese den zu transformierenden Python-Code ein (Beispieldatei)
    with open('file_to_transform.py', 'r', encoding='utf-8') as f:
        code = f.read()

    tree = ast.parse(code)

    # Extrahiere die Whitelist-Einträge
    variable_whitelist = [var['name'] for var in whitelist.get('variables', [])]
    code_section_whitelist = [section['type'] for section in whitelist.get('code_sections', [])]

    # Initialisiere den WatermarkEmbedder und wende die Transformation an
    embedder = WatermarkEmbedder(watermark_bits, variable_whitelist, code_section_whitelist)
    new_tree = embedder.visit(tree)
    new_code = astor.to_source(new_tree)

    # Speichere den transformierten Code
    with open('file_transformed.py', 'w', encoding='utf-8') as f:
        f.write(new_code)
    print("Transformierter Code wurde in file_transformed.py gespeichert.")

if __name__ == "__main__":
    main()
