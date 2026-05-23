import os
import sys
import subprocess
import win32com.client

# ─────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────
TARGET_GAME = "FAREVER.exe"
DASHBOARD_PROCESS_NAME = "TempestApp.exe"  # Match your compiled name

if getattr(sys, 'frozen', False):
    # Moving up one level because it sits inside a subdirectory in --onedir mode
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(sys.executable)))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Match the exact executable name from your PyInstaller build
TRACKER_APP_EXE = os.path.join(BASE_DIR, "TempestApp.exe")


def is_dashboard_already_running():
    """ 
    Queries local Win32 processes to see if the dashboard is already open.
    Prevents spawning duplicate tracking windows if the game restarts.
    """
    wmi = win32com.client.GetObject("winmgmts:\\\\.\\root\\cimv2")
    processes = wmi.ExecQuery(f"SELECT * FROM Win32_Process WHERE Name = '{DASHBOARD_PROCESS_NAME}'")
    return len(processes) > 0


def monitor_system_events():
    """ Registers an asynchronous event sink directly with the Windows Kernel """
    print("[Engine] Connecting to Windows Management Instrumentation...")
    
    wmi = win32com.client.GetObject("winmgmts:\\\\.\\root\\cimv2")
    
    # Kernel-level subscription: 0% CPU footprint while waiting
    query = f"SELECT * FROM __InstanceCreationEvent WITHIN 1 WHERE TargetInstance ISA 'Win32_Process' AND TargetInstance.Name = '{TARGET_GAME}'"
    event_watcher = wmi.ExecNotificationQuery(query)

    print(f"[Engine] Native event sink active. Awaiting {TARGET_GAME}...")

    while True:
        try:
            # Completely blocks execution until the Windows Kernel hooks a match
            new_process_event = event_watcher.NextEvent()
            process_details = new_process_event.TargetInstance
            
            print(f"[Engine] Match Found! {TARGET_GAME} (PID {process_details.ProcessId}) detected.")
            
            # CRITICAL SAFETY CHECK: Don't spawn a duplicate UI if one is already running
            if not is_dashboard_already_running():
                print("[Engine] Dashboard not running. Spawning clean instance...")
                subprocess.Popen([TRACKER_APP_EXE], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                print("[Engine] Dashboard instance already active. Ignoring trigger.")
                
        except Exception as e:
            print(f"[Engine] Critical Callback Exception: {e}")


if __name__ == "__main__":
    monitor_system_events()