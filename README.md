# Wasserzeichen-Einbettung in Python-Code

Dieses Projekt stellt einen Proof-of-Concept dar, um „unsichtbare“ Wasserzeichen in Python-Code mittels AST-Manipulation einzubetten. Ziel ist es, den Schutz geistigen Eigentums in Open-Source-Projekten zu erhöhen, indem versteckte Informationen (wie Projektname, Copyright-
Jahr und UUID) im Quellcode verteilt werden. Die Wasserzeicheninformation wird als Binärstring erzeugt und anhand ausgewählter Code-Elemente (z. B. Variablen-/Funktionsnamen, Schleifen) im Code verankert.

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
- [Lizenz](#lizenz)
- [Kontakt](#kontakt)

---

## Voraussetzungen

- **Python Version:** 3.12 oder höher
- **Benötigte Python-Pakete:**
  - [PyYAML](https://pypi.org/project/PyYAML/) (zum Laden der YAML-Konfigurationsdatei)
  - [astor](https://pypi.org/project/astor/) (zur Rückkonvertierung des modifizierten AST in Quellcode)
  - (Optional für erweiterte Transformationen) [PyCryptodome](https://pypi.org/project/pycryptodome/)

Stelle sicher, dass diese Pakete in Deiner Umgebung installiert sind.

---

## Installation

1. **Virtuelle Umgebung erstellen (optional, aber empfohlen):**

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/macOS
   venv\Scripts\activate      # Windows
   ```

2. **Abhängigkeiten installieren:**

   ```bash
   pip install PyYAML astor
   ```
   
   Für Verschlüsselungsfunktionen (optional):
   
   ```bash
   pip install pycryptodome
   ```

3. **Projektdateien herunterladen oder klonen:**

   Stelle sicher, dass folgende Dateien im Projektverzeichnis vorhanden sind:
   - `config.yaml`
   - `whitelist.json`
   - `file_to_transform.py`
   - `watermark_embedder.py`
   - `watermark_detector.py`
   - `generate_whitelist.py`
   - `robustness_tests.py`
   - `test_watermark.py`

---

## Projektstruktur

- **config.yaml:**  
  Enthält die Konfiguration für das Wasserzeichen-Schema, z. B. Projektname, Copyright-
  Jahr, UUID sowie das Mapping (wie ein Bit in eine bestimmte Änderung übersetzt wird).

- **whitelist.json:**  
  Definiert eine Liste von Variablen und Code-Abschnitten, die für die Einbettung des Wasserzeichens geeignet sind. Jede Eintragung enthält zusätzliche Informationen (z. B. Zeilennummer, Kontext, Gründe für die Aufnahme).

- **file_to_transform.py:**  
  Eine Beispiel-Python-Datei, die als Eingabedatei für den Transformationsprozess dient. Hier wird das Wasserzeichen eingebettet.

- **file_transformed.py:**  
  Die Ausgabedatei, in der der transformierte Code nach erfolgreicher Einbettung gespeichert wird.

- **watermark_embedder.py:**  
  Das Hauptmodul, das den Wasserzeicheneinbettungsprozess mittels AST-Manipulation implementiert. Diese Version umfasst auch:
  - Einen interaktiven Review-Modus, der die vorgenommenen Änderungen anzeigt und eine Bestätigung einholt.
  - Platzhalter für Fehlerkorrektur (z. B. Hamming-Code) und Verschlüsselung.

- **watermark_detector.py:**  
  Ein Modul zur Überprüfung eines Python-Quellcodes auf das eingebettete Wasserzeichen. Es extrahiert mithilfe von AST die Wasserzeichen-Bits und berechnet Robustheitsmetriken, um den Nachweis zu erbringen.

- **generate_whitelist.py:**  
  Ein Skript zur automatischen Generierung einer dynamischen Whitelist anhand des AST und kontextabhängiger Kriterien. Die generierte Whitelist wird im JSON-Format ausgegeben.

- **robustness_tests.py:**  
  Ein Skript, das den transformierten Code zusätzlichen Transformationen (z. B. Minifizierung) unterzieht und anschließend den Wasserzeichennachweis ausführt, um die Robustheit des eingebetteten Wasserzeichens zu überprüfen.

- **test_watermark.py:**  
  Enthält Unit-Tests zur Überprüfung der Funktionalität des Wasserzeicheneinbetters.

---

## Konfiguration

### config.yaml

Diese Datei enthält alle grundlegenden Einstellungen für das Wasserzeichen:

- **projektname:**  
  Der Name des Projekts (z. B. "MySecretProject").

- **copyright:**
  - **jahr:**  
    Das Jahr, in dem das Copyright beansprucht wird (z. B. 2023).

- **uuid:**  
  Eine eindeutige UUID, die den Codezweig identifiziert.

- **mapping:**  
  Definiert, wie Bits (0 oder 1) in Änderungen übersetzt werden:
  - **variable_namen:**  
    - Bit "0": Beibehaltung (snake_case)  
    - Bit "1": Umwandlung in camelCase
  - **code_struktur:**  
    - Bit "0": Verwendung einer klassischen for-Schleife  
    - Bit "1": Verwendung einer List Comprehension

### whitelist.json

Diese Datei enthält Listen von Variablen und Code-Abschnitten, die für die Einbettung zugelassen sind. Jede Eintragung umfasst:
- Den Namen der Variablen oder den Typ des Code-Abschnitts.
- Zusätzliche Informationen wie Zeilennummer, Kontext und Begründung für die Inklusion.

---

## Verwendung

### Wasserzeichen einbetten

1. **Vorbereitung:**  
   Stelle sicher, dass `config.yaml` und `whitelist.json` korrekt konfiguriert sind.

2. **Eingabedatei bearbeiten:**  
   Passe gegebenenfalls `file_to_transform.py` an, um den Zielcode für das Wasserzeichen festzulegen.

3. **Transformation starten:**  
   Führe `watermark_embedder.py` aus:

   ```bash
   python watermark_embedder.py
   ```

   Dabei werden folgende Schritte durchgeführt:
   - Laden der Konfiguration und Whitelist.
   - Generierung des Master-Wasserzeichens als Binärstring.
   - Analyse des AST von `file_to_transform.py`.
   - Transformation ausgewählter Variablen-/Funktionsnamen und Code-Strukturen basierend auf den Wasserzeichenbits.
   - (Im Review-Modus) Anzeige der vorgenommenen Änderungen zur interaktiven Bestätigung.
   - Speicherung des transformierten Codes in `file_transformed.py`.

4. **Ergebnis überprüfen:**  
   Öffne `file_transformed.py` und verifiziere, dass die Funktionalität erhalten bleibt und das Wasserzeichen eingebettet wurde.

### Wasserzeichen nachweisen

Um zu überprüfen, ob der Code Dein eingebettetes Wasserzeichen enthält, führe `watermark_detector.py` aus:

```bash
python watermark_detector.py file_transformed.py
```

Das Skript:
- Lädt die Konfiguration und Whitelist.
- Generiert das erwartete Wasserzeichen.
- Parst den Zielcode und extrahiert die eingebetteten Wasserzeichen-Bits.
- Vergleicht das extrahierte Bitmuster mit dem erwarteten und gibt einen Nachweis bzw. Robustheitsmetriken aus.

---

## Testing

Führe die Unit-Tests aus, um die Funktionalität des Wasserzeicheneinbettungsprozesses sicherzustellen:

```bash
python test_watermark.py
```
![image](https://github.com/user-attachments/assets/38aa533d-9004-47b4-9568-efa37341f5fa)

Die Tests überprüfen:
- Die korrekte Generierung des Master-Wasserzeichens.
- Die fehlerfreie Transformation des Quellcodes.
- Die Ausführbarkeit des transformierten Codes.

---

## Erweiterungsmöglichkeiten

Dieses Projekt bietet folgende Erweiterungsmöglichkeiten, die schrittweise integriert werden können:

- **Dynamische Whitelists:**  
  Ein Skript (`generate_whitelist.py`) generiert automatisch eine Whitelist basierend auf dem AST und kontextabhängigen Kriterien.

- **Robustheitstests:**  
  Ein Skript (`robustness_tests.py`) unterzieht den transformierten Code weiteren Transformationen (z. B. Minifizierung) und führt anschließend den Wasserzeichennachweis aus, um die Robustheit zu evaluieren.

- **Erweiterte Transformationen:**  
  Zusätzliche Code-Transformationen (z. B. Integration von Fehlerkorrekturcodes oder Verschlüsselung des Wasserzeichens) können implementiert werden – Platzhalterfunktionen sind bereits vorhanden.

- **Review-Modus:**  
  Der interaktive Modus in `watermark_embedder.py` zeigt alle vorgenommenen Änderungen an und fragt vor dem endgültigen Speichern nach einer Bestätigung durch den Benutzer.

- **Erweiterter Wasserzeichennachweis:**  
  `watermark_detector.py` wurde erweitert, um nicht nur das Bitmuster zu extrahieren, sondern auch Robustheitsmetriken (z. B. prozentuale Übereinstimmung) zu berechnen und auszugeben.

---

## Lizenz

Dieses Projekt ist als Proof-of-Concept konzipiert. Für den produktiven Einsatz oder die kommerzielle Nutzung sollten weitere rechtliche und technische Aspekte berücksichtigt werden. Bitte beachte, dass das Projekt unter [Lizenzname, z. B. MIT Lizenz] steht, sofern nicht anders angegeben.

---

## Kontakt

Bei Fragen oder Anregungen zur Weiterentwicklung dieses Projekts kannst Du Dich gerne an uns wenden.


