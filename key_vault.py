#!/usr/bin/env python3
"""
key_vault.py
------------
Dieses Modul implementiert ein einfaches, aber vollwertiges Key Vault.
Es nutzt Fernet (aus der cryptography-Bibliothek) zur Verschlüsselung und sicheren Speicherung der Schlüssel.
Die Schlüssel werden in einer verschlüsselten JSON-Datei (z. B. key_vault.json.enc) abgelegt.
In einer echten Produktionsumgebung sollte der Master-Key aus einer sicheren Quelle (z. B. Hardware-Sicherheitsmodul) bezogen werden.
"""

import os
import json
from cryptography.fernet import Fernet

class KeyVault:
    def __init__(self, vault_file: str = "key_vault.json.enc", master_key: str = None):
        # Der Master Key wird entweder als Parameter übergeben oder aus der Umgebungsvariable KEY_VAULT_MASTER gelesen.
        if master_key is None:
            master_key = os.environ.get("KEY_VAULT_MASTER")
        if master_key is None:
            raise ValueError("Kein Master Key für das Key Vault gefunden!")
        # Hinweis: In einer echten Produktionsumgebung sollte hier ein Key-Derivation-Mechanismus (z. B. PBKDF2) genutzt werden.
        self.fernet = Fernet(master_key.encode('utf-8'))
        self.vault_file = vault_file
        self.keys = self.load_keys()

    def load_keys(self) -> dict:
        """Lädt die verschlüsselten Schlüssel aus der Vault-Datei und entschlüsselt sie."""
        if not os.path.exists(self.vault_file):
            return {}
        with open(self.vault_file, "rb") as f:
            encrypted_data = f.read()
        try:
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode('utf-8'))
        except Exception as e:
            raise ValueError(f"Fehler beim Entschlüsseln des Key Vault: {e}")

    def get_key(self, role: str) -> str:
        """Gibt den Schlüssel für die angeforderte Rolle zurück (z. B. 'embedder' oder 'detector')."""
        return self.keys.get(role, "")

    def set_key(self, role: str, key: str) -> None:
        """Speichert den Schlüssel für eine bestimmte Rolle im Vault."""
        self.keys[role] = key
        self.save_keys()

    def save_keys(self) -> None:
        """Speichert die Schlüssel verschlüsselt in der Vault-Datei."""
        data = json.dumps(self.keys).encode('utf-8')
        encrypted_data = self.fernet.encrypt(data)
        with open(self.vault_file, "wb") as f:
            f.write(encrypted_data)
