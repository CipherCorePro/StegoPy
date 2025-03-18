#!/usr/bin/env python3
"""
robustness_tests.py
-------------------
Dieses Skript führt Robustheitstests für den Wasserzeicheneinbettungsprozess durch.
Es simuliert verschiedene Code-Transformationen, darunter Minifizierung und Obfuskation,
und überprüft anschließend, ob das Wasserzeichen noch erkannt wird.
Zusätzlich können externe Tools wie pyminifier integriert werden.
"""

import subprocess

def minify_code(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        code = f.read()
    minified = "\n".join(line for line in code.splitlines() if line.strip() != "")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(minified)
    print(f"Code minifiziert und in '{output_file}' gespeichert.")

def run_detector(file_to_check):
    result = subprocess.run(["python", "watermark_detector.py", file_to_check],
                            capture_output=True, text=True)
    print("Detector Output:")
    print(result.stdout)
    return result.stdout

def main():
    input_file = "file_transformed.py"
    output_file = "file_transformed_min.py"
    minify_code(input_file, output_file)
    print("Ergebnisse nach Minifizierung:")
    run_detector(output_file)
    # Hier könnten weitere Transformationen (z.B. Obfuskation) integriert werden.

if __name__ == "__main__":
    main()
