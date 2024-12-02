
# School PC Checker (SPC)

School PC Checker (SPC) ist ein Konsolenprogramm, mit dem die Hardwareanforderungen von PCs für Schulzwecke überprüft werden können. Das Programm testet, ob ein PC für verschiedene Anforderungen geeignet ist, und speichert die Ergebnisse in einer JSON-Datei (`spc_results.json`).

## Features
- Überprüft:
  - CPU-Kerne
  - Arbeitsspeicher (RAM)
  - Freien Speicherplatz
  - GPU (Grafikkarte) und Videospeicher (VRAM)
- Speichert die Ergebnisse:
  - Raum, Reihe und Platznummer
  - Testergebnisse (geeignet/nicht geeignet)
  - Zeitstempel
  - Systeminformationen
- Ausgabe in der Konsole und JSON-Datei

## Anforderungen
- Python 3.8 oder höher
- Betriebssystem: Windows
- Benötigte Python-Bibliotheken:
  - `altgraph==0.17.4`
  - `packaging==24.2`
  - `pefile==2023.2.7`
  - `psutil==6.1.0`
  - `py3nvml==0.2.7`
  - `pyinstaller==6.11.1`
  - `pyinstaller-hooks-contrib==2024.10`
  - `pywin32==308`
  - `pywin32-ctypes==0.2.3`
  - `setuptools==75.6.0`
  - `WMI==1.5.1`
  - `xmltodict==0.14.2`


## Installation
1. **Python installieren**: Stelle sicher, dass Python 3.8 oder höher installiert ist.
2. **Benötigte Bibliotheken installieren**:
   ```bash
   pip install psutil wmi
   ```
3. **Das Skript ausführen**:
   ```bash
   python SPC.py
   ```

## Bedienung
1. Starte das Skript:
   ```bash
   python SPC.py
   ```
2. Gib die folgenden Informationen ein:
   - Raum (z. B. `B1.11`)
   - Reihe (z. B. `1`)
   - Platznummer (z. B. `1`)
3. Das Programm zeigt die Testergebnisse in der Konsole an und speichert sie in der JSON-Datei `spc_results.json`.

## Beispiele
### Konsolenausgabe
```
--- Testergebnisse ---

Raum: 1, Reihe: 1, Platz: 1
Testergebnis: Geeignet
Zeitstempel: 2024-12-02 03:43:10
Details: PC erfüllt alle Anforderungen

Systeminfo:
  Betriebssystem: Windows 10 Pro Professional
  Version: 10.0.22635
  Prozessor: 13th Gen Intel(R) Core(TM) i7-13700K @ 3.40 GHz
  Arbeitsspeicher: 32 GB
  Freier Speicherplatz: 367 GB
  GPUs:
    NVIDIA GeForce RTX 3080 mit 10 GB VRAM (Treiberversion: 32.0.15.6614)
```

### JSON-Ausgabe
Die Ergebnisse werden in der Datei `spc_results.json` gespeichert:
```json
{
    "B1.11_Reihe1_Platz1": {
        "Raum": "B1.11",
        "Reihe": "1",
        "Platz": "1",
        "Testergebnis": "Geeignet",
        "Details": "PC erfüllt alle Anforderungen",
        "Zeitstempel": "2024-12-02 12:45:00",
        "Systeminfo": {
            "Betriebssystem": "Windows 10 Pro Professional",
            "Version": "10.0.22635",
            "Prozessor": "13th Gen Intel(R) Core(TM) i7-13700K @ 3.40 GHz",
            "Arbeitsspeicher": 32,
            "Freier Speicherplatz": 367,
            "GPUs": [
                {
                    "Name": "NVIDIA GeForce RTX 3080",
                    "VRAM": 10,
                    "Treiberversion": "32.0.15.6614"
                }
            ]
        }
    }
}
```

## Erstellung einer `.exe`-Datei
1. Installiere `pyinstaller`:
   ```bash
   pip install pyinstaller
   ```
2. Erstelle die `.exe`:
   ```bash
   pyinstaller --onefile SPC.py
   ```
3. Die `.exe`-Datei wird im Ordner `dist` gespeichert.

## Lizenz
> Dieses Projekt steht unter der MIT-Lizenz. Weitere Details finden sich in der [LICENSE](LICENSE.md) Datei.
