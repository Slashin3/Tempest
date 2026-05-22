import cv2
import numpy as np
import mss
import pytesseract
import pygetwindow as gw
import time
import tkinter as tk
from tkinter import ttk  
from tkinter import messagebox
import json
import os
import sys
import threading
from datetime import datetime
import difflib
import re

# ─────────────────────────────────────────────────────────────
# TESSERACT PORTABLE & ENVIRONMENT SETUP
# ─────────────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    pytesseract.pytesseract.tesseract_cmd = os.path.join(base_path, "tesseract", "tesseract.exe")
else:
    if "TESSERACT_CMD" in os.environ:
        pytesseract.pytesseract.tesseract_cmd = os.environ["TESSERACT_CMD"]
    elif os.path.exists(r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ─────────────────────────────────────────────────────────────
# STORAGE BOUNDS
# ─────────────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    EXE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    EXE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(EXE_DIR, "farever_ocr_runs.json")

# ─────────────────────────────────────────────────────────────
# DUNGEON LOOT MATRIX (Updated with Type Tags)
# ─────────────────────────────────────────────────────────────
BOSS_LOOT_POOLS = {
    "Crabgantua": [
        "Clawdius", "Crabgantua's Kneecap", "Poetrident",
        "Crown of the Sea", "Abyssal Shoulderplates", "Fin Armor", "Jenny Hanibal's Armored Cape", "Palm of the Lagoon", "Vesture of the Mussel Hunter", "Boots of Abyssal Essence",
        "Tides Hood", "Fins of the First Fish", "Delicate Marine Aiglets", "Cloak of the Third Wave Apostle", "Wings of the Prophet", "Ceremonial Siren Gloves", "Emblem of the Third Wave", "Ceremonial Nepsid Belt", "Spare Sandals of Young Nephisto",
        "Submarine Torpedo Helmet", "Jacket of the Last Pirate", "Burden of the Abyss", "Nepicur's Vacation Shorts", "Bleak Shell's Knee Pads",
        "Charm of the Fisher King", "High-speed Clamdiggers", "Meropsian Crab (mount)", "Antelimbian Crab (mount)"
    ],
    "Nepsilon": [
        "Iron Fins of the Leviathan", "Ghost Clams of the Low Tide", "Poetrident",
        "Crown of the Sea", "Abyssal Shoulderplates", "Fin Armor", "Jenny Hanibal's Armored Cape", "Palm of the Lagoon", "Vesture of the Mussel Hunter", "Boots of Abyssal Essence",
        "Tides Hood", "Fins of the First Fish", "Delicate Marine Aiglets", "Cloak of the Third Wave Apostle", "Wings of the Prophet", "Ceremonial Siren Gloves", "Emblem of the Third Wave", "Ceremonial Nepsid Belt", "Spare Sandals of Young Nephisto",
        "Submarine Torpedo Helmet", "Jacket of the Last Pirate", "Burden of the Abyss", "Nepicur's Vacation Shorts", "Bleak Shell's Knee Pads",
        "Charm of the Fisher King", "High-speed Clamdiggers", "Antelimbian Wingfish (glider)"
    ],
    "Reblochonk": [
        "Cheese Moon", "Flame of Argol", "Raclette Pan",
        "Armored Docker Cap", "Miner Ramparts", "Brie von de Cape", "Diskobold's Discus Throw Gloves", "Unity of the Thirty Kingdoms", "Wrong Trousers", "Buskins of Essential Emptiness",
        "Vision of the Cheeseslicer", "Dust Scarf", "Treasure Hunter's Straps", "Spirit of the Spelunker", "Vows of Prosperity", "Garment of the Aurock Master", "Rat-Vachol's Patched Up Pants", "Gold Pouches",
        "Cheese Covered Shoulderpads", "Reversible Bib of the Cheese Taster", "Gloves of Ninkilim the Envoy", "Relic of the Four Hundred", "Spelunking Shoes of Emmen Tunnel",
        "Goldilock's Thrice Latched Jacket", "Mystical Placemat of the Gourmet", "Knotr'Edam", "Navelian Bat (glider)"
    ],
    "King Ratsar": [
        "Judgement", "Twin Fangs of Ratsar", "Raclette Pan",
        "Armored Docker Cap", "Miner Ramparts", "Brie von de Cape", "Diskobold's Discus Throw Gloves", "Unity of the Thirty Kingdoms", "Wrong Trousers", "Buskins of Essential Emptiness",
        "Vision of the Cheeseslicer", "Dust Scarf", "Treasure Hunter's Straps", "Spirit of the Spelunker", "Vows of Prosperity", "Garment of the Aurock Master", "Rat-Vachol's Patched Up Pants", "Gold Pouches",
        "Cheese Covered Shoulderpads", "Reversible Bib of the Cheese Taster", "Gloves of Ninkilim the Envoy", "Relic of the Four Hundred", "Spelunking Shoes of Emmen Tunnel",
        "Goldilock's Thrice Latched Jacket", "Mystical Placemat of the Gourmet", "Knotr'Edam", "Krisomalese Bat (glider)"
    ],
    "Gatsbee": [
        "Thornlace", "Lady Bee's Ceremonial Stinger", "Eternal Flower Heart",
        "Royal Chamber Helmet", "Queen Spikes", "Whirring Gem of Apix", "Reflective Vest of the Hive Worker", "Gauntlets of the Royal Guard", "Flying Trousers Prototype", "Melain's Golden Greaves",
        "Scout Antennae", "Vision of the Beekeeper", "Hive Sprouts", "Casual Clothes of the Pollincess", "Veil of the Royal Nymph", "Vambraces of the Swarm", "Dancing Hivetree Belt", "Zenobee's Breeches", "War Sabatons of Apix",
        "Beewings", "Emblem of Radiant Nectar", "Flight of the Rumblebee", "Propolis Heart of Apix", "Silhouette of Apix",
        "Palmaryllis", "Cleo's Ethereal Blossoms", "Semeruian Moth (glider)", "Zerzurean Leggybug (mount)"
    ],
    "Lady Bee": [
        "Ipheion, Star Blossom", "Beefury, Blessed Blade of the Farseeker", "Eternal Flower Heart",
        "Royal Chamber Helmet", "Queen Spikes", "Whirring Gem of Apix", "Reflective Vest of the Hive Worker", "Gauntlets of the Royal Guard", "Flying Trousers Prototype", "Melain's Golden Greaves",
        "Scout Antennae", "Vision of the Beekeeper", "Hive Sprouts", "Casual Clothes of the Pollincess", "Veil of the Royal Nymph", "Vambraces of the Swarm", "Dancing Hivetree Belt", "Zenobee's Breeches", "War Sabatons of Apix",
        "Beewings", "Emblem of Radiant Nectar", "Flight of the Rumblebee", "Propolis Heart of Apix", "Silhouette of Apix",
        "Palmaryllis", "Cleo's Ethereal Blossoms", "Zerzurean Leggybug (mount)", "Nescentine Leggybug (mount)"
    ],
    "Golcano": [
        "Magma Mia", "Gorgon Ratsay's Toothpick", "Raclette Pan",
        "Armored Docker Cap", "Miner Ramparts", "Brie von de Cape", "Diskobold's Discus Throw Gloves", "Unity of the Thirty Kingdoms", "Wrong Trousers", "Buskins of Essential Emptiness",
        "Vision of the Cheeseslicer", "Dust Scarf", "Treasure Hunter's Straps", "Spirit of the Spelunker", "Vows of Prosperity", "Garment of the Aurock Master", "Rat-Vachol's Patched Up Pants", "Gold Pouches",
        "Cheese Covered Shoulderpads", "Reversible Bib of the Cheese Taster", "Gloves of Ninkilim the Envoy", "Relic of the Four Hundred", "Spelunking Shoes of Emmen Tunnel",
        "Goldilock's Thrice Latched Jacket", "Mystical Placemat of the Gourmet", "Knotr'Edam", "Ebral Dragoon (glider)"
    ],
    "Sponge Blob": [
        "Book of Mi'Mizan", "Horns of the Wind", "Poetrident",
        "Crown of the Sea", "Abyssal Shoulderplates", "Fin Armor", "Jenny Hanibal's Armored Cape", "Palm of the Lagoon", "Vesture of the Mussel Hunter", "Boots of Abyssal Essence",
        "Tides Hood", "Fins of the First Fish", "Delicate Marine Aiglets", "Cloak of the Third Wave Apostle", "Wings of the Prophet", "Ceremonial Siren Gloves", "Emblem of the Third Wave", "Ceremonial Nepsid Belt", "Spare Sandals of Young Nephisto",
        "Submarine Torpedo Helmet", "Jacket of the Last Pirate", "Burden of the Abyss", "Nepicur's Vacation Shorts", "Bleak Shell's Knee Pads",
        "Charm of the Fisher King", "High-speed Clamdiggers", "Acidic Wingfish (glider)"
    ],
    "Queen Honeyzabeth": [
        "Wingsabers", "Pocket Hive", "Eternal Flower Heart",
        "Royal Chamber Helmet", "Queen Spikes", "Whirring Gem of Apix", "Reflective Vest of the Hive Worker", "Gauntlets of the Royal Guard", "Flying Trousers Prototype", "Melain's Golden Greaves",
        "Scout Antennae", "Vision of the Beekeeper", "Hive Sprouts", "Casual Clothes of the Pollincess", "Veil of the Royal Nymph", "Vambraces of the Swarm", "Dancing Hivetree Belt", "Zenobee's Breeches", "War Sabatons of Apix",
        "Beewings", "Emblem of Radiant Nectar", "Flight of the Rumblebee", "Propolis Heart of Apix", "Silhouette of Apix",
        "Palmaryllis", "Cleo's Ethereal Blossoms", "Zerzurean Leggybug (mount)", "Ponogian Leggybug (mount)"
    ],
    "Munster Chuck": [
        "Twin Pillars of Justice", "Amon Ram, the Creator", "Raclette Pan",
        "Armored Docker Cap", "Miner Ramparts", "Brie von de Cape", "Diskobold's Discus Throw Gloves", "Unity of the Thirty Kingdoms", "Wrong Trousers", "Buskins of Essential Emptiness",
        "Vision of the Cheeseslicer", "Dust Scarf", "Treasure Hunter's Straps", "Spirit of the Spelunker", "Vows of Prosperity", "Garment of the Aurock Master", "Rat-Vachol's Patched Up Pants", "Gold Pouches",
        "Cheese Covered Shoulderpads", "Reversible Bib of the Cheese Taster", "Gloves of Ninkilim the Envoy", "Relic of the Four Hundred", "Spelunking Shoes of Emmen Tunnel",
        "Goldilock's Thrice Latched Jacket", "Mystical Placemat of the Gourmet", "Knotr'Edam", "Rinuhrian Skunk (mount)"
    ]
}

VALID_WEAPONS = {
    "Iron Fins of the Leviathan", "Ghost Clams of the Low Tide", "Cheese Moon", 
    "Flame of Argol", "Clawdius", "Crabgantua's Kneecap", "Judgement", 
    "Twin Fangs of Ratsar", "Thornlace", "Lady Bee's Ceremonial Stinger", 
    "Ipheion, Star Blossom", "Beefury, Blessed Blade of the Farseeker", 
    "Magma Mia", "Gorgon Ratsay's Toothpick", "Book of Mi'Mizan", 
    "Horns of the Wind", "Wingsabers", "Pocket Hive", 
    "Twin Pillars of Justice", "Amon Ram, the Creator", "Poetrident", "Raclette Pan", "Eternal Flower Heart"
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f: return json.load(f)
        except Exception: pass
    return {"runs": [], "total": 0}

def save_data(data_to_save):
    with open(DATA_FILE, "w") as f: json.dump(data_to_save, f, indent=2)

# ─────────────────────────────────────────────────────────────
# APPLICATION INITIALIZATION STATE
# ─────────────────────────────────────────────────────────────
data = load_data()
tracker_armed = True
current_active_boss = "Unknown Boss"

windows = gw.getWindowsWithTitle("Farever")
if not windows:
    print("Error: Farever window must be running to start tracking!")
    sys.exit()

game = windows[0]

def on_closing():
    try: root.destroy()
    except Exception: pass
    os._exit(0)

root = tk.Tk()
root.withdraw()

if sys.platform.startswith('win'):
    root.iconbitmap(default=sys.executable)

root.protocol("WM_DELETE_WINDOW", on_closing)

# ─────────────────────────────────────────────────────────────
# GRAPHICAL DASHBOARD UI COMPONENT
# ─────────────────────────────────────────────────────────────
class Dashboard(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Tempest - Dungeon Tracker")
        self.geometry("900x680")
        self.configure(bg="#11111d")
        self.protocol("WM_DELETE_WINDOW", on_closing)
        
        self.current_view_mode = "ALL"

        if sys.platform.startswith('win'):
            if getattr(sys, 'frozen', False):
                self.iconbitmap(sys.executable)
            else:
                if os.path.exists("tempest.ico"):
                    self.iconbitmap("tempest.ico")

        tk.Label(self, text="Dungeon Boss Tracker", bg="#11111d", fg="#f0c040", font=("Segoe UI", 14, "bold")).pack(pady=5)
        self.status_lbl = tk.Label(self, text="Waiting...", bg="#11111d", fg="#888888", font=("Segoe UI", 11))
        self.status_lbl.pack(pady=2)

        main_frame = tk.Frame(self, bg="#11111d")
        main_frame.pack(fill="both", expand=True, padx=15, pady=10)

        left_frame = tk.Frame(main_frame, bg="#171725", width=240)
        left_frame.pack(side="left", fill="both", padx=(0, 10))
        left_frame.pack_propagate(False)

        tk.Label(left_frame, text="KILL COUNTERS", bg="#171725", fg="#f0c040", font=("Segoe UI", 10, "bold")).pack(pady=8)

        self.counter_tree = ttk.Treeview(left_frame, columns=("boss", "count"), show="headings", height=15)
        self.counter_tree.heading("boss", text="Boss Name")
        self.counter_tree.heading("count", text="Kills")
        self.counter_tree.column("boss", width=160, anchor="w")
        self.counter_tree.column("count", width=60, anchor="center")
        self.counter_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.counter_tree.bind("<<TreeviewSelect>>", self.on_boss_selected)

        right_frame = tk.Frame(main_frame, bg="#11111d")
        right_frame.pack(side="right", fill="both", expand=True)

        log_header_frame = tk.Frame(right_frame, bg="#11111d")
        log_header_frame.pack(fill="x", pady=(0, 5))

        self.log_title_lbl = tk.Label(log_header_frame, text="RECENT DUNGEON RUNS LOG", bg="#11111d", fg="#aaaaaa", font=("Segoe UI", 10, "bold"))
        self.log_title_lbl.pack(side="left", anchor="w")

        tk.Button(log_header_frame, text="View Live Logs", bg="#1e1b4b", fg="#a78bfa", activebackground="#2e2a75", activeforeground="#ffffff",
                  font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=2, command=self.show_all_logs).pack(side="right", anchor="e", padx=(5, 0))

        tk.Button(log_header_frame, text="Reset Logs", bg="#b91c1c", fg="#ffffff", activebackground="#991b1b", activeforeground="#ffffff",
                  font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=2, command=self.confirm_reset).pack(side="right", anchor="e")

        self.canvas = tk.Canvas(right_frame, bg="#0a0a0f", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.canvas.yview)
        self.log_container = tk.Frame(self.canvas, bg="#0a0a0f")

        self.log_container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.log_container, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", lambda event: self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#0a0a0f", fieldbackground="#0a0a0f", foreground="#aaaaaa", borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#171725", foreground="#f0c040", font=("Segoe UI", 10, "bold"), borderwidth=0)

        self.refresh()

    def confirm_reset(self):
        ans = messagebox.askyesno("Confirm Reset", "Are you sure you want to delete all run data history?", parent=self)
        if ans:
            global data
            data = {"runs": [], "total": 0}
            save_data(data)
            self.current_view_mode = "ALL"
            self.refresh()

    def show_all_logs(self):
        self.current_view_mode = "ALL"
        self.counter_tree.selection_remove(self.counter_tree.selection())
        self.rebuild_runs_log_view()

    def on_boss_selected(self, event):
        selected_items = self.counter_tree.selection()
        if not selected_items: return
            
        item_values = self.counter_tree.item(selected_items[0], "values")
        if not item_values: return
            
        boss_name = item_values[0]
        self.current_view_mode = "Unknown Boss" if boss_name == "Unknown / Untracked" else boss_name
        self.rebuild_runs_log_view()

    def refresh(self):
        self.counter_tree.unbind("<<TreeviewSelect>>")
        for entry in self.counter_tree.get_children(): self.counter_tree.delete(entry)
            
        boss_counts = {boss: 0 for boss in BOSS_LOOT_POOLS.keys()}
        unknown_count = 0
        
        for run in data["runs"]:
            b_name = run.get("boss", "Unknown Boss")
            if "NEPS" in b_name.upper(): b_name = "Nepsilon"
            if b_name in boss_counts: boss_counts[b_name] += 1
            else: unknown_count += 1

        for b_name, b_count in sorted(boss_counts.items(), key=lambda x: x[1], reverse=True):
            self.counter_tree.insert("", "end", values=(b_name, b_count))
        if unknown_count > 0:
            self.counter_tree.insert("", "end", values=("Unknown / Untracked", unknown_count))

        self.counter_tree.bind("<<TreeviewSelect>>", self.on_boss_selected)
        self.rebuild_runs_log_view()

    def rebuild_runs_log_view(self):
        for widget in self.log_container.winfo_children(): 
            widget.destroy()

        # VIEW BLOCK 1: Chronological Session Log History Tracker
        if self.current_view_mode == "ALL":
            self.log_title_lbl.config(text="RECENT DUNGEON RUNS LOG")
            target_runs = data["runs"][-50:]
            
            for run in reversed(target_runs):
                row = tk.Frame(self.log_container, bg="#171725", pady=6, padx=8)
                row.pack(fill="x", pady=2, expand=True)

                duration = run.get("duration", "00:00") or "00:00"
                start_time = run.get("time", "--:--")
                    
                meta_text = f"#{run.get('run','?')} | {run.get('boss','Unknown Boss')} {start_time} ({duration}) | Drops: "
                tk.Label(row, text=meta_text, fg="#aaaaaa", bg="#171725", font=("Segoe UI", 9, "bold")).pack(side="left")

                if not run["loot"]:
                    tk.Label(row, text="No items recorded", fg="#666666", bg="#171725", font=("Segoe UI", 9, "italic")).pack(side="left")
                    continue

                for item_str in run["loot"]:
                    color = "#3b82f6"  
                    if "Gold" in item_str or "Legendary" in item_str: color = "#ffd700"
                    elif "Purple" in item_str or "Epic" in item_str: color = "#c084fc"
                    
                    clean_name = item_str.split(" (")[0]
                    tk.Label(row, text=f"[{clean_name}] ", fg=color, bg="#171725", font=("Segoe UI", 9, "bold")).pack(side="left", padx=2)

        # VIEW BLOCK 2: Categorized Static Loot Table Reference (Clean, uniform style)
        else:
            self.log_title_lbl.config(text=f"ALL POSSIBLE DROPS: {self.current_view_mode.upper()}")
            loot_pool = BOSS_LOOT_POOLS.get(self.current_view_mode, [])
            
            if not loot_pool:
                row = tk.Frame(self.log_container, bg="#171725", pady=10, padx=8)
                row.pack(fill="x", pady=2)
                tk.Label(row, text="No baseline item definition schema indexed for target model.", fg="#666666", bg="#171725", font=("Segoe UI", 10, "italic")).pack(side="left")
            else:
                # Filter item strings cleanly by names and tags
                weapons = sorted([item for item in loot_pool if item in VALID_WEAPONS])
                mounts = sorted([item for item in loot_pool if "(mount)" in item.lower()])
                gliders = sorted([item for item in loot_pool if "(glider)" in item.lower()])
                
                # Armors comprise anything remaining that doesn't trigger secondary system sets
                armors = sorted([
                    item for item in loot_pool 
                    if item not in VALID_WEAPONS 
                    and "(mount)" not in item.lower() 
                    and "(glider)" not in item.lower()
                ])

                def render_category_header(title_text):
                    hdr_frame = tk.Frame(self.log_container, bg="#0a0a0f", pady=8)
                    hdr_frame.pack(fill="x", pady=(8, 2))
                    
                    # Category Text Title
                    tk.Label(hdr_frame, text=title_text, fg="#f0c040", bg="#0a0a0f", font=("Segoe UI", 9, "bold")).pack(side="left", padx=4)
                    
                    # FIX: Using a raw tk.Frame with explicit pixel heights for a clean line artifact
                    accent_line = tk.Frame(hdr_frame, bg="#27273a", height=1, bd=0, highlightthickness=0)
                    accent_line.pack(side="left", fill="x", expand=True, padx=(8, 0), pady=2)
                    accent_line.pack_propagate(False) # Prevents the frame from scaling up

                def render_item_rows(item_list):
                    for item in item_list:
                        row = tk.Frame(self.log_container, bg="#171725", pady=5, padx=16)
                        row.pack(fill="x", pady=1, expand=True)
                        tk.Label(row, text="•", fg="#4b5563", bg="#171725", font=("Segoe UI", 10)).pack(side="left")
                        tk.Label(row, text=item, fg="#dddddd", bg="#171725", font=("Segoe UI", 10)).pack(side="left", padx=8)

                if weapons:
                    render_category_header("WEAPONS")
                    render_item_rows(weapons)

                if armors:
                    render_category_header("ARMOR & OTHER DROPS")
                    render_item_rows(armors)

                if mounts:
                    render_category_header("MOUNTS")
                    render_item_rows(mounts)

                if gliders:
                    render_category_header("GLIDERS")
                    render_item_rows(gliders)

        self.canvas.yview_moveto(0)

    def update_status(self, text, color):
        self.status_lbl.config(text=text, fg=color)

dash = Dashboard()

def save_run(boss_name, loot, duration, start_time_str):
    run_index = len(data["runs"]) + 1
    data["total"] = run_index
    data["runs"].append({
        "run": run_index,
        "boss": boss_name,  
        "time": start_time_str,
        "duration": duration,
        "loot": loot
    })
    save_data(data)
    dash.refresh()

# ─────────────────────────────────────────────────────────────
# RESOLUTION-AGNOSTIC SCAN MODULE
# ─────────────────────────────────────────────────────────────
def get_active_loot_pool(boss_name):
    for key, pool in BOSS_LOOT_POOLS.items():
        if key.upper() in boss_name.upper() or boss_name.upper() in key.upper(): return pool
    return BOSS_LOOT_POOLS["Crabgantua"]

def is_duplicate_item(new_item, detected_set):
    for existing in detected_set:
        if difflib.SequenceMatcher(None, existing.split(" (")[0].upper(), new_item.split(" (")[0].upper()).ratio() >= 0.85: return True
    return False

def extract_clean_tokens(raw_text):
    raw_text = raw_text.replace("|", "I").replace("1", "I")
    return [t for t in re.findall(r'[A-Z0-9\']+', raw_text.upper()) if len(t) > 1]

def scan_loot_window_until_loading(sct, left, top, width, height, active_boss):
    loot_monitor = {"top": top + int(height * 0.45), "left": left + int(width * 0.55), "width": int(width * 0.42), "height": int(height * 0.45)}
    loading_monitor = {"top": top + int(height * 0.85), "left": left, "width": int(width * 0.25), "height": int(height * 0.15)}
    
    detected_items = set()
    target_pool = get_active_loot_pool(active_boss)
    
    while True:
        try:
            load_img = np.array(sct.grab(loading_monitor))
            load_gray = cv2.cvtColor(load_img, cv2.COLOR_BGR2GRAY)
            _, load_thresh = cv2.threshold(load_gray, 150, 255, cv2.THRESH_BINARY)
            load_text = pytesseract.image_to_string(load_thresh, config="--psm 6").upper()
            if "LOAD" in load_text or "DING" in load_text: return list(detected_items)

            img = np.array(sct.grab(loot_monitor))
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            _, thresh_base = cv2.threshold(gray, 140, 255, cv2.THRESH_BINARY)
            text_base = pytesseract.image_to_string(thresh_base, config="--psm 6")

            mask_gold = cv2.inRange(hsv, np.array([15, 100, 100]), np.array([35, 255, 255]))
            text_gold = pytesseract.image_to_string(mask_gold, config="--psm 6")

            mask_purple = cv2.inRange(hsv, np.array([125, 40, 40]), np.array([155, 255, 255]))
            text_purple = pytesseract.image_to_string(mask_purple, config="--psm 6")

            mask_blue = cv2.inRange(hsv, np.array([85, 40, 40]), np.array([125, 255, 255]))
            text_blue = pytesseract.image_to_string(mask_blue, config="--psm 6")

            tokens_base = extract_clean_tokens(text_base)
            tokens_gold = extract_clean_tokens(text_gold)
            tokens_purple = extract_clean_tokens(text_purple)
            tokens_blue = extract_clean_tokens(text_blue)
            all_discovered_tokens = tokens_base + tokens_gold + tokens_purple + tokens_blue

            for item in target_pool:
                # Strip out formatting tags before running OCR fuzzy validation rules
                clean_target_name = item.replace(" (mount)", "").replace(" (glider)", "")
                item_tokens = [t for t in [re.sub(r'[^A-Z0-9\']', '', w.upper()) for w in clean_target_name.split()] if t]
                window_size = len(item_tokens)
                if window_size == 0: continue

                detected_rarity = None

                def evaluate_channel(channel_tokens):
                    if len(channel_tokens) < window_size: return False
                    for i in range(len(channel_tokens) - window_size + 1):
                        sub_window = channel_tokens[i:i+window_size]
                        if sum(1 for target, parsed in zip(item_tokens, sub_window) if target == parsed or difflib.SequenceMatcher(None, target, parsed).ratio() > 0.80) == window_size:
                            return True
                    return False

                if evaluate_channel(tokens_gold): detected_rarity = "Legendary/Gold"
                elif evaluate_channel(tokens_purple): detected_rarity = "Epic/Purple"
                elif evaluate_channel(tokens_blue): detected_rarity = "Rare/Blue"
                
                if not detected_rarity and len(all_discovered_tokens) >= window_size:
                    for i in range(len(all_discovered_tokens) - window_size + 1):
                        if sum(1 for target, parsed in zip(item_tokens, all_discovered_tokens[i:i+window_size]) if target == parsed or difflib.SequenceMatcher(None, target, parsed).ratio() > 0.75) == window_size:
                            detected_rarity = "FuzzyMatch"
                            break

                if detected_rarity:
                    if clean_target_name in VALID_WEAPONS and detected_rarity in ["Legendary/Gold", "Epic/Purple"]:
                        candidate = f"{clean_target_name} ({detected_rarity})"
                    else:
                        candidate = f"{clean_target_name} (Rare/Blue)"

                    if not is_duplicate_item(candidate, detected_items):
                        detected_items.add(candidate)

        except Exception as e:
            print("Loot Scan Thread Error:", e)
        time.sleep(0.15)

# ─────────────────────────────────────────────────────────────
# STATE WORKER SYSTEM (3-STAGE LIFECYCLE CONTROLLER)
# ─────────────────────────────────────────────────────────────
def ocr_worker():
    global tracker_armed, current_active_boss

    STATE_MONITORING = 0
    STATE_LOCKED_UNTIL_LOADING = 1
    STATE_LOCKED_UNTIL_GAMEPLAY = 2
    
    current_state = STATE_MONITORING
    fight_start_perf = None  
    fight_start_timestamp_str = "--:--"  

    with mss.MSS() as sct:
        while True:
            try:
                left, top, width, height = game.left, game.top, game.width, game.height

                loading_monitor = {"top": top + int(height * 0.85), "left": left, "width": int(width * 0.25), "height": int(height * 0.15)}
                load_img = np.array(sct.grab(loading_monitor))
                load_gray = cv2.cvtColor(load_img, cv2.COLOR_BGR2GRAY)
                _, load_thresh = cv2.threshold(load_gray, 150, 255, cv2.THRESH_BINARY)
                load_text = pytesseract.image_to_string(load_thresh, config="--psm 6").upper()
                is_loading_screen = "LOAD" in load_text or "DING" in load_text

                if current_state == STATE_LOCKED_UNTIL_LOADING:
                    dash.update_status("Waiting for instance reset...", "#888888")
                    if is_loading_screen: current_state = STATE_LOCKED_UNTIL_GAMEPLAY
                    time.sleep(0.2)
                    continue

                elif current_state == STATE_LOCKED_UNTIL_GAMEPLAY:
                    dash.update_status("Zoning into next instance...", "#f0c040")
                    if not is_loading_screen:
                        tracker_armed = True
                        current_state = STATE_MONITORING
                        fight_start_perf = None  
                        fight_start_timestamp_str = "--:--"
                        current_active_boss = None 
                        dash.update_status("Ready for next instance!", "#10b981")
                        time.sleep(1.5) 
                    time.sleep(0.2)
                    continue

                hp_monitor = {"top": top + int(height * 0.02), "left": left + int(width * 0.30), "width": int(width * 0.40), "height": int(height * 0.15)}
                hp_img = np.array(sct.grab(hp_monitor))
                hp_gray = cv2.cvtColor(hp_img, cv2.COLOR_BGR2GRAY)
                _, hp_thresh = cv2.threshold(hp_gray, 130, 255, cv2.THRESH_BINARY)
                hp_text = pytesseract.image_to_string(hp_thresh, config="--psm 6").upper()

                hp_boss_found = False
                for key in BOSS_LOOT_POOLS.keys():
                    if key.upper() in hp_text or (key == "Nepsilon" and "NEPS" in hp_text):
                        hp_boss_found = True
                        current_active_boss = key 
                        break

                monitor = {"top": top + int(height * 0.04), "left": left + int(width * 0.70), "width": int(width * 0.28), "height": int(height * 0.20)}
                img = np.array(sct.grab(monitor))
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)
                text = pytesseract.image_to_string(thresh, config="--psm 6")
                lines = [line.strip() for line in text.upper().split('\n') if line.strip()]
                
                is_dead = False
                found_boss_text = ""

                for line in lines:
                    if re.search(r'\b1\s*/\s*1\b', line): is_dead = True
                    payload = re.sub(r'\b[01]\s*/\s*1\b', '', line)
                    payload = re.sub(r'\bS[1I]A[1I]N\b|\bSLAIN\b', '', payload)
                    payload = payload.replace("SPECIAL FOES", "").replace("FOE", "").strip()
                    if payload and len(payload) > 3: found_boss_text = payload

                if not hp_boss_found and found_boss_text and not is_dead:
                    if "NEPS" in found_boss_text: current_active_boss = "Nepsilon"
                    else:
                        for key in BOSS_LOOT_POOLS.keys():
                            if key.upper() in found_boss_text:
                                current_active_boss = key
                                break
                    if current_active_boss and fight_start_perf is None:
                        dash.update_status(f"Waiting to detect: {current_active_boss}", "#a855f7")

                if hp_boss_found and not is_dead and tracker_armed:
                    dash.update_status(f"Active Encounter: {current_active_boss}", "#3b82f6")
                    if fight_start_perf is None:
                        fight_start_perf = time.perf_counter()
                        fight_start_timestamp_str = datetime.now().strftime("%H:%M")

                elif is_dead and tracker_armed and fight_start_perf is not None:
                    stop_perf = time.perf_counter()
                    elapsed_seconds = int(round(stop_perf - fight_start_perf))
                    if elapsed_seconds <= 0: elapsed_seconds = 1 
                    duration_str = f"{elapsed_seconds // 60:02d}:{elapsed_seconds % 60:02d}"

                    dash.update_status(f"Reading drops for {current_active_boss} until exit...", "#f0c040")
                    time.sleep(1.5) 
                    
                    auto_loot = scan_loot_window_until_loading(sct, left, top, width, height, current_active_boss)
                    save_run(current_active_boss, auto_loot, duration_str, fight_start_timestamp_str)
                    
                    tracker_armed, fight_start_perf, fight_start_timestamp_str, current_active_boss = False, None, "--:--", None
                    current_state = STATE_LOCKED_UNTIL_LOADING

            except Exception as e:
                print("Encounter Processing Error:", e)
            time.sleep(0.1)

# ─────────────────────────────────────────────────────────────
# EXECUTOR
# ─────────────────────────────────────────────────────────────
threading.Thread(target=ocr_worker, daemon=True).start()
root.mainloop()