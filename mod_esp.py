import os, sys, glob, shutil, zipfile, subprocess, threading, platform, tkinter as tk
from tkinter import filedialog, messagebox

selected_zip_path = ""
monitor_active = False
ser = None

def select_zip_file(lbl, cb):
    global selected_zip_path
    f = filedialog.askopenfilename(filetypes=[("ZIP", "*.zip")])
    if f: selected_zip_path = f; lbl.config(text=os.path.basename(f), fg="#39ff14"); cb(f"[SYSTEM] Loaded ZIP: {f}\n")

def show_supported_devices():
    messagebox.showinfo("Devices", "ESP8266EX fully supported with validated list array indexing.")

def refresh_board_list(dropdown_widget, log_callback):
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    found_devices = []
    for p in ports:
        vid = p.vid if p.vid is not None else 0
        pid = p.pid if p.pid is not None else 0
        b_type = "NodeMCU" if (vid == 0x1a86 or vid == 0x10c4) else "Wemos D1 Mini"
        found_devices.append(f"{p.device} - {b_type}")
    if not found_devices: found_devices = ["No Device Found"]
    dropdown_widget["values"] = found_devices
    dropdown_widget.set(found_devices)
    return ports
def run_flash_logic(ssid_entry, pw_entry, board_var, update_progress, log_callback, flash_btn, zip_btn, mon_btn, root):
    global selected_zip_path
    try:
        ssid = ssid_entry.get().strip(); pw = pw_entry.get().strip(); selection = str(board_var.get())
        if not selected_zip_path or not os.path.exists(selected_zip_path):
            log_callback("[ERROR] No Website ZIP file selected!\n"); update_progress(0, "ZIP missing!"); return
        if "No Device" in selection or "-" not in selection:
            log_callback("[ERROR] No hardware stick selected in dropdown!\n"); update_progress(0, "No Selection!"); return
            
        # ABSOLUTER ARRAYS-FIX: Expliziter Index-Zugriff auf das erste Element [0] vor dem Strippen!
        clean_selection = selection.replace("{", "").replace("}", "").strip()
        parts = clean_selection.split(" - ")
        com_port = parts[0].strip()
        board_type = parts[1].strip() if len(parts) > 1 else "NodeMCU"
        
        flash_btn.config(state=tk.DISABLED); zip_btn.config(state=tk.DISABLED); mon_btn.config(state=tk.DISABLED)
        log_callback(f"=== INITIATING FLAT SPIFFS BUILD ON {com_port} ===\n\n", clear=True)
        update_progress(10, "Preparing sandbox...")
        
        if getattr(sys, 'frozen', False): base_dir = os.path.dirname(sys.executable)
        else: base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        fs_dir = os.path.join(base_dir, "web_fs")
        shutil.rmtree(fs_dir, ignore_errors=True)
        os.makedirs(fs_dir, exist_ok=True)
        
        log_callback("[SYSTEM] Unpacking ZIP and peeling off GitHub wrapper folder...\n")
        update_progress(25, "Extracting payload...")
        
        with zipfile.ZipFile(selected_zip_path, 'r') as z:
            for member in z.infolist():
                filename = member.filename
                p_parts = filename.split('/', 1)
                if len(p_parts) > 1 and p_parts[1]:
                    new_rel_path = p_parts[1]
                    target_path = os.path.join(fs_dir, new_rel_path.replace('/', os.sep))
                    if member.is_dir():
                        os.makedirs(target_path, exist_ok=True)
                    else:
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        with z.open(member) as source, open(target_path, "wb") as target:
                            shutil.copyfileobj(source, target)
                            
        log_callback("[SYSTEM] Injecting system configurations (wifi_config.txt)...\n")
        with open(os.path.join(fs_dir, "wifi_config.txt"), "w", encoding="utf-8") as fcf:
            fcf.write(f"{ssid}\n{pw}\n")
            
        user_home = os.path.expanduser("~")
        mkspiffs_glob = os.path.join(user_home, "AppData", "Local", "Arduino15", "packages", "esp8266", "tools", "mkspiffs", "*", "mkspiffs.exe")
        found_tools = glob.glob(mkspiffs_glob)
        if not found_tools:
            log_callback("[CRITICAL ERROR] Official mkspiffs.exe compiler missing in Arduino15!\n")
            update_progress(0, "Toolchain missing!"); return
            
        mkspiffs_cmd = found_tools[0]
        target_fs_bin = os.path.join(base_dir, "firmware_src", "spiffs_data.bin")
        
        if os.path.exists(target_fs_bin): os.remove(target_fs_bin)
        os.makedirs(os.path.dirname(target_fs_bin), exist_ok=True)
        
        log_callback(f"[COMPILER] Invoking factory binary: {os.path.basename(mkspiffs_cmd)}\n")
        log_callback("[COMPILER] Compiling normalized 3MB SPIFFS filesystem map...\n")
        update_progress(50, "Compiling filesystem...")
        
        mk_proc = subprocess.Popen([
            mkspiffs_cmd, "-c", fs_dir, "-b", "8192", "-p", "256", "-s", "3145728", target_fs_bin
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in mk_proc.stdout:
            log_callback(f" [MKSPIFFS] {line}")
        mk_proc.wait()
        
        esptool_cmd = "esptool.exe" if platform.system() == "Windows" else "esptool"
        log_callback(f"[HARDWARE] Flashing certified asset binary to Sektor 0x100000 on {com_port}...\n")
        update_progress(75, "Uploading filesystem...")
        
        p = subprocess.Popen([esptool_cmd, "--port", com_port, "--baud", "460800", "write_flash", "--flash_mode", "dio", "0x100000", target_fs_bin], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in p.stdout: log_callback(line); root.update_idletasks()
        p.stdout.close(); rc = p.wait()
        
        shutil.rmtree(fs_dir, ignore_errors=True)
        if rc == 0:
            update_progress(100, "Flash Successful!")
            log_callback(f"\n=======================================================\n 🎉 SUCCESS! Standardized C++ Server synchronized and active!\n -> Gateway Node : http://10.1.1.1\n=======================================================\n")
        else: log_callback(f"\nERROR: esptool code {rc}\n")
    except Exception as e: log_callback(f"\n[ERROR]: {str(e)}\n")
    finally: flash_btn.config(state=tk.NORMAL); zip_btn.config(state=tk.NORMAL); mon_btn.config(state=tk.NORMAL)

def start_flash_thread(ssid, pw, board_var, up, log, fb, zb, mb, r):
    threading.Thread(target=run_flash_logic, args=(ssid, pw, board_var, up, log, fb, zb, mb, r), daemon=True).start()

def run_monitor_logic(update_progress, log_callback, flash_btn, zip_btn, mon_btn, root, board_var, ssid_val, pw_val):
    global monitor_active, ser
    import serial, time
    selection = str(board_var.get())
    if "No Device" in selection or "-" not in selection: monitor_active = False; return
    clean_selection = selection.replace("{", "").replace("}", "").strip()
    parts = clean_selection.split(" - ")
    com_port = parts[0].strip()
    try:
        ser = serial.Serial(com_port, 74880, timeout=1)
        ser.setDTR(False); ser.setRTS(False); time.sleep(0.1); ser.setDTR(True); ser.setRTS(True); time.sleep(0.1); ser.setDTR(False)
        log_callback(f"=== ASYNC LIVE MONITOR ACTIVE ON {com_port} AT 74880 BAUD ===\n")
        log_callback("-------------------------------------------------------\n")
        log_callback(f" [AUDIT] Injected WLAN SSID : {ssid_val}\n")
        log_callback(f" [AUDIT] Network Gateway    : http://10.1.1.1:80\n")
        log_block = "-------------------------------------------------------\n Waiting for native hardware API boot logs...\n\n"
        log_callback(log_block)
        while monitor_active:
            if ser.in_waiting: log_callback(ser.readline().decode('utf-8', errors='ignore'))
            time.sleep(0.01)
    except Exception as e: log_callback(f"\n[MONITOR ERROR]: {str(e)}\n")
    finally:
        monitor_active = False
        if ser and ser.is_open: ser.close()
        mon_btn.config(text="Start Live Monitor", bg="#ff8f00", fg="black")
        flash_btn.config(state=tk.NORMAL); zip_btn.config(state=tk.NORMAL)

def monitor_serial_logic(update_progress, log_callback, flash_btn, zip_btn, mon_btn, root, board_var, ssid_entry=None, pw_entry=None):
    global monitor_active, ser
    if monitor_active: monitor_active = False; return
    monitor_active = True
    mon_btn.config(text="STOP MONITOR", bg="#c62828", fg="white"); flash_btn.config(state=tk.DISABLED); zip_btn.config(state=tk.DISABLED)
    s_val = ssid_entry.get().strip() if ssid_entry else "N/A"
    p_val = pw_entry.get().strip() if pw_entry else "N/A"
    threading.Thread(target=run_monitor_logic, args=(update_progress, log_callback, flash_btn, zip_btn, mon_btn, root, board_var, s_val, p_val), daemon=True).start()
