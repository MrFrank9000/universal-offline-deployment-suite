import os, sys, glob, shutil, zipfile, subprocess, threading, tkinter as tk
from tkinter import filedialog
selected_apk_zip_path = ""
def select_apk_zip_file(lbl, log):
    global selected_apk_zip_path
    f = filedialog.askopenfilename(filetypes=[("ZIP-Archive", "*.zip")])
    if f: selected_apk_zip_path = f; lbl.config(text=os.path.basename(f), fg="#39ff14"); log(f"[SYSTEM] Loaded: {f}\n")
def run_command_live(cmd, wd, log, root):
    p = subprocess.Popen(cmd, shell=True, cwd=wd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    for line in p.stdout: log(line); root.update_idletasks()
    p.stdout.close(); return p.wait()
def build_apk_logic(update_progress, log_callback, build_btn, zip_btn, root):
    global selected_apk_zip_path
    try:
        build_btn.config(state=tk.DISABLED); zip_btn.config(state=tk.DISABLED)
        log_callback('=== STARTING SERVER-BASED APK BUILD STATION ===\n\n', clear=True)
        if not selected_apk_zip_path:
            base_check = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            zip_candidates = glob.glob(os.path.join(base_check, '*.zip'))
            if zip_candidates: selected_apk_zip_path = zip_candidates[0]
        if not selected_apk_zip_path or not os.path.exists(selected_apk_zip_path):
            log_callback('ERROR: No ZIP file selected or found!\n'); update_progress(0, 'ZIP missing!'); return
        true_base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        app_dir = os.path.join(true_base_dir, 'android_app')
        android_dir = os.path.join(app_dir, 'android'); www_dir = os.path.join(app_dir, 'www')
        java_home = r'C:\Program Files\Android\Android Studio\jbr'
        android_home = os.path.join(os.environ['LOCALAPPDATA'], 'Android', 'Sdk')
        os.environ['JAVA_HOME'] = java_home; os.environ['ANDROID_HOME'] = android_home
        os.environ['PATH'] = os.path.join(java_home, 'bin') + os.path.pathsep + os.environ['PATH']
        if not os.path.exists(app_dir):
            log_callback('[SYSTEM] Generating framework skeleton...\n'); os.makedirs(www_dir, exist_ok=True)
            run_command_live('npm init -y', app_dir, log_callback, root)
            run_command_live('npm install @capacitor/core @capacitor/cli @capacitor/android --save-dev --no-audit --no-fund', app_dir, log_callback, root)
            run_command_live('npx cap init "Offline Web Host" com.anonymous.localhost --web-dir=www', app_dir, log_callback, root)
            run_command_live('npx cap add android', app_dir, log_callback, root)
        strings_path = os.path.join(android_dir, 'app', 'src', 'main', 'res', 'values', 'strings.xml')
        if os.path.exists(strings_path):
            with open(strings_path, 'w', encoding='utf-8') as f:
                f.write("<?xml version='1.0' encoding='utf-8'?>\n<resources>\n    <string name=\"app_name\">Offline Web Host</string>\n    <string name=\"title_activity_main\">Offline Web Host</string>\n    <string name=\"package_name\">com.anonymous.localhost</string>\n</resources>")
        java_main_path = os.path.join(android_dir, 'app', 'src', 'main', 'java', 'com', 'anonymous', 'localhost', 'MainActivity.java')
        os.makedirs(os.path.dirname(java_main_path), exist_ok=True)
        with open(java_main_path, 'w', encoding='utf-8') as f:
            f.write("package com.anonymous.localhost;\nimport android.os.Bundle;\nimport android.webkit.JavascriptInterface;\nimport android.webkit.WebView;\nimport com.getcapacitor.BridgeActivity;\nimport java.net.InetAddress;\nimport java.net.NetworkInterface;\nimport java.util.Collections;\nimport java.util.List;\npublic class MainActivity extends BridgeActivity {\n    @Override\n    protected void onCreate(Bundle savedInstanceState) {\n        super.onCreate(savedInstanceState);\n        WebView w = getBridge().getWebView();\n        w.getSettings().setJavaScriptEnabled(true);\n        w.addJavascriptInterface(new Object() {\n            @JavascriptInterface\n            public String getDeviceIp() {\n                try {\n                    for (NetworkInterface n : Collections.list(NetworkInterface.getNetworkInterfaces())) {\n                        for (InetAddress a : Collections.list(n.getInetAddresses())) {\n                            if (!a.isLoopbackAddress() && a.getHostAddress().indexOf(':')<0) return a.getHostAddress();\n                        }\n                    }\n                } catch (Exception e) { }\n                return \"192.168.X.X\";\n            }\n        }, \"AndroidInterface\");\n    }\n}")
        os.makedirs(www_dir, exist_ok=True)
        dashboard_html = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'><style>body { background-color: #121216; color: #ffffff; font-family: 'Segoe UI', sans-serif; text-align: center; padding: 30px 15px; }.version-badge { color: #ff8f00; font-weight: bold; font-size: 14px; background-color: rgba(255,143,0,0.1); padding: 5px 15px; border-radius: 20px; display: inline-block; margin-bottom: 10px; border: 1px solid rgba(255,143,0,0.3); }.card { background-color: #161620; border-radius: 8px; padding: 25px; margin: 10px auto; max-width: 500px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }h1 { color: #0080ff; font-size: 22px; margin-bottom: 5px; }.ip-box { font-family: monospace; background-color: #0d0d11; color: #39ff14; padding: 15px; border-radius: 4px; font-size: 20px; margin: 15px 0; word-break: break-all; font-weight: bold; }p { color: #aaaaaa; font-size: 14px; line-height: 1.5; }</style></head><body><div class='version-badge'>v1.1.0-AUTOMATIC-IP</div><div class='card'><h1>Offline Web Host Server</h1><p>Server active on Port 80. Your smartphone Wi-Fi IP address has been detected automatically:</p><div class='ip-box' id='ipServer'>Detecting IP address...</div><p><strong>Instructions:</strong><br>1. Connect your console to this smartphone Wi-Fi hotspot.<br>2. Type the green URL address above into your console web browser.</p></div><script>function setDetectedIp(ip) { document.getElementById("ipServer").innerText = "http://" + ip; }window.addEventListener('DOMContentLoaded', () => { if (window.AndroidInterface && window.AndroidInterface.getDeviceIp) { setDetectedIp(window.AndroidInterface.getDeviceIp()); } });</script></body></html>"""
        with open(os.path.join(www_dir, 'index.html'), 'w', encoding='utf-8') as f: f.write(dashboard_html)
        log_callback(f'[SYSTEM] Extracting archive: {os.path.basename(selected_apk_zip_path)}\n'); update_progress(25, 'Processing server assets...')
        temp_extract = os.path.join(os.environ['TEMP'], 'apk_manual_web_extracted')
        if os.path.exists(temp_extract): shutil.rmtree(temp_extract)
        with zipfile.ZipFile(selected_apk_zip_path, 'r') as zip_ref: zip_ref.extractall(temp_extract)
        assets_target_dir = os.path.join(android_dir, 'app', 'src', 'main', 'assets', 'public')
        if os.path.exists(assets_target_dir): shutil.rmtree(assets_target_dir)
        os.makedirs(assets_target_dir, exist_ok=True)
        ext_c = os.listdir(temp_extract)
        if ext_c:
            src_folder = os.path.join(temp_extract, ext_c[0])
            if os.path.isdir(src_folder):
                for item in os.listdir(src_folder):
                    s = os.path.join(src_folder, item); d = os.path.join(assets_target_dir, item)
                    shutil.copytree(s, d, dirs_exist_ok=True) if os.path.isdir(s) else shutil.copy2(s, d)
        shutil.rmtree(temp_extract)
        run_command_live('npx cap sync android', app_dir, log_callback, root)
        run_command_live('.\\gradlew --stop', android_dir, log_callback, root)
        update_progress(75, 'Compiling product APK package...')
        build_result = run_command_live(f'.\\gradlew assembleDebug -Dorg.gradle.java.home="{java_home}"', android_dir, log_callback, root)
        generated_apk = os.path.join(android_dir, 'app', 'build', 'outputs', 'apk', 'debug', 'app-debug.apk')
        if os.path.exists(generated_apk) and build_result == 0:
            update_progress(100, 'APK compiled successfully!')
            shutil.copy2(generated_apk, os.path.join(true_base_dir, 'universal-offline-deployment-suite.apk'))
            log_callback('\n=======================================================\n 🎉 SUCCESS! Server-based APK with Automatic IP created!\n=======================================================\n')
        else: log_callback('\nERROR: Build failed.\n')
    except Exception as e: log_callback(f'\n[SYSTEM ERROR]: {str(e)}\n')
    finally: build_btn.config(state=tk.NORMAL); zip_btn.config(state=tk.NORMAL)
def start_apk_thread(p_bar, log, b_btn, z_btn, root): threading.Thread(target=build_apk_logic, args=(p_bar, log, b_btn, z_btn, root), daemon=True).start()
