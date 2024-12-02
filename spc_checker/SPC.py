# Import der notwendigen Module
import ctypes
import platform  # Für Systeminformationen
from datetime import datetime

import psutil  # Für Hardware-Informationen
import json  # Für das Speichern von Ergebnissen
import os  # Für Dateiprüfung
import math  # Für Rundungsfunktionen
import wmi  # Für GPU-Informationen auf Windows-Systemen (optional)
import subprocess  # Für direkten Zugriff auf GPU-Daten bei Bedarf (z. B. NVIDIA-spezifisch)
import winreg


# Mindestanforderungen für die Leistung
min_cpu_cores = 4
min_ram_gb = 16
min_free_space_gb = 100
min_gpu_gb = 4


# Funktion zum Testen der PC-Leistung
def test_pc_performance():
    """
    Testet die PC-Leistung basierend auf Prozessor, Arbeitsspeicher, freiem Speicherplatz
    und der GPU mit Videospeicher.
    Gibt True zurück, wenn der PC geeignet ist, ansonsten False.
    """
    issues = []  # Liste, um alle Probleme zu speichern

    # Prozessor-Kerne prüfen
    cpu_cores = psutil.cpu_count(logical=True)
    if cpu_cores < min_cpu_cores:
        issues.append(f"Zu wenige CPU-Kerne: PC hat nur {cpu_cores} Kerne (benötigt: {min_cpu_cores} Kerne)")

    # Arbeitsspeicher prüfen
    ram = psutil.virtual_memory()
    ram_gb = math.ceil(ram.total / (1024 ** 3))  # Aufrunden auf die nächste ganze Zahl
    if ram_gb < min_ram_gb:
        issues.append(f"Zu wenig Arbeitsspeicher: PC hat nur {ram_gb} GB (benötigt: {min_ram_gb} GB)")

    # GPU-Videospeicher prüfen
    gpus = get_gpu_details()
    for gpu in gpus:
        if gpu["VRAM"] < min_gpu_gb:
            issues.append(f"Zu wenig Videospeicher: {gpu['Name']} PC hat nur {gpu['VRAM']} GB (benötigt: {min_gpu_gb} GB)")

    # Freien Speicherplatz prüfen
    free_space_gb = int(psutil.disk_usage('/').free / (1024 ** 3))  # Ganze Zahl für freien Speicherplatz
    if free_space_gb < min_free_space_gb:
        issues.append(f"Zu wenig freier Speicherplatz: PC hat nur {free_space_gb} GB (benötigt: {min_free_space_gb} GB)")

    if issues:
        return False, issues  # Gibt False und die Liste der Probleme zurück
    return True, ["PC erfüllt alle Anforderungen"]


# Funktion, um GPU-Informationen zu sammeln
def get_gpu_details():
    """
    Liefert eine Liste mit verfügbaren GPUs, ihren Namen, VRAM (Videospeicher) in GB und Treiberversionen.
    """
    gpus = []
    try:
        # Funktioniert auf Windows-Systemen
        if platform.system() == "Windows":
            w = wmi.WMI()
            for gpu in w.Win32_VideoController():
                # VRAM wird in Bytes geliefert, also in GB umwandeln
                vram_bytes = gpu.AdapterRAM
                if vram_bytes and vram_bytes > 0:  # Überprüfen, ob AdapterRAM verfügbar und sinnvoll ist
                    vram_gb = math.ceil(float(vram_bytes) / (1024 ** 3))  # Ganze Zahl
                else:
                    vram_gb = get_vram_from_nvidia_smi(gpu.Name.strip())  # Fallback für NVIDIA

                # GPU-Treiberversion
                driver_version = gpu.DriverVersion if hasattr(gpu, "DriverVersion") else "Unbekannt"

                gpus.append({
                    "Name": gpu.Name.strip(),
                    "VRAM": vram_gb,  # Videospeicher in GB
                    "Treiberversion": driver_version  # GPU-Treiber
                })
    except ImportError:
        pass

    # Fallback für Systeme ohne WMI-Unterstützung
    if not gpus:
        gpus.append({"Name": "Keine GPU-Informationen verfügbar", "VRAM": 0, "Treiberversion": "Unbekannt"})

    return gpus


# NVIDIA-spezifischer Fallback für VRAM
def get_vram_from_nvidia_smi(gpu_name):
    """
    Versucht, den VRAM einer NVIDIA-GPU mithilfe von nvidia-smi auszulesen.
    """
    try:
        # Aufruf von nvidia-smi für Speicherinformationen
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            # Ergebnis auslesen
            vram_values = result.stdout.strip().split("\n")
            # Suche die passende GPU (einfaches Matching)
            for idx, vram in enumerate(vram_values):
                if idx == 0:  # Im einfachsten Fall, die erste GPU
                    return math.ceil(float(vram) / 1024)  # MB -> GB, Ganze Zahl
    except FileNotFoundError:
        pass
    return 0  # Fallback, wenn kein nvidia-smi verfügbar ist


# Funktion zum Laden der JSON-Datei
def load_data(filename):
    """
    Lädt Daten aus der JSON-Datei. Falls die Datei nicht existiert, wird ein leeres Dictionary zurückgegeben.
    """
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                print(f"Warnung: '{filename}' ist keine gültige JSON-Datei. Eine neue Datei wird erstellt.")
                return {}
    return {}


