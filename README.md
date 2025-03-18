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
- [FAQ](#faq)
- [Glossar](#glossar)
- [Lizenz](#lizenz)
- [Kontakt](#kontakt)

---

## Voraussetzungen

- **Python Version:** 3.12 oder höher  
- **Benötigte Python-Pakete:**
  - [PyYAML](https://pypi.org/project/PyYAML/) (zum Laden der YAML-Konfigurationsdatei)
  - [astor](https://pypi.org/project/astor/) (zur Rückkonvertierung des modifizierten AST in Quellcode)
  - (Optional, für erweiterte Transformationen) [PyCryptodome](https://pypi.org/project/pycryptodome/)

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
   
   Für optionale Verschlüsselungsfunktionen:
   
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
  - Erweiterte Transformationen mit integrierter Fehlerkorrektur (Hamming-Code) und AES-Verschlüsselung (sofern konfiguriert).

- **watermark_detector.py:**  
  Ein Modul zur Überprüfung eines Python-Quellcodes auf das eingebettete Wasserzeichen. Es extrahiert mithilfe von AST die Wasserzeichen-Bits, berechnet Robustheitsmetriken und entschlüsselt das Wasserzeichen (falls verschlüsselt).

- **generate_whitelist.py:**  
  Ein Skript zur automatischen Generierung einer dynamischen Whitelist anhand des AST und kontextabhängiger Kriterien. Die generierte Whitelist wird im JSON-Format ausgegeben.

- **robustness_tests.py:**  
  Ein Skript, das den transformierten Code zusätzlichen Transformationen (z. B. Minifizierung) unterzieht und anschließend den Wasserzeichennachweis ausführt, um die Robustheit des eingebetteten Wasserzeichens zu überprüfen.

- **test_watermark.py:**  
  Enthält Unit-Tests zur Überprüfung der Funktionalität des Wasserzeicheneinbettungsprozesses.

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

- **encryption_key:**  
  (Optional) Ein Schlüssel zur Verschlüsselung des Wasserzeichens.

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
   - Generierung des Master-Wasserzeichens als Binärstring (mit Hamming-Code und optionaler AES-Verschlüsselung).
   - Analyse des AST von `file_to_transform.py`.
   - Transformation ausgewählter Variablen-/Funktionsnamen und Code-Strukturen basierend auf den Wasserzeichenbits.
   - **Im Review-Modus** werden alle vorgenommenen Änderungen interaktiv angezeigt – eine Bestätigung ist erforderlich, bevor der transformierte Code in `file_transformed.py` gespeichert wird.

4. **Ergebnis überprüfen:**  
   Öffne `file_transformed.py` und verifiziere, dass die Funktionalität erhalten bleibt und das Wasserzeichen eingebettet wurde.

### Wasserzeichen nachweisen

Um zu überprüfen, ob der Code Dein eingebettetes Wasserzeichen enthält, führe `watermark_detector.py` aus:

```bash
python watermark_detector.py file_transformed.py
```

Das Skript:
- Lädt die Konfiguration und Whitelist.
- Generiert das erwartete Wasserzeichen (und entschlüsselt es bei Bedarf).
- Parst den Zielcode und extrahiert die eingebetteten Wasserzeichen-Bits.
- Vergleicht das extrahierte Bitmuster mit dem erwarteten und gibt einen Nachweis sowie Robustheitsmetriken aus.

---

## Testing

Führe die Unit-Tests aus, um die Funktionalität des Wasserzeicheneinbettungsprozesses sicherzustellen:

```bash
python test_watermark.py
```

Die Tests überprüfen:
- Die korrekte Generierung des Master-Wasserzeichens.
- Die fehlerfreie Transformation des Quellcodes.
- Die Ausführbarkeit des transformierten Codes.

---

## FAQ

**Q1: Was ist ein Wasserzeichen in diesem Kontext?**  
A1: Ein Wasserzeichen ist eine versteckte, binäre Information, die in den Quellcode eingebettet wird, um Urheberschaft und den Schutz geistigen Eigentums nachweisen zu können.

**Q2: Wie wird das Wasserzeichen eingebettet?**  
A2: Das Wasserzeichen wird aus Konfigurationsdaten (Projektname, Jahr, UUID) als Binärstring generiert. Anschließend wird es mithilfe von AST-Manipulation in ausgewählte Code-Elemente (z. B. Variablennamen, Funktionen, Schleifen) eingebettet – dabei kommen auch Fehlerkorrektur (Hamming-Code) und Verschlüsselung (AES) zum Einsatz.

**Q3: Was ist der Review-Modus?**  
A3: Im Review-Modus zeigt das Programm alle vorgenommenen Änderungen (z. B. Umbenennungen) an und fragt interaktiv nach einer Bestätigung, bevor der transformierte Code gespeichert wird.

**Q4: Wie kann ich überprüfen, ob mein Wasserzeichen erhalten geblieben ist?**  
A4: Mit dem Modul `watermark_detector.py` lässt sich der transformierte Code parsen, die eingebetteten Bits extrahieren und mit dem erwarteten Wasserzeichen vergleichen. Zusätzlich werden Robustheitsmetriken berechnet.

**Q5: Was passiert, wenn der Wasserzeichennachweis nur teilweise erfolgreich ist?**  
A5: Falls nur ein Teil des Wasserzeichens erkannt wird, wird der Prozentsatz der Übereinstimmung ausgegeben, sodass sich die Robustheit des eingebetteten Wasserzeichens bewerten lässt.

---

## Glossar

- **AST (Abstract Syntax Tree):**  
  Eine baumartige Darstellung des Quellcodes, die die syntaktische Struktur eines Programms beschreibt. Wird verwendet, um Code zu analysieren und zu transformieren.

- **Wasserzeichen:**  
  Eine versteckte Information, die in den Quellcode eingebettet wird, um Urheberrechte nachweisen zu können.

- **Hamming-Code:**  
  Ein Fehlerkorrekturcode, der durch Hinzufügen von Paritätsbits die Erkennung und Korrektur von Fehlern im Bitstrom ermöglicht.

- **AES-Verschlüsselung:**  
  Ein weit verbreiteter symmetrischer Verschlüsselungsalgorithmus, der hier genutzt wird, um das Wasserzeichen zu schützen.

- **Review-Modus:**  
  Ein interaktiver Modus, in dem die vorgenommenen Änderungen am Code angezeigt werden und eine Bestätigung durch den Benutzer erforderlich ist, bevor der transformierte Code gespeichert wird.

- **Whitelist:**  
  Eine Liste von Variablen und Code-Abschnitten, die für die Wasserzeichen-Einbettung zugelassen sind.

- **Minifizierung:**  
  Ein Prozess, bei dem der Code durch Entfernen von überflüssigen Zeichen (z. B. Leerzeilen) verkleinert wird, ohne seine Funktionalität zu verändern.

---

## Lizenz

Dieses Projekt ist als Proof-of-Concept konzipiert. Für den produktiven Einsatz oder die kommerzielle Nutzung sollten weitere rechtliche und technische Aspekte berücksichtigt werden. Bitte beachte, dass das Projekt unter [Lizenzname, z. B. MIT Lizenz] steht, sofern nicht anders angegeben.

---

## Kontakt

Bei Fragen oder Anregungen zur Weiterentwicklung dieses Projekts kannst Du Dich gerne an uns wenden.

