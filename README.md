# Wasserzeichen-Einbettung in Python-Code – Erweiterte Produktionsumgebung

Dieses Projekt demonstriert eine vollwertige, produktionsreife Umgebung zur Einbettung „unsichtbarer“ Wasserzeichen in Python-Quellcode. Neben der ursprünglichen Idee, durch AST-Manipulation binäre Informationen (basierend auf Projektname, Copyright‑Jahr und UUID) in den Code einzubetten, umfasst dieses System nun:

- **Ein vollwertiges Plugin-System:** Externe Plugins (aus dem Verzeichnis `plugins`) können zusätzliche Transformationen am AST durchführen.
- **Erweiterte Transformationen:** Neben Namensänderungen (camelCase, PascalCase, zufälliger Prefix/Suffix) wird jetzt auch ein alternativer Fehlerkorrektur-Algorithmus (Reed-Solomon-Code) neben dem klassischen Hamming(7,4)-Code unterstützt.
- **Ein echtes Key Vault:** Mit Hilfe der `cryptography`‑Bibliothek (Fernet) werden Verschlüsselungsschlüssel sicher in einer verschlüsselten JSON‑Datei gespeichert. Der Master-Key wird über die Umgebungsvariable `KEY_VAULT_MASTER` bezogen.
- **Modulare Architektur:** Alle Funktionalitäten (Konfiguration, Fehlerkorrektur, Verschlüsselung, Plugin-Management) sind in separaten Modulen gekapselt, was Wartbarkeit, Testbarkeit und Erweiterbarkeit verbessert.

---

## Inhaltsverzeichnis

