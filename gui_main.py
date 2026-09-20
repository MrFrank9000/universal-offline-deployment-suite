import os
import sys
import tkinter as tk
from tkinter import ttk
import mod_esp
import mod_apk
import mod_pc
import lang

def log_message(text, clear=False):
    if clear:
        log_text.delete("1.0", tk.END)
    log_text.insert(tk.END, text)
    log_text.see(tk.END)
    root.update_idletasks()

def update_progress(value, status_text):
    progress_bar["value"] = value
    status_label.config(text=status_text)
    root.update_idletasks()

def change_language(event=None):
    selected_lang = lang_combo.get()
    db = lang.translations[selected_lang]
    
    title_label.config(text=db["title"])
    notebook.tab(0, text=db["tab_welcome"])
    notebook.tab(1, text=db["tab_apk"])
    notebook.tab(2, text=db["tab_esp"])
    notebook.tab(3, text=db["tab_pc"])
    
    dash_title.config(text=db["dash_title"])
    dash_guide.config(text=db["dash_guide"])
    apk_info.config(text=db["apk_info"])
    esp_info.config(text=db["esp_info"])
    pc_info.config(text=db["pc_info"])
    
    apk_zip_btn.config(text=db["btn_load_zip"])
    zip_btn.config(text=db["btn_load_zip"])
    pc_zip_btn.config(text=db["btn_load_zip"])
    
    if "No ZIP" in apk_zip_label.cget("text") or "Keine ZIP" in apk_zip_label.cget("text"):
        apk_zip_label.config(text=db["zip_missing"])
    if "No ZIP" in zip_label.cget("text") or "Keine ZIP" in zip_label.cget("text"):
        zip_label.config(text=db["zip_missing"])
    if "No ZIP" in pc_zip_label.cget("text") or "Keine ZIP" in pc_zip_label.cget("text"):
        pc_zip_label.config(text=db["zip_missing"])
        
    apk_btn.config(text=db["btn_start_apk"])
    apk_m_lbl.config(text=db["apk_maintenance"])
    flash_btn.config(text=db["btn_flash_esp"])
    server_start_btn.config(text=db["btn_start_pc"])
    server_stop_btn.config(text=db["btn_stop_pc"])
    status_label.config(text=db["status_ready"])
    ssid_lbl.config(text=db["lbl_ssid"])
    pw_lbl.config(text=db["lbl_pw"])
    info_esp_btn.config(text=db["btn_info_esp"])
    
    if not mod_esp.monitor_active:
        monitor_btn.config(text=db["btn_mon_esp"])
        
    root.update_idletasks()

root = tk.Tk()
root.title("Universal Offline Deployment Suite (v0.0.3-Test)")
root.geometry("830x780")
root.configure(bg="#121216")
root.resizable(False, False)

lang_frame = tk.Frame(root, bg="#121216")
lang_frame.pack(anchor=tk.E, padx=25, pady=(10, 0))
tk.Label(lang_frame, text="Language:", fg="#aaaaaa", bg="#121216", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=5)
lang_combo = ttk.Combobox(lang_frame, values=["DE", "EN"], width=5, state="readonly")
lang_combo.set("DE")
lang_combo.pack(side=tk.LEFT)
lang_combo.bind("<<ComboboxSelected>>", change_language)

title_label = tk.Label(root, text="UNIVERSAL OFFLINE DEPLOYMENT SUITE (v0.0.3-Test)", fg="#0080ff", bg="#121216", font=("Segoe UI", 14, "bold"))
title_label.pack(pady=10)

notebook = ttk.Notebook(root)
notebook.pack(pady=5, padx=25, fill=tk.BOTH, expand=False)

style = ttk.Style()
style.theme_use('default')
style.configure("TNotebook", background="#121216", borderwidth=0)
style.configure("TNotebook.Tab", background="#8c8c8c", foreground="#000000", font=("Segoe UI", 9, "bold"), padding=10, borderwidth=1, relief=tk.RAISED)
style.map("TNotebook.Tab", background=[("selected", "#00439c"), ("active", "#0059c8")], foreground=[("selected", "#ffffff")])

