import os, sys, shutil, zipfile, threading, http.server, socketserver, socket, tkinter as tk
from tkinter import filedialog

selected_pc_zip = ""
server_instance = None
server_thread = None

def select_zip_file(lbl, log_callback):
    global selected_pc_zip
    f = filedialog.askopenfilename(filetypes=[("ZIP", "*.zip")])
    if f:
        selected_pc_zip = f
        lbl.config(text=os.path.basename(f), fg="#39ff14")
        log_callback(f"[PC SERVER] Loaded Target Website ZIP: {f}\n")

class CustomHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0] # Holt exakt den String der primaeren Netzwerkkarte
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

# UNZERSTÖRBAR: Die Logic nimmt nun das ip_display_lbl der Haupt-GUI entgegen!
def run_server_logic(log_callback, update_progress, start_btn, stop_btn, ip_display_lbl):
    global server_instance, selected_pc_zip
    try:
        if not selected_pc_zip or not os.path.exists(selected_pc_zip):
            log_callback("[ERROR] Please select a valid Website ZIP file first!\n")
            update_progress(0, "ZIP Missing!")
            start_btn.config(state=tk.NORMAL)
            stop_btn.config(state=tk.DISABLED)
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        pc_fs_dir = os.path.join(base_dir, "pc_web_fs")
        shutil.rmtree(pc_fs_dir, ignore_errors=True)
        os.makedirs(pc_fs_dir, exist_ok=True)

        log_callback("[PC SERVER] Unpacking assets into temporary webroot...\n")
        with zipfile.ZipFile(selected_pc_zip, 'r') as z:
            for member in z.infolist():
                filename = member.filename
                parts = filename.split('/', 1)
                if len(parts) > 1 and parts[1]:
                    clean_rel_path = parts[1].replace('/', os.sep)
                    target_path = os.path.join(pc_fs_dir, clean_rel_path)
                    if member.is_dir(): 
                        os.makedirs(target_path, exist_ok=True)
                    else:
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        with z.open(member) as src, open(target_path, "wb") as tgt:
                            shutil.copyfileobj(src, tgt)

        os.chdir(pc_fs_dir)
        handler = CustomHTTPHandler
        
        socketserver.TCPServer.allow_reuse_address = True
        server_instance = socketserver.TCPServer(("", 80), handler)
        
        local_lan_ip = get_local_ip()
        
        log_callback("=======================================================\n")
        log_callback(" 🎉 SUCCESS! PC LOCAL SERVER IS NOW ONLINE ON PORT 80!\n")
        log_callback(f" -> Target URL for your PS4 Console: http://{local_lan_ip}\n")
        log_callback("=======================================================\n")
        update_progress(100, "Server Running")
        
        # PROFI-SCHLUSS: Beschreibt das grosse Label unter den Buttons fett und gut lesbar!
        ip_display_lbl.config(text=f"PS4 URL: http://{local_lan_ip}", fg="#39ff14")
        
        server_instance.serve_forever()
    except Exception as e:
        log_callback(f"[PC SERVER ERROR]: {str(e)}\n")
        start_btn.config(state=tk.NORMAL)
        stop_btn.config(state=tk.DISABLED)
        ip_display_lbl.config(text="SERVER ERROR", fg="#d32f2f")

def start_server_thread(log_callback, update_progress, start_btn, stop_btn, ip_display_lbl):
    global server_thread
    start_btn.config(state=tk.DISABLED)
    stop_btn.config(state=tk.NORMAL)
    ip_display_lbl.config(text="STARTING SERVER...", fg="#ff8f00")
    log_callback("=== INITIATING LOCAL HTTP SERVER ON PORT 80 ===\n", clear=True)
    update_progress(30, "Detecting network interface...")
    
    # Uebergibt das Label an den asynchronen Hintergrund-Thread
    server_thread = threading.Thread(target=run_server_logic, args=(log_callback, update_progress, start_btn, stop_btn, ip_display_lbl), daemon=True)
    server_thread.start()

def stop_server_logic(log_callback, update_progress, start_btn, stop_btn, ip_display_lbl):
    global server_instance
    log_callback("\n[PC SERVER] Shutting down HTTP engine and clearing ports...\n")
    if server_instance:
        server_instance.shutdown()
        server_instance.server_close()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    shutil.rmtree(os.path.join(base_dir, "pc_web_fs"), ignore_errors=True)
    
    start_btn.config(state=tk.NORMAL)
    stop_btn.config(state=tk.DISABLED)
    
    # Setzt das Label im Hauptmenue spiegelblank zurueck
    ip_display_lbl.config(text="SERVER OFFLINE", fg="gray")
    update_progress(0, "Server Stopped")
    log_callback("[PC SERVER] HTTP Server offline successfully.\n")
