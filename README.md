# Tempest - Dungeon Boss Tracker

Tempest is a desktop application designed to track dungeon boss runs and kill statistics. Built with Python and Tkinter, it provides a clean, real-time user interface to log your gameplay data and keep track of your run histories efficiently.

<img width="1907" height="1009" alt="image" src="https://github.com/user-attachments/assets/e913eb75-bb95-49df-8333-2319b968d16d" />


## 🚀 Download & Run (For Users)

You do not need Python or Git installed to use Tempest. You can download the ready-to-run Windows standalone application:

1. Go to the [Releases](https://github.com/Slashin3/Tempest/releases) page.
2. Download the latest `Tempest-v1.0.0-Windows.rar` file.
3. Extract the RAR file anywhere on your PC using WinRAR or 7-Zip.
4. Open the extracted folder, find `tempest.exe` (with the blue storm vortex icon), and double-click to run!

---

## Features
* **Real-time Kill Counters:** Track individual boss kills (e.g., Crabgantua, Nepsilon, Reblochon) with a single glance.
* **Live Run Logging:** View recent dungeon run logs dynamically.
* **Persistent State:** Saves your progress so you can pick up right where you left off.
* **Custom UI:** Sleek, dark-themed dashboard tailored for focus during gameplay.

---

## 🛠️ Development & Setup (For Developers)

If you want to run the application from source code or modify it:

### Prerequisites
Make sure you have Python 3.x installed on your system. Verify it by running:
```bash
python --version
Installation
Clone the repository:

Bash
git clone [https://github.com/Slashin3/Tempest.git](https://github.com/Slashin3/Tempest.git)
cd Tempest
Install dependencies (if applicable):

Bash
pip install -r requirements.txt
Running the Source Code
Bash
python tempest.py
Compiling Your Own Executable
To bundle the source code back into a Windows application folder after making changes:

Bash
pip install pyinstaller
pyinstaller --noconfirm --onedir --windowed --icon="tempest.ico" "tempest.py"
The compilation output will be generated inside the dist/ directory.
