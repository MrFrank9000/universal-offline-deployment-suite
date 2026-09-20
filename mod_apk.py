import os
import sys
import glob
import shutil
import zipfile
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog

selected_apk_zip_path = ""

def select_apk_zip_file(zip_label, log_callback):
    global selected_apk_zip_path
    file_path = filedialog.askopenfilename(filetypes=[("ZIP-Archive", "*.zip")])
    if file_path:
        selected_apk_zip_path = file_path
        zip_label.config(text=os.path.basename(file_path), fg="#39ff14")
        log_callback(f"[SYSTEM] APK ZIP source loaded: {file_path}\n")

def run_command_live(command, working_dir, log_callback, root):
    process = subprocess.Popen(command, shell=True, cwd=working_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    for line in process.stdout:
        log_callback(line)
        root.update_idletasks()
    process.stdout.close()
    return process.wait()

def build_apk_logic(update_progress, log_callback, build_btn, zip_btn, root):
    global selected_apk_zip_path
    try:
        build_btn.config(state=tk.DISABLED); zip_btn.config(state=tk.DISABLED)
        log_callback('=== STARTING DYNAMIC APK BUILD STATION ===\n\n', clear=True)
        if not selected_apk_zip_path or not os.path.exists(selected_apk_zip_path):
            log_callback('ERROR: No ZIP file selected!\n')
            update_progress(0, 'ZIP missing!'); return
        true_base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        app_dir = os.path.join(true_base_dir, 'android_app')
        android_dir = os.path.join(app_dir, 'android'); www_dir = os.path.join(app_dir, 'www')
        java_home = r'C:\Program Files\Android\Android Studio\jbr'
        android_home = os.path.join(os.environ['LOCALAPPDATA'], 'Android', 'Sdk')
        os.environ['JAVA_HOME'] = java_home; os.environ['ANDROID_HOME'] = android_home
        os.environ['PATH'] = os.path.join(java_home, 'bin') + os.path.pathsep + os.environ['PATH']
        if not os.path.exists(app_dir):
            log_callback('[SYSTEM] Generating skeleton...\n')
            os.makedirs(www_dir, exist_ok=True)
            with open(os.path.join(www_dir, 'index.html'), 'w') as f: f.write('<body><h1>Offline Web Host</h1></body>')
            run_command_live('npm init -y', app_dir, log_callback, root)
            run_command_live('npm install @capacitor/core @capacitor/cli @capacitor/android --save-dev --no-audit --no-fund', app_dir, log_callback, root)
            run_command_live('npx cap init "Offline Web Host" com.anonymous.localhost --web-dir=www', app_dir, log_callback, root)
            run_command_live('npx cap add android', app_dir, log_callback, root)
            props_path = os.path.join(app_dir, 'android', 'gradle.properties')
            if os.path.exists(props_path):
                with open(props_path, 'a') as f: f.write('\nandroid.useAndroidX=true\nandroid.enableJetifier=true\n')
        log_callback(f'[SYSTEM] Extracting: {os.path.basename(selected_apk_zip_path)}\n')
        temp_extract = os.path.join(os.environ['TEMP'], 'apk_manual_web_extracted')
        if os.path.exists(temp_extract): shutil.rmtree(temp_extract)
        with zipfile.ZipFile(selected_apk_zip_path, 'r') as zip_ref: zip_ref.extractall(temp_extract)
        if os.path.exists(www_dir): shutil.rmtree(www_dir)
        os.makedirs(www_dir, exist_ok=True)
        ext_c = os.listdir(temp_extract)
        if ext_c:
            src_folder = os.path.join(temp_extract, ext_c)
            if os.path.isdir(src_folder):
                for item in os.listdir(src_folder):
                    s = os.path.join(src_folder, item); d = os.path.join(www_dir, item)
                    shutil.copytree(s, d, dirs_exist_ok=True) if os.path.isdir(s) else shutil.copy2(s, d)
        shutil.rmtree(temp_extract)
        run_command_live('npx cap sync android', app_dir, log_callback, root)
        run_command_live('.\\gradlew --stop', android_dir, log_callback, root)
        build_result = run_command_live(f'.\\gradlew assembleDebug -Dorg.gradle.java.home="{java_home}"', android_dir, log_callback, root)
        generated_apk = os.path.join(android_dir, 'app', 'build', 'outputs', 'apk', 'debug', 'app-debug.apk')
        if os.path.exists(generated_apk) and build_result == 0:
            update_progress(100, 'APK compiled successfully!')
            final_export_path = os.path.join(true_base_dir, 'offline_web_host_server.apk')
            shutil.copy2(generated_apk, final_export_path)
            log_callback(f'\n=======================================================\n 🎉 SUCCESS! Standalone APK created!\n File exported to: {final_export_path}\n=======================================================\n')
        else: log_callback('\nERROR: Build failed.\n')
    except Exception as e: log_callback(f'\n[SYSTEM ERROR]: {str(e)}\n')
    finally: build_btn.config(state=tk.NORMAL); zip_btn.config(state=tk.NORMAL)

def start_apk_thread(update_progress, log_callback, build_btn, zip_btn, root):
    threading.Thread(target=build_apk_logic, args=(update_progress, log_callback, build_btn, zip_btn, root), daemon=True).start()
