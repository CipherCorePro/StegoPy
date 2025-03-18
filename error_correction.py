#!/usr/bin/env python3
"""
error_correction.py
-------------------
Dieses Modul implementiert alternative Fehlerkorrekturcodes.
Unterstützt werden:
- Hamming(7,4)-Code
- Reed-Solomon-Code (über die Bibliothek reedsolo)

Die Funktionen encode_error_correction und decode_error_correction
wenden den gewählten Algorithmus zur Kodierung bzw. Dekodierung an.
"""

import math

# Hamming-Code Implementierung
def hamming_encode(bitstring: str) -> str:
    """Kodiert einen Binärstring mittels Hamming(7,4)-Code."""
    # Falls die Länge nicht durch 4 teilbar ist, wird gepadded.
    pad_length = (4 - len(bitstring) % 4) % 4
    bitstring += "0" * pad_length
    coded = []
    for i in range(0, len(bitstring), 4):
        d = [int(b) for b in bitstring[i:i+4]]
        # Berechnung der Paritätsbits
        p1 = d[0] ^ d[1] ^ d[3]
        p2 = d[0] ^ d[2] ^ d[3]
        p3 = d[1] ^ d[2] ^ d[3]
        # Zusammenstellung des 7-Bit-Codeworts
        codeword = [p1, p2, d[0], p3, d[1], d[2], d[3]]
        coded.extend(str(bit) for bit in codeword)
    return "".join(coded)

def hamming_decode(bitstring: str) -> str:
    """Dekodiert einen Binärstring, der mittels Hamming(7,4)-Code kodiert wurde."""
    def correct_hamming_block(codeword: str) -> str:
        bits = [int(b) for b in codeword]
        s1 = bits[0] ^ bits[2] ^ bits[3] ^ bits[6]
        s2 = bits[1] ^ bits[2] ^ bits[4] ^ bits[6]
        s3 = bits[3] ^ bits[4] ^ bits[5] ^ bits[6]
        syndrome = (s3 << 2) | (s2 << 1) | s1
        if syndrome != 0 and syndrome <= 7:
            idx = syndrome - 1
            bits[idx] ^= 1
        # Extrahiere die 4 Databits
        return "".join(str(b) for b in [bits[2], bits[4], bits[5], bits[6]])
    decoded = ""
    for i in range(0, len(bitstring), 7):
        block = bitstring[i:i+7]
        if len(block) == 7:
            decoded += correct_hamming_block(block)
    return decoded

# Reed-Solomon Implementierung
try:
    import reedsolo
except ImportError:
    reedsolo = None

def reed_solomon_encode(bitstring: str) -> str:
    """Kodiert einen Binärstring mittels Reed-Solomon-Code.
    (Achtung: Die Bibliothek 'reedsolo' muss installiert sein.)
    """
    if reedsolo is None:
        raise ImportError("Die Bibliothek 'reedsolo' ist nicht installiert.")
    # Umwandlung des Bitstrings in Bytes (Länge sollte durch 8 teilbar sein)
    byte_array = []
    for i in range(0, len(bitstring), 8):
        byte = int(bitstring[i:i+8], 2)
        byte_array.append(byte)
    data = bytes(byte_array)
    # RSCodec mit 10 Fehlerkorrektur-Bytes initialisieren
    rs = reedsolo.RSCodec(10)
    encoded = rs.encode(data)
    # Rückumwandlung in einen Binärstring
    return ''.join(format(b, '08b') for b in encoded)

def reed_solomon_decode(bitstring: str) -> str:
    """Dekodiert einen Binärstring, der mittels Reed-Solomon kodiert wurde.
    (Achtung: Die Bibliothek 'reedsolo' muss installiert sein.)
    """
    if reedsolo is None:
        raise ImportError("Die Bibliothek 'reedsolo' ist nicht installiert.")
    byte_array = []
    for i in range(0, len(bitstring), 8):
        byte = int(bitstring[i:i+8], 2)
        byte_array.append(byte)
    data = bytes(byte_array)
    rs = reedsolo.RSCodec(10)
    decoded = rs.decode(data)
    # decoded liefert ein Tupel: (message, ecc)
    message = decoded[0]
    return ''.join(format(b, '08b') for b in message)

def encode_error_correction(bitstring: str, method: str = "hamming") -> str:
    """Wendet den ausgewählten Fehlerkorrekturalgorithmus zur Kodierung an."""
    match method:
        case "hamming":
            return hamming_encode(bitstring)
        case "reed-solomon":
            return reed_solomon_encode(bitstring)
        case _:
            raise ValueError(f"Unbekannte Fehlerkorrektur-Methode: {method}")

def decode_error_correction(bitstring: str, method: str = "hamming") -> str:
    """Wendet den ausgewählten Fehlerkorrekturalgorithmus zur Dekodierung an."""
    match method:
        case "hamming":
            return hamming_decode(bitstring)
        case "reed-solomon":
            return reed_solomon_decode(bitstring)
        case _:
            raise ValueError(f"Unbekannte Fehlerkorrektur-Methode: {method}")
