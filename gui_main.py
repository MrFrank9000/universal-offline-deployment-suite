import os, sys, platform, tkinter as tk
from tkinter import ttk, messagebox
import lang, mod_pc, mod_esp, mod_apk
current_lang = "DE"

def switch_language():
    global current_lang; current_lang = "EN" if current_lang == "DE" else "DE"; refresh_ui_texts()

def log_to_console(text, clear=False):
    console_box.config(state=tk.NORMAL)
    if clear: console_box.delete("1.0", tk.END)
    console_box.insert(tk.END, text); console_box.see(tk.END); console_box.config(state=tk.DISABLED)

def update_progress(val, text): progress_bar["value"] = val; progress_lbl.config(text=text); root.update_idletasks()

def show_external_credits():
    db = lang.translations[current_lang]
    popup = tk.Toplevel(root)
    popup.title(db["btn_credits"])
    popup.geometry("620x460")
    popup.configure(bg="#1a1a1a")
    popup.resizable(False, False)
    popup.transient(root)
    popup.grab_set()
    
    title_lbl = tk.Label(popup, text=db["btn_credits"], font=("Arial", 14, "bold"), fg="#ff8f00", bg="#1a1a1a", pady=15)
    title_lbl.pack()
    
    text_frame = tk.Frame(popup, bg="#121212", bd=1, relief=tk.SOLID)
    text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    credits_box = tk.Text(text_frame, bg="#121212", fg="white", font=("Consolas", 10), wrap=tk.WORD, bd=0, padx=10, pady=10)
    credits_box.insert(tk.END, db["credits_text"])
    credits_box.config(state=tk.DISABLED)
    credits_box.pack(fill=tk.BOTH, expand=True)
    
    close_btn = tk.Button(popup, text="OK", bg="#1976d2", fg="white", font=("Arial", 10, "bold"), bd=0, padx=25, pady=5, command=popup.destroy)
    close_btn.pack(pady=15)

def refresh_ui_texts():
    db = lang.translations[current_lang]; root.title(db["title"]); status_bar.config(text=db["status_ready"])
    notebook.tab(0, text=db["tab_welcome"]); notebook.tab(1, text=db["tab_apk"]); notebook.tab(2, text=db["tab_esp"]); notebook.tab(3, text=db["tab_pc"])
    welcome_title.config(text=db["dash_title"]); welcome_text.config(text=db["dash_guide"])
    apk_info_lbl.config(text=db["apk_info"]); esp_info_lbl.config(text=db["esp_info"]); pc_info_lbl.config(text=db["pc_info"])
    zip_btn1.config(text=db["btn_load_zip"]); zip_btn2.config(text=db["btn_load_zip"]); zip_btn3.config(text=db["btn_load_zip"])
    apk_start_btn.config(text=db["btn_start_apk"]); flash_btn.config(text=db["btn_flash_esp"])
    pc_start_btn.config(text=db["btn_start_pc"]); pc_stop_btn.config(text=db["btn_stop_pc"])
    lbl_ssid.config(text=db["lbl_ssid"]); lbl_pw.config(text=db["lbl_pw"]); mon_btn.config(text=db["btn_mon_esp"])
    credits_main_btn.config(text=db["btn_credits"])

root = tk.Tk(); root.geometry("820x680"); root.configure(bg="#121212")
style = ttk.Style(); style.theme_use("clam")
style.configure("TNotebook", background="#1a1a1a", borderwidth=0)
style.configure("TNotebook.Tab", background="#2d2d2d", foreground="white", padding=5)
style.map("TNotebook.Tab", background=[("selected", "#ff8f00")], foreground=[("selected", "black")])

top_frame = tk.Frame(root, bg="#1a1a1a", height=40); top_frame.pack(fill=tk.X, side=tk.TOP)
tk.Button(top_frame, text="EN / DE", bg="#2d2d2d", fg="white", font=("Arial", 9, "bold"), command=switch_language, bd=0, padx=10).pack(side=tk.RIGHT, padx=10, pady=5)

notebook = ttk.Notebook(root); notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
tab_welcome = tk.Frame(notebook, bg="#1a1a1a"); notebook.add(tab_welcome, text="")
welcome_title = tk.Label(tab_welcome, font=("Arial", 16, "bold"), fg="#ff8f00", bg="#1a1a1a", pady=10); welcome_title.pack()
welcome_text = tk.Label(tab_welcome, font=("Arial", 11), fg="white", bg="#1a1a1a", justify=tk.LEFT, pady=10); welcome_text.pack(padx=20)

credits_main_btn = tk.Button(tab_welcome, bg="#1976d2", fg="white", font=("Arial", 10, "bold"), command=show_external_credits, bd=0, padx=15, pady=5)
credits_main_btn.pack(pady=15)

tab_apk = tk.Frame(notebook, bg="#1a1a1a"); notebook.add(tab_apk, text="")
apk_info_lbl = tk.Label(tab_apk, font=("Arial", 11), fg="white", bg="#1a1a1a", pady=10); apk_info_lbl.pack()
zip_btn1 = tk.Button(tab_apk, bg="#2d2d2d", fg="white", font=("Arial", 10, "bold"), command=lambda: mod_apk.select_zip_file(zip_lbl1, log_to_console)); zip_btn1.pack(pady=5)
zip_lbl1 = tk.Label(tab_apk, text="...", fg="gray", bg="#1a1a1a"); zip_lbl1.pack()
apk_start_btn = tk.Button(tab_apk, bg="#333333", fg="gray", font=("Arial", 11, "bold"), state=tk.DISABLED); apk_start_btn.pack(pady=20)

