import os
import sys
import glob
import shutil
import zipfile
import threading
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import socket
import tkinter as tk

httpd = None
server_thread = None
selected_pc_zip_path = ""

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()
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
        log_callback(f"[SYSTEM] PC ZIP source loaded: {file_path}\n")

def start_pc_server_logic(update_progress, log_callback, start_btn, stop_btn, zip_btn, root):
    global httpd, server_thread, selected_pc_zip_path
    try:
        if not selected_pc_zip_path or not os.path.exists(selected_pc_zip_path):
            log_callback("ERROR: No ZIP file selected!\n")
            update_progress(0, "ZIP missing!")
            return

        start_btn.config(state=tk.DISABLED); zip_btn.config(state=tk.DISABLED)
        log_callback("=== STARTING LOCAL WEB SERVER ===\n\n", clear=True)
        update_progress(20, "Preparing web assets...")

        base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        
        # CROSS-PLATFORM FIX: os.path.join verwaltet die Slashes fuer Windows und Linux vollautomatisch!
        www_pc_dir = os.path.join(base_dir, "pc_web_server_dir")
        if os.path.exists(www_pc_dir): shutil.rmtree(www_pc_dir)
        os.makedirs(www_pc_dir, exist_ok=True)

        temp_extract = os.path.join(os.environ.get("TEMP", os.environ.get("TMP", "/tmp")), "pc_web_extracted")
        if os.path.exists(temp_extract): shutil.rmtree(temp_extract)
        with zipfile.ZipFile(selected_pc_zip_path, 'r') as zip_ref: zip_ref.extractall(temp_extract)

        extracted_contents = os.listdir(temp_extract)
        if extracted_contents:
            src_folder = os.path.join(temp_extract, extracted_contents)
            if os.path.isdir(src_folder):
                for item in os.listdir(src_folder):
                    s = os.path.join(src_folder, item); d = os.path.join(www_pc_dir, item)
                    shutil.copytree(s, d, dirs_exist_ok=True) if os.path.isdir(s) else shutil.copy2(s, d)
        shutil.rmtree(temp_extract)

        port = 80
        local_ip = get_local_ip()

        class MyHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=www_pc_dir, **kwargs)
            def log_message(self, format, *args):
                log_callback(f"[SERVER REQUEST] {format%args}\n")

        TCPServer.allow_reuse_address = True
        httpd = TCPServer(("", port), MyHandler)
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()

        update_progress(100, "Server Active!")
        log_callback("=======================================================\n")
        log_callback(" SUCCESS! Local Web Server is running on Port 80!\n")
        log_callback(f" -> Address for your console browser:\n")
        log_callback(f"    http://{local_ip}\n")
        log_callback("=======================================================\n")
        stop_btn.config(state=tk.NORMAL)
    except Exception as e:
        log_callback(f"\n[SERVER ERROR]: {str(e)}\n")
        start_btn.config(state=tk.NORMAL); zip_btn.config(state=tk.NORMAL)

def stop_pc_server_logic(update_progress, log_callback, start_btn, stop_btn, zip_btn):
    global httpd
    try:
        if httpd:
            httpd.shutdown(); httpd.server_close(); httpd = None
        log_callback("\n[SYSTEM] Local Web Server stopped successfully.\n")
        update_progress(100, "Server stopped.")
    except Exception as e: log_callback(f"\n[STOP ERROR]: {str(e)}\n")
    finally: start_btn.config(state=tk.NORMAL); zip_btn.config(state=tk.NORMAL); stop_btn.config(state=tk.DISABLED)
