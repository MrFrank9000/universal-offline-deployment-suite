import os
import sys
import glob
import shutil
import zipfile
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    subprocess.run("python -m pip install pyserial", shell=True)
    import serial
    import serial.tools.list_ports

selected_zip_path = ""
monitor_active = False

def show_supported_devices():
    info_text = (
        "=== Supported Espressif Chips ===\n\n"
        "1. ESP8266 / ESP8266EX\n"
        "   -> NodeMCU V2, Wemos D1 Mini, ESP-01S\n\n"
        "2. ESP32 (Classic)\n"
        "   -> ESP32-WROOM-32, NodeMCU-32S, ESP32-DevKitC\n\n"
        "3. ESP32-S2\n"
        "   -> ESP32-S2-Saola, Lolin S2 Mini (Highly Recommended!)\n\n"
        "4. ESP32-S3\n"
        "   -> ESP32-S3-DevKitC-1, Lolin S3 Mini\n\n"
        "5. ESP32-C3\n"
        "   -> ESP32-C3-DevKitM-1, Lolin C3 Mini\n\n"
        "The suite automatically detects your connected hardware and optimizes all compiler configurations!"
    )
    messagebox.showinfo("Supported Devices & Boards", info_text)

def select_zip_file(zip_label, log_callback):
    global selected_zip_path
    file_path = filedialog.askopenfilename(filetypes=[("ZIP-Archive", "*.zip")])
    if file_path:
        selected_zip_path = file_path
        zip_label.config(text=os.path.basename(file_path), fg="#39ff14")
        log_callback(f"[SYSTEM] ZIP source loaded: {file_path}\n")

def get_auto_com_port():
    ports = [p.device for p in serial.tools.list_ports.comports()]
    if ports:
        return ports
    return None

def detect_chip_type(port):
    try:
        cmd = f"python -m esptool --port {port} chip_id"
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        output = proc.stdout.lower() + proc.stderr.lower()
        if "esp32-s2" in output: return "esp32-s2"
        if "esp32-s3" in output: return "esp32-s3"
        if "esp32-c3" in output: return "esp32-c3"
        if "esp32" in output: return "esp32"
        return "esp8266"
    except Exception:
        return "esp8266"
def run_command_live(command, log_callback):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    for line in process.stdout:
        log_callback(line)
    process.stdout.close()
    return process.wait()