- [Voraussetzungen](#voraussetzungen)
- [Installation](#installation)
- [Projektstruktur](#projektstruktur)
- [Konfiguration](#konfiguration)
- [Verwendung](#verwendung)
  - [Wasserzeichen einbetten](#wasserzeichen-einbetten)
  - [Wasserzeichen nachweisen](#wasserzeichen-nachweisen)
- [Testing](#testing)
- [Erweiterungsmöglichkeiten](#erweiterungsmöglichkeiten)
- [FAQ](#faq)
- [Glossar](#glossar)
- [Lizenz](#lizenz)
- [Kontakt](#kontakt)

---

## Voraussetzungen

- **Python Version:** 3.12 oder höher
- **Benötigte Python-Pakete:**
  - [PyYAML](https://pypi.org/project/PyYAML/) – zum Laden der YAML-Konfiguration
  - [astor](https://pypi.org/project/astor/) – zur Rückkonvertierung des modifizierten AST in Quellcode
  - [PyCryptodome](https://pypi.org/project/pycryptodome/) – für AES-Verschlüsselung (EAX-Modus)
  - [cryptography](https://cryptography.io/de/latest/) – zur Implementierung des Key Vault (Fernet)
  - (Optional) [reedsolo](https://pypi.org/project/reedsolo/) – für den Reed-Solomon-Fehlerkorrekturcode

Stelle sicher, dass alle benötigten Pakete installiert sind.

---

## Installation

1. **Virtuelle Umgebung erstellen (optional, aber empfohlen):**

   ```bash
   python -m venv venv
   # Linux/macOS:
   source venv/bin/activate
   # Windows:
   venv\Scripts\activate
   ```

2. **Abhängigkeiten installieren:**

   ```bash
   pip install PyYAML astor pycryptodome cryptography
   ```
   
   Für die optionale Reed-Solomon-Unterstützung:
   
   ```bash
   pip install reedsolo
   ```

3. **Projektdateien herunterladen oder klonen:**

   Sorge dafür, dass im Projektverzeichnis folgende Dateien und Ordner vorhanden sind:

   ```
   projectwatermark/
   ├── config.yaml
   ├── file_to_transform.py
   ├── file_transformed.py           # Wird nach der Transformation erzeugt
   ├── generate_whitelist.py
   ├── key_vault.py
   ├── plugin_manager.py
   ├── plugins/
   │   └── sample_plugin.py
   ├── robustness_tests.py
   ├── test_watermark.py
   ├── watermark_detector.py
   ├── watermark_embedder.py
   ├── error_correction.py
   └── main.py
   ```

---

## Projektstruktur

- **config.yaml:**  
  Enthält sämtliche Einstellungen für das Wasserzeichen-System, inklusive Projektinformationen, Verschlüsselungsoptionen, Fehlerkorrektur-Methode (Hamming oder Reed-Solomon), Plugin-Einstellungen und Parameter für das Key Vault.

- **file_to_transform.py:**  
  Eine Beispiel-Python-Datei, die als Eingabe für den Einbettungsprozess dient.

- **file_transformed.py:**  
  Die Ausgabedatei, in der der transformierte Quellcode gespeichert wird.

- **generate_whitelist.py:**  
  Ein Skript zur automatischen Generierung einer Whitelist (im JSON-Format) basierend auf dem AST des Zielcodes. Diese Liste enthält kritische Variablen und Funktionen, die für die Wasserzeichen-Einbettung vorgesehen sind.

- **key_vault.py:**  
  Implementiert ein einfaches Key Vault zur sicheren Speicherung von Verschlüsselungsschlüsseln mittels Fernet (cryptography).  
  *Hinweis:* Der Master-Key muss über die Umgebungsvariable `KEY_VAULT_MASTER` bereitgestellt werden.

- **error_correction.py:**  
  Enthält die Implementierung alternativer Fehlerkorrekturcodes: Hamming(7,4)-Code und Reed-Solomon-Code (via reedsolo).

- **plugin_manager.py:**  
  Lädt alle Plugins aus dem Verzeichnis `plugins` und wendet sie auf den AST an. Jedes Plugin muss eine Funktion `apply(ast_tree: ast.AST) -> ast.AST` implementieren.

- **plugins/sample_plugin.py:**  
  Ein Beispiel-Plugin, das jedem Funktionsnamen ein Präfix `prod_` hinzufügt, um zu demonstrieren, wie eigene Plugins integriert werden können.

- **watermark_embedder.py:**  
  Implementiert den Einbettungsprozess des Wasserzeichens. Neben AST-Manipulation, Fehlerkorrektur und AES-Verschlüsselung werden hier auch Plugins angewendet. Der interaktive Review-Modus zeigt alle vorgenommenen Änderungen an.

- **watermark_detector.py:**  
  Dient zur Überprüfung, ob ein eingebettetes Wasserzeichen im Quellcode vorhanden ist. Es extrahiert Wasserzeichen-Bits aus dem AST, wendet die Fehlerkorrektur an und vergleicht das Ergebnis mit dem erwarteten Wasserzeichen.

- **robustness_tests.py:**  
  Führt Robustheitstests durch, indem der transformierte Code zusätzlichen Transformationen (z. B. Minifizierung, Obfuskation) unterzogen wird und anschließend die Erkennung des Wasserzeichens geprüft wird.

- **test_watermark.py:**  
  Enthält Unit-Tests zur Überprüfung der Funktionalität des gesamten Systems.

- **main.py:**  
  Der Haupteinstiegspunkt des Systems. Über die Kommandozeile kann zwischen Einbettung (`embed`) und Erkennung (`detect`) gewählt werden. Zudem werden hier Konfiguration, Key Vault und Plugin-Management initialisiert.

---

## Konfiguration

### config.yaml

Diese Datei enthält alle grundlegenden Einstellungen:

- **projektname, copyright, uuid:**  
  Basisinformationen für die Generierung des Master-Wasserzeichens.

- **encryption_key_embedder & encryption_key_detector:**  
  Schlüssel zur Verschlüsselung bzw. Entschlüsselung. Werden bevorzugt aus dem Key Vault geladen, falls dieser initialisiert werden kann.

- **error_correction:**  
  Wähle den Fehlerkorrekturalgorithmus: `"hamming"` oder `"reed-solomon"`.

- **random_bit_assignment:**  
  (Boolean) Legt fest, ob die Bit-Zuordnung zufällig erfolgen soll.

- **alternate_naming:**  
  (Boolean) Bei Bit '1' wird zufällig zwischen camelCase und PascalCase gewählt, ggf. mit zufälligen Präfixen/Suffixen.

- **mapping:**  
  Dokumentation der Namenskonventionen und Code-Strukturen, die intern genutzt werden.

---

## Verwendung

Unser System wird über die Kommandozeile gesteuert. Der Einstiegspunkt ist `main.py`.

### Wasserzeichen einbetten

1. **Key Vault konfigurieren (optional):**  
   Stelle sicher, dass die Umgebungsvariable `KEY_VAULT_MASTER` gesetzt ist oder die Schlüssel in der `config.yaml` hinterlegt sind.

2. **Einbettung starten:**  
   Führe den folgenden Befehl aus, um das Wasserzeichen in die Datei `file_to_transform.py` einzubetten:

   ```bash
   python main.py embed file_to_transform.py
   ```

   Dabei werden folgende Schritte ausgeführt:
   - Laden der Konfiguration, Whitelist und ggf. Schlüssel aus dem Key Vault.
   - Generierung des Master-Wasserzeichens inkl. Fehlerkorrektur (Hamming oder Reed-Solomon) und AES-Verschlüsselung.
   - Anwendung von Plugins auf den AST (z. B. zusätzliche Namensänderungen).
   - Transformierung des Codes mit interaktivem Review-Modus (Bestätigung erforderlich).
   - Speicherung des transformierten Codes in `file_transformed.py`.

### Wasserzeichen nachweisen

Um zu überprüfen, ob der transformierte Code das eingebettete Wasserzeichen enthält, verwende:

```bash
python main.py detect file_transformed.py
```

Das Programm:
- Lädt die Konfiguration und Whitelist.
- Generiert das erwartete Wasserzeichen (entsprechend der Fehlerkorrektur- und Verschlüsselungseinstellungen).
- Parst den Zielcode, extrahiert die Wasserzeichen-Bits und wendet die Dekodierung an.
- Vergleicht das extrahierte Muster mit dem erwarteten und gibt eine Erfolgs- oder Warnmeldung aus.

---

## Testing

- **Unit-Tests:**  
  Führe `python test_watermark.py` aus, um die Funktionalität (Wasserzeichengenerierung, Transformation, Codeausführung) zu testen.

- **Robustheitstests:**  
  Das Skript `robustness_tests.py` simuliert zusätzliche Transformationen (z. B. Minifizierung) und führt anschließend den Erkennungsprozess aus, um die Stabilität des Wasserzeichens zu überprüfen.

---

## Erweiterungsmöglichkeiten

- **Weitere Plugins:**  
  Entwickle eigene Plugins, um zusätzliche Code-Transformationen oder Obfuskationstechniken einzubinden.

- **Alternative Fehlerkorrekturverfahren:**  
  Neben Hamming und Reed-Solomon können weitere Algorithmen integriert werden.

- **Verbessertes Key Management:**  
  Für den produktiven Einsatz empfiehlt sich die Integration eines professionellen Key Management Systems oder Hardware Security Modules (HSM).

- **Integration in CI/CD-Pipelines:**  
  Automatisiere den Einbettungs- und Erkennungsprozess als Teil von Build- oder Deployment-Pipelines.

---

## FAQ

**Q1: Was macht das Plugin-System?**  
A1: Das Plugin-System lädt externe Module aus dem `plugins`-Verzeichnis, die den AST zusätzlich transformieren können – beispielsweise durch das Hinzufügen von Präfixen zu Funktionsnamen.

**Q2: Wie funktioniert die Fehlerkorrektur?**  
A2: Je nach Konfiguration wird entweder der Hamming(7,4)-Code oder der Reed-Solomon-Code verwendet, um das Wasserzeichen robust gegen kleine Veränderungen im Code zu machen.

**Q3: Was ist das Key Vault?**  
A3: Das Key Vault speichert Verschlüsselungsschlüssel sicher in einer verschlüsselten Datei. Der Master-Key, der zur Entschlüsselung benötigt wird, muss über die Umgebungsvariable `KEY_VAULT_MASTER` bereitgestellt werden.

**Q4: Kann ich den Einbettungsprozess automatisieren?**  
A4: Ja, durch den modularen Aufbau und den Kommandozeilen-Einstiegspunkt (`main.py`) lässt sich das System gut in automatisierte Pipelines integrieren.

---

## Glossar

- **AST (Abstract Syntax Tree):**  
  Eine baumartige Darstellung des Quellcodes, die dessen syntaktische Struktur wiedergibt und zur Analyse sowie Transformation verwendet wird.

- **Wasserzeichen:**  
  Eine versteckte, binäre Information, die zur Kennzeichnung des geistigen Eigentums in den Quellcode eingebettet wird.

- **Hamming-Code & Reed-Solomon-Code:**  
  Fehlerkorrekturcodes, die helfen, kleinere Änderungen oder Fehler im eingebetteten Wasserzeichen zu erkennen und zu korrigieren.

- **Key Vault:**  
  Ein Modul zur sicheren Speicherung von Schlüsseln, hier implementiert mittels Fernet-Verschlüsselung.

- **Plugin-System:**  
  Eine Architektur, die es ermöglicht, externe Module (Plugins) dynamisch in den Transformationsprozess einzubinden.

---

## Lizenz

Dieses Projekt steht unter der GNU General Public License v3.0. Für den produktiven Einsatz sollten zusätzliche rechtliche und technische Prüfungen erfolgen.

---

## Kontakt

Bei Fragen, Anregungen oder Feedback zur Weiterentwicklung dieses Systems kannst Du Dich gerne per E-Mail oder über die Projektseite melden.
