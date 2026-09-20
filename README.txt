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

2. SUPPORTED HARDWARE & MODULE STATUS (v0.0.4-Test):
   - [PC SERVER] Local Server Module: fully functional on cross-platform Port 80.
   - [USB FLASH] Hardware Stick Flasher: fully functional on Port 80 with auto-OS scan.
     Supports: ESP8266, ESP8266EX, ESP32, ESP32-S2, ESP32-S3, ESP32-C3.
   - [APK BUILD] Android App Module: CURRENTLY PAUSED / UNDER CONSTRUCTION.
     This feature is temporarily disabled in this build for technical optimization.

3. HOW TO BUILD FROM SOURCE (For Developers):
   You can easily compile this application from source code on both Windows and Linux.
   
   Prerequisites:
   - Python 3.x installed
   - Standard package manager (pip) active
   
   Step 1: Install required developer dependencies:
           pip install pyserial pyinstaller
           
   Step 2: Navigate into the source directory:
           cd suite_src
           
   Step 3: Run the compiler command for your operating system:
           [Windows]: python -m PyInstaller --clean --noconsole --onefile --name="universal-offline-deployment-suite" gui_main.py
           [Linux]  : python3 -m PyInstaller --clean --noconsole --onefile --name="universal-offline-deployment-suite" gui_main.py

4. DISCLAIMER / NO LIABILITY:
   This software is provided "as-is", without warranty of any kind. The developer 
   assumes absolutely no responsibility or liability for any potential damages, 
   data loss, or crashes on your console or computer system. Use at your own risk.

5. LICENSE:
   This project is public domain. Feel free to use, modify, expand, and redistribute.

-----------------------------------------------------------

[DEUTSCH]
1. ZWECK DIESER SOFTWARE:
   Dieses Programm enthaelt keinerlei Exploits, Payloads, Hacks oder Jailbreak-Dateien!
   Es ist ein reines, leeres Server-Werkzeug. Es wurde ausschliesslich dafeur entwickelt, 
   um vom Nutzer selbst bereitgestellte Web-Dateien komfortabel im privaten Heimnetzwerk 
   zu hosten, damit die Konsole zu 100% offline bleiben kann. Der Anwender muss sein 
   eigenes Quell-Archiv (.zip) mit den Web-Assets mitbringen.

2. UNTERSTUETZTE HARDWARE & MODUL-STATUS (v0.0.4-Test):
   - [PC SERVER] Lokaler Server-Reiter: Voll einsatzbereit auf Cross-Platform Port 80.
   - [USB FLASH] Hardware Stick Flasher: Voll einsatzbereit auf Port 80 mit Auto-OS-Erkennung.
     Unterstuetzt: ESP8266, ESP8266EX, ESP32, ESP32-S2, ESP32-S3, ESP32-C3.
   - [APK BUILD] Android App-Reiter: AKTUELL PAUSIERT / IN ARBEIT.
     Dieses Feature ist in dieser Testversion fuer Optimierungen temporaer deaktiviert.

3. BAUANLEITUNG AUS DEM QUELLCODE (Fuer Entwickler):
   Du kannst diese Anwendung ganz einfach aus den Skripten heraus unter Windows und Linux selbst compilieren.
   
   Voraussetzungen:
   - Python 3.x installiert
   - Standard-Paketmanager (pip) aktiv
   
   Schritt 1: Installiere die benoetigten Abhaengigkeiten:
              pip install pyserial pyinstaller
              
   Schritt 2: Wechsle in das Quellcode-Verzeichnis:
              cd suite_src
              
   Schritt 3: Starte den Compiler-Befehl fuer dein Betriebssystem:
              [Windows]: python -m PyInstaller --clean --noconsole --onefile --name="universal-offline-deployment-suite" gui_main.py
              [Linux]  : python3 -m PyInstaller --clean --noconsole --onefile --name="universal-offline-deployment-suite" gui_main.py

4. HAFTUNGSAUSSCHLUSS:
   Diese Software wird ohne Maengelgewaehr zur Verfuegung gestellt. Der Entwickler 
   uebernimmt absolut keine Haftung oder Verantwortung fuer eventuelle Schaeden, 
   Systemabstuerze oder Datenverlust an deiner Konsole oder deinem Computer! 
   Die Nutzung erfolgt vollstaendig auf eigene Gefahr.

5. LIZENZ:
   Dieses Projekt ist gemeinfrei (Public Domain). Du kannst die Skripte nach Belieben 
   veraendern, erweitern und teilen!
===========================================================