def flash_esp_logic(ssid_entry, pw_entry, update_progress, log_callback, flash_btn, zip_btn, monitor_btn, root):
    global selected_zip_path
    try:
        flash_btn.config(state=tk.DISABLED); zip_btn.config(state=tk.DISABLED); monitor_btn.config(state=tk.DISABLED)
        log_callback("=== STARTE MULTI-CHIP HARDWARE BUILD STATION ===\n\n", clear=True)
        
        if not selected_zip_path or not os.path.exists(selected_zip_path):
            log_callback("ABBRUCH-FEHLER: Keine ZIP-Datei ausgewaehlt!\nBitte lade zuerst deine Exploit-ZIP ueber den blauen Button.\n")
            update_progress(0, "ZIP-Quelle fehlt!"); return

        custom_ssid = ssid_entry.get().strip()
        custom_pw = pw_entry.get().strip()
        
        if not custom_ssid:
            log_callback("FEHLER: WLAN-Name darf nicht leer sein!\n"); update_progress(0, "Eingabefehler!"); return
            
        auto_port = get_auto_com_port()
        if not auto_port:
            log_callback("FEHLER: Kein USB-Chip am PC erkannt!\n"); update_progress(0, "Hardware-Fehler!"); return
            
        update_progress(10, "Scanne Hardware-Architektur...")
        log_callback(f"[SYSTEM] Hardware auf Port {auto_port} lokalisiert. Analysiere Chip-Typ...\n")
        
        # 1. HARDWARE-ERKENNUNG TRIGGERN
        chip_type = detect_chip_type(auto_port)
        log_callback(f"[AUTO-DETECT] Architektur erkannt: {chip_type.upper()}\n")
            
        true_base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.realpath(__file__))
        build_dir = os.path.join(true_base_dir, "raw13g_dynamic_build")
        if os.path.exists(build_dir): shutil.rmtree(build_dir)
        os.makedirs(os.path.join(build_dir, "src"), exist_ok=True)
        
        update_progress(25, "Extrahiere Web-Assets aus ZIP...")
        extract_temp = os.path.join(os.environ["TEMP"], "dynamic_zip_extract")
        if os.path.exists(extract_temp): shutil.rmtree(extract_temp)
            
        with zipfile.ZipFile(selected_zip_path, 'r') as zip_ref: zip_ref.extractall(extract_temp)
        html_files = glob.glob(os.path.join(extract_temp, "**", "index.html"), recursive=True)
        
        if not html_files:
            log_callback("ABBRUCH-FEHLER: Keine 'index.html' in der ZIP gefunden!\n")
            update_progress(0, "index.html fehlt!"); return
            
        with open(html_files, "r", encoding="utf-8", errors="ignore") as f: html_content = f.read()
        if os.path.exists(extract_temp): shutil.rmtree(extract_temp)

        html_content = html_content.replace('"', '\\"')
        update_progress(45, "Generiere plattformspezifische Konfiguration...")
        
        # 2. DYNAMISCHE WEICHE FÜR CONFIG & C++ LIBRARIES
        ini_path = os.path.join(build_dir, "platformio.ini")
        if chip_type == "esp32":
            with open(ini_path, "w") as f:
                f.write(f"[env:esp32dev]\nplatform = espressif32\nboard = esp32dev\nframework = arduino\nupload_port = {auto_port}\nupload_speed = 921600\n")
            wifi_headers = "#include <WiFi.h>\n#include <WebServer.h>\n\nWebServer server(80);\n"
        else:
            with open(ini_path, "w") as f:
                f.write(f"[env:nodemcuv2]\nplatform = espressif8266\nboard = nodemcuv2\nframework = arduino\nboard_build.flash_mode = dio\nupload_port = {auto_port}\nupload_speed = 115200\n")
            wifi_headers = "#include <ESP8266WiFi.h>\n#include <ESP8266WebServer.h>\n\nESP8266WebServer server(80);\n"

        update_progress(60, "Schreibe angepassten C++ Quellcode...")
        cpp_path = os.path.join(build_dir, "src", "main.cpp")
        with open(cpp_path, "w") as f:
            f.write('#include <Arduino.h>\n' + wifi_headers + '\nconst char custom_payload_html[] PROGMEM = "' + html_content.replace('\n', ' ').replace('\r', '') + '";\n\nvoid handleRoot() {\n    server.send(200, "text/html", custom_payload_html);\n}\n\nvoid setup() {\n    Serial.begin(115200);\n    delay(1000);\n    IPAddress local_IP(10, 1, 1, 1);\n    IPAddress gateway(10, 1, 1, 1);\n    IPAddress subnet(255, 255, 255, 0);\n    WiFi.softAPConfig(local_IP, gateway, subnet);\n    WiFi.softAP("' + custom_ssid + '", "' + custom_pw + '");\n    server.on("/", handleRoot);\n    server.onNotFound(handleRoot);\n    server.begin();\n}\n\nvoid loop() {\n    server.handleClient();\n}\n')

        update_progress(75, "Kompiliere via PlatformIO...")
        pio_scripts = os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", "Python", "Python314", "Scripts")
        os.environ["PATH"] = pio_scripts + os.path.pathsep + os.environ["PATH"]
        
        build_result = run_command_live(f"platformio run --target upload --project-dir \"{build_dir}\"", log_callback)
        
        if build_result == 0:
            update_progress(100, "Erfolgreich aufgespielt!")
            log_callback(f"\n=======================================================\n 🎉 ALLES ERLEDIGT! Dein {chip_type.upper()}-Dongle ist online!\n=======================================================\n")
        else:
            update_progress(0, "Compiler-Fehler!")
        if os.path.exists(build_dir): shutil.rmtree(build_dir)
    except Exception as e: log_callback(f"\n[SYSTEM FEHLER]: {str(e)}\n")
    finally: flash_btn.config(state=tk.NORMAL); zip_btn.config(state=tk.NORMAL); monitor_btn.config(state=tk.NORMAL)

def monitor_serial_logic(update_progress, log_callback, flash_btn, zip_btn, monitor_btn, root):
    global monitor_active
    ser = None
    try:
        flash_btn.config(state=tk.DISABLED); zip_btn.config(state=tk.DISABLED); monitor_btn.config(text="Stop Monitor", command=lambda: stop_monitor(monitor_btn))
        log_callback("=== NATIVER USB-MONITOR GEOEFFNET ===\n", clear=True)
        auto_port = get_auto_com_port()
        if not auto_port: log_callback("FEHLER: Kein USB-Chip am PC erkannt!\n"); return
        log_callback(f"[INFO] Lausche an {auto_port}... Bitte resette das Board.\n\n")
        ser = serial.Serial(auto_port, 115200, timeout=1); monitor_active = True
        while monitor_active:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore')
                if line: log_callback(line); root.update_idletasks()
    except Exception as e: log_callback(f"\n[DIAGNOSE FEHLER]: {str(e)}\n")
    finally:
        if ser and ser.is_open: ser.close()
        monitor_btn.config(text="[MONITOR] Live-Monitor starten", command=lambda: threading.Thread(target=monitor_serial_logic, args=(update_progress, log_callback, flash_btn, zip_btn, monitor_btn, root), daemon=True).start())
        flash_btn.config(state=tk.NORMAL); zip_btn.config(state=tk.NORMAL)

def stop_monitor(monitor_btn):
    global monitor_active
    monitor_active = False

def start_flash_thread(ssid_entry, pw_entry, update_progress, log_callback, flash_btn, zip_btn, monitor_btn, root):
    threading.Thread(target=flash_esp_logic, args=(ssid_entry, pw_entry, update_progress, log_callback, flash_btn, zip_btn, monitor_btn, root), daemon=True).start()
