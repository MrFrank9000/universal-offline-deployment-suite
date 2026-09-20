import os
import sys
import glob
import shutil
import zipfile
import threading
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import socket

httpd = None
server_thread = None
selected_pc_zip_path = ""

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def select_pc_zip_file(zip_label, log_callback):
    global selected_pc_zip_path
    from tkinter import filedialog
    file_path = filedialog.askopenfilename(filetypes=[("ZIP-Archive", "*.zip")])
    if file_path:
        selected_pc_zip_path = file_path
        zip_label.config(text=os.path.basename(file_path), fg="#39ff14")
        log_callback(f"[SYSTEM] PC-Host ZIP-Quelle geladen: {file_path}\n")

def start_pc_server_logic(update_progress, log_callback, start_btn, stop_btn, zip_btn, root):
    global httpd, server_thread, selected_pc_zip_path
    try:
        if not selected_pc_zip_path or not os.path.exists(selected_pc_zip_path):
            log_callback("ABBRUCH-FEHLER: Keine Exploit ZIP-Datei fuer den PC-Host ausgewaehlt!\n")
            update_progress(0, "ZIP-Quelle fehlt!")
            return

        start_btn.config(state=tk.DISABLED)
        zip_btn.config(state=tk.DISABLED)
        log_callback("=== STARTE LOKALEN PC EXPLOIT WEB SERVER ===\n\n", clear=True)
        update_progress(20, "Bereite Web-Assets vor...")

        # Temporaeren Web-Ordner auf dem PC anlegen
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            
        www_pc_dir = os.path.join(base_dir, "pc_web_server_dir")
        if os.path.exists(www_pc_dir):
            shutil.rmtree(www_pc_dir)
        os.makedirs(www_pc_dir, exist_ok=True)

        # ZIP entpacken
        update_progress(40, "Entpacke Exploit-ZIP in den PC-Server-Speicher...")
        temp_extract = os.path.join(os.environ["TEMP"], "pc_web_extracted")
        if os.path.exists(temp_extract):
            shutil.rmtree(temp_extract)
            
        with zipfile.ZipFile(selected_pc_zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract)

        extracted_contents = os.listdir(temp_extract)
        if extracted_contents:
            src_folder = os.path.join(temp_extract, extracted_contents[0])
            if os.path.isdir(src_folder):
                for item in os.listdir(src_folder):
                    s = os.path.join(src_folder, item)
                    d = os.path.join(www_pc_dir, item)
                    shutil.copytree(s, d, dirs_exist_ok=True) if os.path.isdir(s) else shutil.copy2(s, d)
        shutil.rmtree(temp_extract)

        # In das Web-Verzeichnis wechseln fuer den HTTP-Handler
        os.chdir(www_pc_dir)

        # Server aufsetzen auf Port 8080 (Port 80 blockiert Windows oft)
        port = 8080
        local_ip = get_local_ip()

        class MyHandler(SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                log_callback(f"[PC-SERVER REQUEST] {format%args}\n")

        handler = MyHandler
        TCPServer.allow_reuse_address = True
        httpd = TCPServer(("", port), handler)

        def serve_forever_thread():
            httpd.serve_forever()

        server_thread = threading.Thread(target=serve_forever_thread, daemon=True)
        server_thread.start()

        update_progress(100, "PC Web Server aktiv!")
        log_callback(f"=======================================================\n")
        log_callback(f" 🎉 SUCCESS! Der lokale PC-Webserver laeuft!\n")
        log_callback(f" -> Adresse fuer den PS4-Browser:\n")
        log_callback(f"    http://{local_ip}:{port}\n")
        log_callback(f"=======================================================\n")
        log_callback(f"[INFO] Der Server laeuft, solange dieses Fenster geoeffnet bleibt.\n")
        stop_btn.config(state=tk.NORMAL)

    except Exception as e:
        log_callback(f"\n[SERVER FEHLER]: {str(e)}\n")
        start_btn.config(state=tk.NORMAL)
        zip_btn.config(state=tk.NORMAL)

def stop_pc_server_logic(update_progress, log_callback, start_btn, stop_btn, zip_btn):
    global httpd
    try:
        if httpd:
            httpd.shutdown()
            httpd.server_close()
            httpd = None
        log_callback("\n[SYSTEM] Lokaler PC-Webserver erfolgreich gestoppt.\n")
        update_progress(100, "PC Web Server gestoppt.")
    except Exception as e:
        log_callback(f"\n[STOP FEHLER]: {str(e)}\n")
    finally:
        start_btn.config(state=tk.NORMAL)
        zip_btn.config(state=tk.NORMAL)
        stop_btn.config(state=tk.DISABLED)

import tkinter as tk