tab_esp = tk.Frame(notebook, bg="#1a1a1a"); notebook.add(tab_esp, text="")
esp_info_lbl = tk.Label(tab_esp, font=("Arial", 11), fg="white", bg="#1a1a1a", pady=5); esp_info_lbl.pack()
form_frame = tk.Frame(tab_esp, bg="#1a1a1a"); form_frame.pack(pady=5)
lbl_ssid = tk.Label(form_frame, fg="white", bg="#1a1a1a", font=("Arial", 10, "bold")); lbl_ssid.grid(row=0, column=0, padx=5, sticky=tk.W)
ssid_entry = tk.Entry(form_frame, bg="#2d2d2d", fg="white", insertbackground="white", width=25); ssid_entry.insert(0, "Offline-Web-Server"); ssid_entry.grid(row=0, column=1, padx=5)
lbl_pw = tk.Label(form_frame, fg="white", bg="#1a1a1a", font=("Arial", 10, "bold")); lbl_pw.grid(row=1, column=0, padx=5, sticky=tk.W)
pw_entry = tk.Entry(form_frame, bg="#2d2d2d", fg="white", insertbackground="white", width=25); pw_entry.insert(0, "12345678"); pw_entry.grid(row=1, column=1, padx=5)

tk.Label(form_frame, text="Select Stick:", fg="white", bg="#1a1a1a", font=("Arial", 10, "bold")).grid(row=2, column=0, padx=5, sticky=tk.W)
board_var = tk.StringVar()
board_dropdown = ttk.Combobox(form_frame, textvariable=board_var, state="readonly", width=22)
board_dropdown.grid(row=2, column=1, padx=5)
refresh_btn = tk.Button(form_frame, text="🔄", bg="#2d2d2d", fg="white", bd=0, command=lambda: mod_esp.refresh_board_list(board_dropdown, log_to_console))
refresh_btn.grid(row=2, column=2, padx=5)

btn_frame = tk.Frame(tab_esp, bg="#1a1a1a"); btn_frame.pack(pady=5)
zip_btn2 = tk.Button(btn_frame, bg="#2d2d2d", fg="white", font=("Arial", 10, "bold"), command=lambda: mod_esp.select_zip_file(zip_lbl2, log_to_console)); zip_btn2.pack(side=tk.LEFT, padx=5)
flash_btn = tk.Button(btn_frame, bg="#ff8f00", fg="black", font=("Arial", 10, "bold"), command=lambda: mod_esp.start_flash_thread(ssid_entry, pw_entry, board_var, update_progress, log_to_console, flash_btn, zip_btn2, mon_btn, root)); flash_btn.pack(side=tk.LEFT, padx=5)
mon_btn = tk.Button(btn_frame, bg="#ff8f00", fg="black", font=("Arial", 10, "bold"), command=lambda: mod_esp.monitor_serial_logic(update_progress, log_to_console, flash_btn, zip_btn2, mon_btn, root, board_var, ssid_entry, pw_entry)); mon_btn.pack(side=tk.LEFT, padx=5)

zip_lbl2 = tk.Label(tab_esp, text="...", fg="gray", bg="#1a1a1a"); zip_lbl2.pack()

tab_pc = tk.Frame(notebook, bg="#1a1a1a"); notebook.add(tab_pc, text="")
pc_info_lbl = tk.Label(tab_pc, font=("Arial", 11), fg="white", bg="#1a1a1a", pady=10); pc_info_lbl.pack()
zip_btn3 = tk.Button(tab_pc, bg="#2d2d2d", fg="white", font=("Arial", 10, "bold"), command=lambda: mod_pc.select_zip_file(zip_lbl3, log_to_console)); zip_btn3.pack(pady=5)
zip_lbl3 = tk.Label(tab_pc, text="...", fg="gray", bg="#1a1a1a"); zip_lbl3.pack()

pc_btn_frame = tk.Frame(tab_pc, bg="#1a1a1a"); pc_btn_frame.pack(pady=15)
pc_start_btn = tk.Button(pc_btn_frame, bg="#388e3c", fg="white", font=("Arial", 11, "bold"), command=lambda: mod_pc.start_server_thread(log_to_console, update_progress, pc_start_btn, pc_stop_btn, ip_display_lbl)); pc_start_btn.pack(side=tk.LEFT, padx=10)
pc_stop_btn = tk.Button(pc_btn_frame, bg="#d32f2f", fg="white", font=("Arial", 11, "bold"), state=tk.DISABLED, command=lambda: mod_pc.stop_server_logic(log_to_console, update_progress, pc_start_btn, pc_stop_btn, ip_display_lbl)); pc_stop_btn.pack(side=tk.LEFT, padx=10)

# UNZERSTÖRBAR: Das gigantische IP-Label gut sichtbar unter den Knöpfen platziert!
ip_display_lbl = tk.Label(tab_pc, text="SERVER OFFLINE", font=("Arial", 14, "bold"), fg="gray", bg="#1a1a1a", pady=10)
ip_display_lbl.pack()

console_frame = tk.Frame(root, bg="#121212"); console_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
progress_frame = tk.Frame(console_frame, bg="#121212"); progress_frame.pack(fill=tk.X, pady=2)
progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=400, mode="determinate"); progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
progress_lbl = tk.Label(progress_frame, text="0%", fg="white", bg="#121212", font=("Arial", 9, "bold"), width=15); progress_lbl.pack(side=tk.RIGHT, padx=5)

console_box = tk.Text(console_frame, bg="#000000", fg="#39ff14", font=("Consolas", 10), state=tk.DISABLED, bd=0); console_box.pack(fill=tk.BOTH, expand=True, pady=5)
status_bar = tk.Label(root, bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#1a1a1a", fg="gray", font=("Arial", 9)); status_bar.pack(fill=tk.X, side=tk.BOTTOM)

mod_esp.refresh_board_list(board_dropdown, log_to_console)
refresh_ui_texts(); root.mainloop()