# TAB 0: DASHBOARD
tab_welcome = tk.Frame(notebook, bg="#161620", padx=25, pady=15)
notebook.add(tab_welcome, text=" Placeholder ")
dash_title = tk.Label(tab_welcome, text="Placeholder", fg="#0080ff", bg="#161620", font=("Segoe UI", 11, "bold"))
dash_title.pack(anchor=tk.W, pady=(0, 5))
dash_guide = tk.Label(tab_welcome, text="Placeholder", fg="#ffffff", bg="#161620", font=("Segoe UI", 9), justify=tk.LEFT)
dash_guide.pack(anchor=tk.W, pady=2)

# TAB 1: APK BUILDER
tab_apk = tk.Frame(notebook, bg="#161620", padx=20, pady=20)
notebook.add(tab_apk, text=" Placeholder ")
apk_info = tk.Label(tab_apk, text="Placeholder", fg="#ffffff", bg="#161620", font=("Segoe UI", 10), justify=tk.LEFT)
apk_info.pack(anchor=tk.W, pady=10)
apk_zip_frame = tk.Frame(tab_apk, bg="#161620")
apk_zip_frame.pack(pady=10, anchor=tk.W)
apk_zip_btn = tk.Button(apk_zip_frame, text="Placeholder", state=tk.DISABLED, bg="#21212d", fg="#888888", font=("Segoe UI", 9, "bold"), padx=10, pady=5, relief=tk.FLAT)
apk_zip_btn.pack(side=tk.LEFT)
apk_zip_label = tk.Label(apk_zip_frame, text="Inaktiv", fg="#888888", bg="#161620", font=("Segoe UI", 9, "italic"))
apk_zip_label.pack(side=tk.LEFT, padx=10)

apk_btn = tk.Button(tab_apk, text="Placeholder", state=tk.DISABLED, bg="#21212d", fg="#888888", font=("Segoe UI", 11, "bold"), padx=30, pady=12, relief=tk.FLAT)
apk_btn.pack(pady=(20, 5))
apk_m_lbl = tk.Label(tab_apk, text="Placeholder", fg="#ff8f00", bg="#161620", font=("Segoe UI", 10, "italic"))
apk_m_lbl.pack(pady=5)
# TAB 2: HARDWARE STICK FLASHER
tab_esp = tk.Frame(notebook, bg="#161620", padx=20, pady=10)
notebook.add(tab_esp, text=" Placeholder ")
esp_info = tk.Label(tab_esp, text="Placeholder", fg="#ffffff", bg="#161620", font=("Segoe UI", 10), justify=tk.LEFT)
esp_info.pack(anchor=tk.W, pady=5)

info_esp_btn = tk.Button(tab_esp, text="Placeholder", command=mod_esp.show_supported_devices, bg="#00439c", fg="white", font=("Segoe UI", 9, "bold"), padx=10, pady=5, relief=tk.FLAT)
info_esp_btn.pack(anchor=tk.E, pady=(0, 5))

input_frame = tk.Frame(tab_esp, bg="#161620")
input_frame.pack(pady=5, fill=tk.X)
ssid_lbl = tk.Label(input_frame, text="Placeholder", fg="#aaaaaa", bg="#161620", font=("Segoe UI", 9))
ssid_lbl.grid(row=0, column=0, sticky=tk.W, pady=5)
ssid_entry = tk.Entry(input_frame, bg="#0d0d11", fg="#ffffff", insertbackground="white", font=("Segoe UI", 10), width=22, relief=tk.FLAT)
ssid_entry.insert(0, "Offline-Web-Server")
ssid_entry.grid(row=0, column=1, pady=5, padx=10)
pw_lbl = tk.Label(input_frame, text="Placeholder", fg="#aaaaaa", bg="#161620", font=("Segoe UI", 9))
pw_lbl.grid(row=0, column=2, sticky=tk.W, pady=5)
pw_entry = tk.Entry(input_frame, bg="#0d0d11", fg="#ffffff", insertbackground="white", font=("Segoe UI", 10), width=22, relief=tk.FLAT)
pw_entry.insert(0, "11110000")
pw_entry.grid(row=0, column=3, pady=5, padx=10)