# Funktion zum Speichern der JSON-Daten
def save_data(filename, data):
    """
    Speichert die Daten in der JSON-Datei und sortiert die IDs aufsteigend.
    """
    # Sortiere die Daten nach den IDs der Schlüssel
    sorted_data = dict(sorted(data.items(), key=lambda x: x[0]))

    # Speichere die sortierten Daten in der JSON-Datei
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(sorted_data, file, indent=4, ensure_ascii=False)  # ensure_ascii=False für korrekte Umlaute


# Funktion, um den vollständigen CPU-Namen mit Taktfrequenz zu ermitteln
def get_cpu_details():
    """
    Liefert den CPU-Namen im Format:
    Name @ GHz
    """
    try:
        # Funktioniert auf Windows-Systemen
        if platform.system() == "Windows":
            w = wmi.WMI()
            for processor in w.Win32_Processor():
                name = processor.Name.strip()
                max_speed = float(processor.MaxClockSpeed) / 1000  # MHz -> GHz
                return f"{name} @ {max_speed:.2f} GHz"
    except ImportError:
        pass

    # Fallback für andere Betriebssysteme
    name = platform.processor()
    # Fallback für Taktfrequenz
    cpu_freq = psutil.cpu_freq().max if psutil.cpu_freq() else 0
    return f"{name} @ {cpu_freq:.2f} GHz"


# Hauptfunktion für Eingabe und Zuordnung
def get_os_details():
    """
    Ermittelt das Betriebssystem, die Hauptversion (z. B. Windows 10 oder 11)
    und die Edition (z. B. Pro oder Home).
    Funktioniert auf Windows-Systemen.
    """
    if platform.system() == "Windows":
        try:
            # Zugriff auf den Windows-Registrierungswert für die Edition
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                product_name = winreg.QueryValueEx(key, "ProductName")[0]
                edition_id = winreg.QueryValueEx(key, "EditionID")[0]
                return f"{product_name} {edition_id}"
        except Exception as e:
            return "Unbekanntes Windows-Betriebssystem"
    return platform.system()  # Für andere Betriebssysteme


def set_window_title(title):
    """
    Setzt den Fenstertitel auf Windows-Systemen.
    """
    ctypes.windll.kernel32.SetConsoleTitleW(title)

def main():
    """
    Hauptprogramm für die Eingabe von PC-Daten, Testen der Leistung
    und Speichern der Ergebnisse in einer einzigen JSON-Datei.
    """
    # Fenstertitel setzen
    set_window_title("School PC Checker - SPC")

    # Dateiname für die JSON-Datei
    filename = "spc_results.json"

    # Vorhandene Daten laden
    data = load_data(filename)

    # Eingabe von Raum, Reihe und Platznummer
    room = input("Bitte den Raum eingeben: ").strip()
    row = input("Bitte die Reihe (z. B. 1 für vorne) eingeben: ").strip()
    seat = input("Bitte die Platznummer (z. B. 1 für vom Fenster aus) eingeben: ").strip()

    # Teste die Leistung des PCs
    is_suitable, messages = test_pc_performance()

    # Systeminformationen sammeln
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Zeitstempel im Format YYYY-MM-DD HH:MM:SS

    # Systeminformationen sammeln
    ram_gb = math.ceil(psutil.virtual_memory().total / (1024 ** 3))  # Ganze Zahl
    free_space_gb = int(psutil.disk_usage('/').free / (1024 ** 3))  # Ganze Zahl für freien Speicherplatz
    gpus = get_gpu_details()

    system_info = {
        "Betriebssystem": get_os_details(),
        "Version": platform.version(),
        "Prozessor": get_cpu_details(),
        "Arbeitsspeicher": ram_gb,
        "Freier Speicherplatz": free_space_gb,
        "GPUs": gpus
    }

    # Ergebnisse in die JSON-Datei einfügen
    pc_key = f"{room}_Reihe{row}_Platz{seat}"
    data[pc_key] = {
        "Raum": room,
        "Reihe": row,
        "Platz": seat,
        "Testergebnis": "Geeignet" if is_suitable else "Nicht geeignet",
        "Details": "; ".join(messages),  # Alle Probleme zusammenfügen
        "Zeitstempel": timestamp,
        "Systeminfo": system_info
    }

    # Ergebnisse anzeigen
    print("\n--- Testergebnisse ---\n")
    print(f"Raum: {room}, Reihe: {row}, Platz: {seat}")
    print(f"Testergebnis: {'Geeignet' if is_suitable else 'Nicht geeignet'}")
    print(f"Zeitstempel: {timestamp}")
    print(f"Details: {'; '.join(messages)}")  # Details ausgeben
    print("\nSysteminfo:")
    for key, value in system_info.items():
        if key == "Betriebssystem":
            print(f"  {key}: {value}")
        elif key == "Version":
            print(f"  {key}: {value}")
        elif key == "Prozessor":
            print(f"  {key}: {value}")
        elif key == "Arbeitsspeicher":
            print(f"  {key}: {value} GB")
        elif key == "Freier Speicherplatz":
            print(f"  {key}: {value} GB")
        elif key == "GPUs":
            print("  GPUs:")
            for gpu in value:
                print(f"    {gpu['Name']} mit {gpu['VRAM']} GB VRAM (Treiberversion: {gpu['Treiberversion']})")
        else:
            print(f"  {key}: {value}")
    print("\n--- Testergebnisse ---")

    # Daten in die JSON-Datei speichern
    save_data(filename, data)
    print(f"\nErgebnisse wurden in '{filename}' aktualisiert.")


# Programmstart
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDas Programm wurde durch den Benutzer abgebrochen.")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
    finally:
        os.system("pause")