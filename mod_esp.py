import os
import sys
import glob
import shutil
import zipfile
import subprocess
import threading
import platform
import tkinter as tk
from tkinter import filedialog, messagebox

selected_zip_path = ""
monitor_active = False
ser = None

def select_zip_file(zip_label, log_callback):
    global selected_zip_path
    file_path = filedialog.askopenfilename(filetypes=[("ZIP-Archive", "*.zip")])
    if file_path:
        selected_zip_path = file_path
        zip_label.config(text=os.path.basename(file_path), fg="#39ff14")
        log_callback(f"[SYSTEM] Hardware ZIP source loaded: {file_path}\n")

def show_supported_devices():
    devices = (
        "- ESP8266 / ESP8266EX (NodeMCU V2, Wemos D1 Mini)\n"
        "- ESP32 (Classic WROOM-32, NodeMCU-32S)\n"
        "- ESP32-S2 (Saola, Lolin S2 Mini - Highly Recommended)\n"
        "- ESP32-S3 (DevKitC-1, Lolin S3 Mini)\n"
        "- ESP32-C3 (DevKitM-1, Lolin C3 Mini)\n\n"
        "All chip architectures are detected automatically during the flashing process."
    )
    messagebox.showinfo("Supported Hardware Devices", devices)

def get_auto_com_port(log_callback):
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    
    # CROSS-PLATFORM PORT DETECTION: Filtert je nach Betriebssystem
    current_os = platform.system()
    for p in ports:
        p_upper = p.device.upper()
        if current_os == "Windows" and "COM" in p_upper:
            log_callback(f"[HARDWARE] Auto-detected Windows port: {p.device}\n")
            return p.device
        elif current_os == "Linux" and ("TTYUSB" in p_upper or "TTYACM" in p_upper or "TTY" in p_upper):
            log_callback(f"[HARDWARE] Auto-detected Linux port: {p.device}\n")
            return p.device
            
    if ports:
        log_callback(f"[WARNING] Using first available port fallback: {ports[0].device}\n")
        return ports[0].device
    return None
def run_flash_logic(ssid_entry, pw_entry, update_progress, log_callback, flash_btn, zip_btn, mon_btn, root):
    global selected_zip_path
    try:
        flash_btn.config(state=tk.DISABLED); zip_btn.config(state=tk.DISABLED); mon_btn.config(state=tk.DISABLED)
        log_callback("=== STARTING CROSS-PLATFORM HARDWARE FLASHER ===\n\n", clear=True)
        
        if not selected_zip_path or not os.path.exists(selected_zip_path):
            log_callback("ERROR: No firmware ZIP file selected!\n")
            update_progress(0, "ZIP missing!"); return
            
        ssid = ssid_entry.get().strip()
        pw = pw_entry.get().strip()
        
        update_progress(10, "Scanning USB serial ports...")
        com_port = get_auto_com_port(log_callback)
        if not com_port:
            log_callback("ERROR: No connected ESP board found! Please check your USB cable.\n")
            update_progress(0, "Device not found!"); return
            
        base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        
        # CROSS-PLATFORM PATHS: os.path.join regelt die Slashes automatisch fuer Windows und Linux
        firmware_dir = os.path.join(base_dir, "firmware_src")
        if os.path.exists(firmware_dir): shutil.rmtree(firmware_dir)
        os.makedirs(firmware_dir, exist_ok=True)
        
        log_callback(f"[SYSTEM] Unpacking assets: {os.path.basename(selected_zip_path)}\n")
        update_progress(30, "Extracting firmware assets...")
        with zipfile.ZipFile(selected_zip_path, 'r') as zip_ref:
            zip_ref.extractall(firmware_dir)
            
        update_progress(60, "Configuring Wi-Fi credentials...")
        config_path = os.path.join(firmware_dir, "wifi_config.h")
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(f'#define WIFI_SSID "{ssid}"\n#define WIFI_PASSWORD "{pw}"\n#define SERVER_PORT 80\n')
            
        update_progress(80, "Executing esptool flasher...")
        log_callback(f"[HARDWARE] Flashing stick on port {com_port} via Port 80 core...\n")
        
        # CROSS-PLATFORM EXECUTABLE DETECTION
        esptool_cmd = "esptool.exe" if platform.system() == "Windows" else "esptool"
        
        process = subprocess.Popen(
            [esptool_cmd, "--port", com_port, "--baud", "460800", "write_flash", "0x0", os.path.join(firmware_dir, "firmware.bin")],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
        )
        for line in process.stdout:
            log_callback(line)
            root.update_idletasks()
        process.stdout.close()
        rc = process.wait()
        
        if rc == 0:
            update_progress(100, "Flash Successful!")
            log_callback("\n=======================================================\n 🎉 SUCCESS! Hardware stick flashed successfully on Port 80!\n=======================================================\n")
        else:
            update_progress(0, "Flasher error!")
            log_callback(f"\nERROR: esptool exited with error code {rc}\n")
            
    except Exception as e:
        log_callback(f"\n[CRITICAL ERROR]: {str(e)}\n")
        update_progress(0, "Failed!")
    finally:
        flash_btn.config(state=tk.NORMAL); zip_btn.config(state=tk.NORMAL); mon_btn.config(state=tk.NORMAL)

def start_flash_thread(ssid_entry, pw_entry, update_progress, log_callback, flash_btn, zip_btn, mon_btn, root):
    threading.Thread(target=run_flash_logic, args=(ssid_entry, pw_entry, update_progress, log_callback, flash_btn, zip_btn, mon_btn, root), daemon=True).start()

def monitor_serial_logic(update_progress, log_callback, flash_btn, zip_btn, mon_btn, root):
    global monitor_active, ser
    import serial
    if monitor_active:
        monitor_active = False
        if ser and ser.is_open: ser.close()
        log_callback("\n[MONITOR] Serial monitor stopped.\n")
        mon_btn.config(text="Start Live Monitor", bg="#ff8f00", fg="black")
        flash_btn.config(state=tk.NORMAL); zip_btn.config(state=tk.NORMAL)
        return
        
    com_port = get_auto_com_port(log_callback)
    if not com_port:
        log_callback("ERROR: Cannot start monitor. No device found!\n")
        return
        
    try:
        ser = serial.Serial(com_port, 115200, timeout=1)
        monitor_active = True
        log_callback(f"=== STARTING SERIAL MONITOR ON PORT {com_port} (115200 Baud) ===\n\n")
        mon_btn.config(text="STOP MONITOR", bg="#c62828", fg="white")
        flash_btn.config(state=tk.DISABLED); zip_btn.config(state=tk.DISABLED)
        
        while monitor_active:
            if ser.in_waiting:
                data = ser.readline().decode('utf-8', errors='ignore')
                log_callback(data)
                root.update_idletasks()
            root.update_idletasks()
    except Exception as e:
        log_callback(f"\n[MONITOR ERROR]: {str(e)}\n")
        monitor_active = False
        if ser and ser.is_open: ser.close()
        mon_btn.config(text="Start Live Monitor", bg="#ff8f00", fg="black")
        flash_btn.config(state=tk.NORMAL); zip_btn.config(state=tk.NORMAL)