zip_frame = tk.Frame(tab_esp, bg="#161620")
zip_frame.pack(pady=5, anchor=tk.W)
zip_btn = tk.Button(zip_frame, text="Placeholder", command=lambda: mod_esp.select_zip_file(zip_label, log_message), bg="#21212d", fg="white", font=("Segoe UI", 9, "bold"), padx=10, pady=5, relief=tk.FLAT)
zip_btn.pack(side=tk.LEFT)
zip_label = tk.Label(zip_frame, text="Keine ZIP ausgewaehlt", fg="#ff3333", bg="#161620", font=("Segoe UI", 9, "italic"))
zip_label.pack(side=tk.LEFT, padx=10)

act_frame = tk.Frame(tab_esp, bg="#161620")
act_frame.pack(pady=10)
flash_btn = tk.Button(act_frame, text="Placeholder", command=lambda: mod_esp.start_flash_thread(ssid_entry, pw_entry, update_progress, log_message, flash_btn, zip_btn, monitor_btn, root), bg="#2e7d32", fg="white", font=("Segoe UI", 11, "bold"), padx=20, pady=10, relief=tk.FLAT)
flash_btn.pack(side=tk.LEFT, padx=10)
monitor_btn = tk.Button(act_frame, text="Placeholder", command=lambda: threading.Thread(target=mod_esp.monitor_serial_logic, args=(update_progress, log_message, flash_btn, zip_btn, monitor_btn, root), daemon=True).start(), bg="#ff8f00", fg="black", font=("Segoe UI", 11, "bold"), padx=20, pady=10, relief=tk.FLAT)
monitor_btn.pack(side=tk.LEFT, padx=10)

# TAB 3: PC SERVER
tab_pc = tk.Frame(notebook, bg="#161620", padx=20, pady=20)
notebook.add(tab_pc, text=" Placeholder ")
pc_info = tk.Label(tab_pc, text="Placeholder", fg="#ffffff", bg="#161620", font=("Segoe UI", 10), justify=tk.LEFT)
pc_info.pack(anchor=tk.W, pady=10)
pc_zip_frame = tk.Frame(tab_pc, bg="#161620")
pc_zip_frame.pack(pady=5, anchor=tk.W)
pc_zip_btn = tk.Button(pc_zip_frame, text="Placeholder", command=lambda: mod_pc.select_pc_zip_file(pc_zip_label, log_message), bg="#21212d", fg="white", font=("Segoe UI", 9, "bold"), padx=10, pady=5, relief=tk.FLAT)
pc_zip_btn.pack(side=tk.LEFT)
pc_zip_label = tk.Label(pc_zip_frame, text="Keine ZIP ausgewaehlt", fg="#ff3333", bg="#161620", font=("Segoe UI", 9, "italic"))
pc_zip_label.pack(side=tk.LEFT, padx=10)
pc_act_frame = tk.Frame(tab_pc, bg="#161620")
pc_act_frame.pack(pady=20)
server_start_btn = tk.Button(pc_act_frame, text="Placeholder", command=lambda: mod_pc.start_pc_server_logic(update_progress, log_message, server_start_btn, server_stop_btn, pc_zip_btn, root), bg="#2e7d32", fg="white", font=("Segoe UI", 11, "bold"), padx=20, pady=10, relief=tk.FLAT)
server_start_btn.pack(side=tk.LEFT, padx=10)
server_stop_btn = tk.Button(pc_act_frame, text="Placeholder", command=lambda: mod_pc.stop_pc_server_logic(update_progress, log_message, server_start_btn, server_stop_btn, pc_zip_btn), bg="#c62828", fg="white", font=("Segoe UI", 11, "bold"), padx=20, pady=10, relief=tk.FLAT, state=tk.DISABLED)
server_stop_btn.pack(side=tk.LEFT, padx=10)

# LOG AREA
status_label = tk.Label(root, text="Placeholder", fg="#0080ff", bg="#121216", font=("Segoe UI", 10))
status_label.pack(pady=5)
progress_bar = ttk.Progressbar(root, style="TProgressbar", orient="horizontal", length=750, mode="determinate")
progress_bar.pack(pady=5)
log_frame = tk.Frame(root, bg="#121216")
log_frame.pack(pady=5, padx=25, fill=tk.BOTH, expand=True)
scrollbar = tk.Scrollbar(log_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
log_text = tk.Text(log_frame, bg="#0d0d0d", fg="#39ff14", font=("Consolas", 9), yscrollcommand=scrollbar.set, relief=tk.FLAT)
log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=log_text.yview)

import threading
change_language()
root.mainloop()
