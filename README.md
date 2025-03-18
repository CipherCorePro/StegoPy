# Wasserzeichen-Einbettung in Python-Code

Dieses Projekt stellt einen Proof-of-Concept dar, um „unsichtbare“ Wasserzeichen in Python-Code mittels AST-Manipulation einzubetten. Ziel ist es, den Schutz geistigen Eigentums in Open-Source-Projekten zu erhöhen, indem versteckte Informationen (wie Projektname, Copyright-Jahr und UUID)
im Quellcode verteilt werden. Dabei wird die Wasserzeicheninformation als Binärstring erzeugt und anhand ausgewählter Code-Elemente (z. B. Variablen-/Funktionsnamen und Schleifen) im Code verankert.

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

3. **Projektdateien herunterladen oder klonen:**

   Stelle sicher, dass folgende Dateien im Projektverzeichnis vorhanden sind:
   - `config.yaml`
   - `whitelist.json`
   - `watermark_embedder.py`
   - `file_to_transform.py`
   - `watermark_detector.py`
   - `test_watermark.py`

---

## Projektstruktur

- **config.yaml:**  
  Enthält die Konfiguration für das Wasserzeichen-Schema, wie z. B. Projektname, Copyright-
  Jahr, UUID und das Mapping (z. B. wie ein Bit in eine bestimmte Änderung übersetzt wird).

- **whitelist.json:**  
  Definiert eine Liste von Variablen und Code-Abschnitten, die für die Einbettung des Wasserzeichens geeignet sind.  
  Jede Eintragung enthält zusätzliche Informationen (z. B. Zeilennummer, Code-Kontext und Gründe für die Aufnahme).

- **watermark_embedder.py:**  
  Das Hauptmodul, das den Wasserzeicheneinbettungsprozess mittels AST-Manipulation implementiert.  
  Es liest die Konfigurations- und Whitelist-Dateien ein, generiert das Master-Wasserzeichen und transformiert den Quellcode.

- **file_to_transform.py:**  
  Eine Beispiel-Python-Datei, die als Eingabedatei für den Transformationsprozess dient.  
  Hier wird das Wasserzeichen eingebettet.

- **file_transformed.py:**  
  Die Ausgabedatei, in der der transformierte Code nach erfolgreicher Einbettung gespeichert wird.

- **watermark_detector.py:**  
  Ein zusätzliches Modul, das den transformierten Code analysiert, um das eingebettete Wasserzeichen
  zu extrahieren und zu verifizieren. Mithilfe von AST-Analyse wird festgestellt, ob der Code Dein Wasserzeichen enthält.

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
   Stelle sicher, dass die Dateien `config.yaml` und `whitelist.json` korrekt konfiguriert sind und alle benötigten Informationen enthalten.

2. **Eingabedatei bearbeiten:**  
   Passe ggf. die Datei `file_to_transform.py` an, um den Code zu repräsentieren, in den das Wasserzeichen eingebettet werden soll.

3. **Transformation starten:**  
   Führe das Hauptmodul `watermark_embedder.py` aus:

   ```bash
   python watermark_embedder.py
   ```

   Dabei werden folgende Schritte durchgeführt:
   - Die Konfigurations- und Whitelist-Dateien werden geladen.
   - Ein Master-Wasserzeichen wird als Binärstring generiert.
   - Der AST des Quellcodes in `file_to_transform.py` wird analysiert.
   - Basierend auf den Wasserzeichenbits werden die ausgewählten Variablen-/Funktionsnamen und Code-Strukturen transformiert.
   - Der transformierte Code wird in `file_transformed.py` gespeichert.

4. **Ergebnis überprüfen:**  
   Öffne `file_transformed.py`, um die vorgenommenen Änderungen zu inspizieren. Achte darauf, dass die Funktionalität erhalten bleibt und das Wasserzeichen gemäß den definierten Regeln eingebettet wurde.

### Wasserzeichen nachweisen

Um zu überprüfen, ob der transformierte Code Dein eingebettetes Wasserzeichen enthält, verwende das Skript `watermark_detector.py`:

1. **Detektor ausführen:**  
   Führe das Detektorskript mit der zu prüfenden Datei (z. B. `file_transformed.py`) aus:

   ```bash
   python watermark_detector.py file_transformed.py
   ```

2. **Funktionsweise:**  
   Das Skript:
   - Lädt die Konfiguration (`config.yaml`) und die Whitelist (`whitelist.json`).
   - Generiert das vollständige Wasserzeichen als Binärstring.
   - Parst den Quellcode der angegebenen Datei und extrahiert anhand der in der Whitelist definierten Namen die angewendeten Wasserzeichen-Bits.
   - Vergleicht das extrahierte Bitmuster (Prefix) mit dem erwarteten Muster.
   - Gibt eine Meldung aus, ob das Wasserzeichen im Code gefunden wurde oder nicht.

---

## Testing

Um sicherzustellen, dass der Wasserzeicheneinbettungsprozess korrekt funktioniert, führe die Unit-Tests aus:

```bash
python test_watermark.py
```
![image](https://github.com/user-attachments/assets/8dcccab8-d432-48f2-a3e8-e278ddd94335)

Die Tests überprüfen:
- Die korrekte Generierung des Master-Wasserzeichens.
- Die fehlerfreie Transformation des Quellcodes.
- Die Ausführbarkeit des transformierten Codes.

---

## Erweiterungsmöglichkeiten

- **Dynamische Whitelists:**  
  Integration eines Skripts, das automatisch geeignete Variablen und Code-Abschnitte anhand des AST und kontextabhängiger Kriterien auswählt.

- **Robustheitstests:**  
  Automatisierte Tests, die den transformierten Code nach verschiedenen Transformationen (z. B. Minifizierung oder Refactoring) erneut überprüfen.

- **Erweiterte Transformationen:**  
  Zusätzliche Möglichkeiten der Code-Transformation, wie z. B. die Integration von Fehlerkorrekturcodes oder die Verschlüsselung des Wasserzeichens.

- **Review-Modus:**  
  Ein interaktiver Modus, der dem Benutzer ermöglicht, die automatisch generierten Änderungen vor der endgültigen Übernahme zu überprüfen und anzupassen.

- **Erweiterter Wasserzeichennachweis:**  
  Verbesserung des Detektors, um robustere und umfangreichere Wasserzeichen-Metriken (z. B. Robustheit gegenüber Code-Transformationen) zu implementieren.

---

## Lizenz

Dieses Projekt ist als Proof-of-Concept konzipiert. Für den produktiven Einsatz oder die kommerzielle Nutzung sollten weitere rechtliche und technische Aspekte berücksichtigt werden. Bitte beachte, dass das Projekt unter [Lizenzname, z. B. MIT Lizenz] steht, sofern nicht anders angegeben.

---

## Kontakt

Bei Fragen oder Anregungen zur Weiterentwicklung dieses Projekts kannst Du Dich gerne an uns wenden.

