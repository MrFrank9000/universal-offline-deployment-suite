===========================================================
 Universal Offline Deployment Suite - README & LEGAL NOTICE
===========================================================

[ENGLISH]
1. PURPOSE OF THIS SOFTWARE:
   This program does NOT contain any exploits, payloads, hacks, or jailbreak files!
   It is a completely blank server utility. It was created solely to help users 
   host their own web assets or external HTML exploit pages within a private local 
   network so that the console can remain 100% offline securely. The user must 
   provide their own source archive (.zip) containing the web assets.

2. EXTERNAL CREDITS & ATTRIBUTIONS (Required Open-Source Notice):
   - This application utilizes the official, open-source native C++ Arduino Core 
     and Espressif SDK frameworks to power the local Port 80 micro-webserver 
     on ESP8266 hardware dongles.
   - Filesystem compilation utilizes the mkspiffs toolchain binary (MIT License).
   - Hardware flashing routines are executed via esptool (GPL v2).

3. SUPPORTED HARDWARE & MODULE STATUS (v0.0.5-Test):
   - [PC SERVER] Local Server Module: fully functional on cross-platform Port 80.
   - [USB FLASH] Hardware Stick Flasher: fully functional on Port 80 with native SPIFFS deployment.
   - [APK BUILD] Android App Module: CURRENTLY PAUSED / UNDER CONSTRUCTION.

-----------------------------------------------------------

[DEUTSCH]
1. ZWECK DIESER SOFTWARE:
   Dieses Programm enthaelt keinerlei Exploits, Payloads, Hacks oder Jailbreak-Dateien!
   Es ist ein reines, leeres Server-Werkzeug. Es wurde ausschliesslich dafeur entwickelt, 
   um vom Nutzer selbst bereitgestellte Web-Dateien komfortabel im privaten Heimnetzwerk 
   zu hosten, damit die Konsole zu 100% offline bleiben kann.

2. EXTERNE CREDITS & QUELLENVERWEISE (Erforderlicher Open-Source-Hinweis):
   - Diese Anwendung nutzt den offiziellen, quelloffenen nativen C++ Arduino Core 
     und die Espressif Systemtreiber, um den lokalen Port-80-Mini-Webserver auf 
     ESP8266-WLAN-Sticks zu betreiben.
   - Die Dateisystem-Kompilierung nutzt das offizielle mkspiffs-Werkzeug (MIT-Lizenz).
   - Die Hardware-Flash-Routinen werden ueber das integrierte esptool (GPL v2) ausgefuehrt.

===========================================================
 HOW TO BUILD FROM SOURCE (MANUAL COMPILATION)
===========================================================

If you want to compile the standalone binary yourself instead of using the pre-built files, follow these native cross-platform instructions. Ensure you have **Python 3.10+** and **PyInstaller** installed.

### 🪟 1. Building on Windows
Open your Windows Command Prompt (CMD) or PowerShell inside the source directory and run:

1. Install the required serial drivers:
   ```bash
   pip install pyserial
   ```
2. Invoke PyInstaller to package the graphical interface into a single standalone executable:
   ```bash
   python -m PyInstaller --clean --noconsole --onefile --name="universal-offline-deployment-suite_v0.0.5-Test" gui_main.py
   ```
3. Your compiled standalone application will be located inside the generated `\dist\` folder.

### 🐧 2. Building on Linux
Open your Linux Terminal inside the source directory and run:

1. Install the required serial communication libraries (requires system packages permissions on modern distros):
   ```bash
   sudo python3 -m pip install pyserial --break-system-packages
   ```
2. Invoke the native Linux PyInstaller engine to generate an uncompressed standalone ELF binary:
   ```bash
   python3 -m PyInstaller --clean --noconsole --onefile --name="universal-offline-deployment-suite_v0.0.5-Linux" gui_main.py
   ```
3. Your native executable file will be located inside the generated `/dist/` directory. Grant execution permissions before running it:
   ```bash
   chmod +x dist/universal-offline-deployment-suite_v0.0.5-Linux
   ./dist/universal-offline-deployment-suite_v0.0.5-Linux
