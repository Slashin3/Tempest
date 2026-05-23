import os
import sys
import subprocess
import win32com.client

# ─────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────
TARGET_GAME = "FAREVER.exe"

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Point this to your main compiled tracking dashboard app
TRACKER_APP_EXE = os.path.join(BASE_DIR, "tempest_dashboard.exe")


def monitor_system_events():
    """ Registers an asynchronous event sink directly with the Windows Kernel """
    print("[Engine] Connecting to Windows Management Instrumentation...")
    
    # Initialize the COM library connection to the local machine root
    wmi = win32com.client.GetObject("winmgmts:\\\\.\\root\\cimv2")
    
    # Subscribe to Process Creation Events specifically filtering for our target
    # This instructs the kernel to notify us instantly when the game opens
    query = f"SELECT * FROM __InstanceCreationEvent WITHIN 1 WHERE TargetInstance ISA 'Win32_Process' AND TargetInstance.Name = '{TARGET_GAME}'"
    event_watcher = wmi.ExecNotificationQuery(query)

    print(f"[Engine] Native event sink active. Awaiting {TARGET_GAME}...")

    while True:
        try:
            # This line completely blocks execution and consumes ZERO CPU cycles.
            # It sleeps until the Windows Kernel explicitly fires the event.
            new_process_event = event_watcher.NextEvent()
            process_details = new_process_event.TargetInstance
            
            print(f"[Engine] Match Found! PID {process_details.ProcessId} detected. Spawning Tracker...")
            
            # Fire up your main dashboard UI completely detached from this watcher
            subprocess.Popen([TRACKER_APP_EXE], creationflags=subprocess.CREATE_NEW_CONSOLE)
            
        except Exception as e:
            print(f"[Engine] Critical Callback Exception: {e}")


if __name__ == "__main__":
    # If compiled as a windowless binary (.exe via PyInstaller with --noconsole)
    # this will operate completely silently in the background using less than 8MB of RAM.
    monitor_system_events()