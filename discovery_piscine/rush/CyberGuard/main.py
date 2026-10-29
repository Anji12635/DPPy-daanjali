"""
CyberGuard - Threat Intelligence & Incident Response
Tkinter dashboard (educational simulator, local data only).

  python3 main.py          -> terminal application (cli.py)
  python3 main.py --gui    -> graphical dashboard
"""

import sys
import os
import json
import csv
import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from datetime import datetime, timedelta

# Pillow is optional: without it the dashboard still works, just without
# the background pictures.
try:
    from PIL import Image, ImageEnhance, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "incidents.json"
SETTINGS_FILE = APP_DIR / "settings.json"
IMAGE_DIR = APP_DIR / "images"

# ------------------------------------------------------------
# COLOURS AND CONSTANTS
# ------------------------------------------------------------
BG = "#030b18"
SIDEBAR = "#061329"
PANEL = "#071a32"
CARD = "#0a203d"
CARD2 = "#102b50"
BLUE = "#168cff"
CYAN = "#21d4fd"
PURPLE = "#8067ff"
WHITE = "#edf5ff"
MUTED = "#91acd0"
BORDER = "#123e70"
RED = "#ff416c"
ORANGE = "#ff9f43"
GREEN = "#00d6a0"
YELLOW = "#ffd166"
DARK = "#04122a"

SEVERITIES = ["Low", "Medium", "High", "Critical"]
STATUSES = ["Open", "Investigating", "Contained", "Resolved"]
TYPES = ["Phishing", "Malware", "Brute Force", "Suspicious Login",
         "Data Breach", "Data Exfiltration", "Unauthorized Access", "Other"]

SEV_COLOR = {"Low": GREEN, "Medium": ORANGE, "High": RED, "Critical": PURPLE}
STATUS_BG = {"Open": "#0f4c8a", "Investigating": "#8b1f45",
             "Contained": "#0f5c4a", "Resolved": "#1d5a3a"}
TYPE_COLORS = [RED, ORANGE, BLUE, PURPLE, GREEN, CYAN]
LEVEL_COLOR = {"Low": GREEN, "Medium": ORANGE, "High": RED}

BASE_RISK = {"Low": 15, "Medium": 35, "High": 60, "Critical": 80}
TYPE_RISK = {"Phishing": 10, "Malware": 15, "Brute Force": 12,
             "Suspicious Login": 10, "Data Breach": 20,
             "Data Exfiltration": 18}

CATEGORY_TYPES = {
    "Network": ["Brute Force", "Data Exfiltration"],
    "Applications": ["Phishing", "Other"],
    "Endpoints": ["Malware"],
    "Data": ["Data Breach", "Data Exfiltration"],
    "Users": ["Suspicious Login", "Unauthorized Access"],
}

NOTES_BY_TYPE = {
    "Phishing": "Suspicious email or link reported",
    "Malware": "Suspicious file needs review",
    "Brute Force": "Repeated authentication failures",
    "Suspicious Login": "Unusual sign-in behaviour",
    "Data Exfiltration": "Unexpected outbound traffic",
    "Data Breach": "Possible data exposure",
}

THREATS = [
    ("PHISHING", RED,
     "Fake messages or websites designed to trick users into sharing "
     "sensitive information.",
     "Verify the sender, inspect links, and report suspicious messages."),
    ("MALWARE", ORANGE,
     "Software designed to damage systems, steal information, or gain "
     "unauthorized access.",
     "Document affected devices and follow approved isolation procedures."),
    ("BRUTE FORCE", PURPLE,
     "Repeated attempts to guess passwords or access accounts.",
     "Review authentication logs and apply approved account protections."),
    ("SUSPICIOUS LOGIN", BLUE,
     "A sign-in that differs from the expected device, location, or "
     "user behaviour.",
     "Verify the user and review related sign-in activity."),
    ("DATA EXFILTRATION", GREEN,
     "Potential unauthorized transfer of information outside an "
     "environment.",
     "Record observations and escalate through the incident process."),
    ("UNAUTHORIZED ACCESS", YELLOW,
     "Access to a resource without the required permission.",
     "Preserve relevant details and notify the responsible security team."),
]

REPORTS = [
    ("weekly", "Weekly Security Report"),
    ("summary", "Incident Summary (Last 7 Days)"),
    ("intel", "Threat Intelligence Report"),
]

# Which background picture (1.jpg ... 4.jpg) each page banner uses.
PAGE_IMAGES = {"Dashboard": 1, "Threat Intelligence": 2, "Reports": 3,
               "Analytics": 4, "Settings": 1}

# id, title, type, severity, status, ip, day, time
SEED = [
    (1024, "Suspicious login detected", "Suspicious Login", "High", "Investigating", "192.168.1.45", "Oct 28", "21:32"),
    (1023, "Malware attachment flagged", "Malware", "High", "Open", "203.0.113.24", "Oct 28", "18:17"),
    (1022, "Repeated failed login attempts", "Brute Force", "Medium", "Contained", "185.199.110.23", "Oct 28", "16:03"),
    (1021, "Urgent account verification email", "Phishing", "Medium", "Open", "10.0.0.12", "Oct 28", "14:27"),
    (1020, "Unusual data transfer", "Data Exfiltration", "Low", "Resolved", "172.16.5.8", "Oct 28", "11:05"),
    (1019, "Credential harvesting page", "Phishing", "Medium", "Contained", "198.51.100.7", "Oct 28", "09:42"),
    (1018, "Unknown endpoint file", "Malware", "Low", "Resolved", "192.168.10.20", "Oct 28", "07:15"),
    (1017, "Fake invoice email", "Phishing", "Medium", "Investigating", "45.33.32.156", "Oct 27", "22:10"),
    (1016, "SSH password guessing", "Brute Force", "High", "Contained", "91.134.12.8", "Oct 27", "19:40"),
    (1015, "Trojan dropper blocked", "Malware", "Medium", "Resolved", "104.21.55.2", "Oct 27", "15:21"),
    (1014, "Spam link reported", "Phishing", "Low", "Resolved", "10.0.0.31", "Oct 27", "11:02"),
    (1013, "Login from new country", "Suspicious Login", "Medium", "Investigating", "77.88.55.60", "Oct 26", "20:45"),
    (1012, "Prize scam message", "Phishing", "Low", "Resolved", "172.16.2.14", "Oct 26", "16:30"),
    (1011, "Ransomware note found", "Malware", "High", "Contained", "185.220.101.4", "Oct 26", "12:12"),
    (1010, "Admin panel brute force", "Brute Force", "Medium", "Resolved", "62.210.11.9", "Oct 25", "23:50"),
    (1009, "Fake delivery text", "Phishing", "Low", "Resolved", "10.0.0.77", "Oct 25", "17:18"),
    (1008, "Spoofed bank login page", "Phishing", "Medium", "Contained", "198.51.100.55", "Oct 25", "10:05"),
    (1007, "Suspicious macro document", "Malware", "Medium", "Resolved", "203.0.113.99", "Oct 24", "21:00"),
    (1006, "Impossible travel login", "Suspicious Login", "High", "Resolved", "118.69.12.34", "Oct 24", "14:26"),
    (1005, "Password reset lure", "Phishing", "Low", "Resolved", "192.168.5.5", "Oct 23", "18:40"),
    (1004, "VPN login failures", "Brute Force", "Medium", "Resolved", "122.155.1.20", "Oct 23", "09:15"),
    (1003, "Exposed customer file", "Data Breach", "Medium", "Resolved", "10.10.1.3", "Oct 22", "20:33"),
    (1002, "Botnet beacon detected", "Malware", "High", "Resolved", "80.82.77.139", "Oct 22", "13:08"),
    (1001, "CEO impersonation email", "Phishing", "Low", "Resolved", "172.16.9.9", "Oct 22", "08:50"),
]

COUNTRIES = ["United States", "China", "Russia", "Germany",
             "Vietnam", "Brazil", "India"]


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------

def build_seed():
    return [
        {"id": iid, "title": title, "type": kind, "severity": sev,
         "status": status, "source": ip, "created": f"{day}, {clock}",
         "notes": NOTES_BY_TYPE.get(kind, "")}
        for iid, title, kind, sev, status, ip, day, clock in SEED
    ]


def risk_score(incident):
    score = BASE_RISK.get(incident.get("severity"), 15)
    score += TYPE_RISK.get(incident.get("type"), 5)
    if incident.get("notes"):
        score += 5
    return min(100, score)


def valid_ip(text):
    parts = text.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit() or int(part) > 255:
            return False
    return True


def parse_created(text):
    try:
        moment = datetime.strptime(str(text), "%b %d, %H:%M")
    except ValueError:
        return None
    now = datetime.now()
    moment = moment.replace(year=now.year)
    if moment > now + timedelta(days=1):
        moment = moment.replace(year=now.year - 1)
    return moment


def time_ago(moment):
    if moment is None:
        return ""
    seconds = max(0, int((datetime.now() - moment).total_seconds()))
    if seconds < 3600:
        return f"{max(1, seconds // 60)} min ago"
    if seconds < 86400:
        return f"{seconds // 3600} hr ago"
    return f"{seconds // 86400} d ago"


def country_of(ip):
    """Simulated geolocation for the educational map."""
    try:
        first = int(str(ip).split(".")[0])
    except ValueError:
        return "Unknown"
    if first in (10, 127, 172, 192):
        return "Local Network"
    return COUNTRIES[first % len(COUNTRIES)]


def level_of(score):
    if score < 40:
        return "Low"
    if score < 70:
        return "Medium"
    return "High"


def incident_code(incident_id):
    return f"CG-{incident_id}"


# ------------------------------------------------------------
# BACKGROUND IMAGES (images/1.jpg ... images/4.jpg)
# ------------------------------------------------------------

class BackgroundManager:
    """Loads, darkens and crops background pictures to any size."""

    def __init__(self, brightness=0.42):
        self.brightness = brightness
        self.sources = {}
        self.cache = {}

    def load(self, number):
        if number in self.sources:
            return self.sources[number]
        image = None
        path = IMAGE_DIR / f"{number}.jpg"
        if HAS_PIL and path.is_file():
            try:
                image = Image.open(path).convert("RGB")
                image = ImageEnhance.Brightness(image).enhance(self.brightness)
            except Exception as error:
                print(f"Could not load background {path.name}: {error}")
                image = None
        elif HAS_PIL:
            print(f"Background image not found: {path}")
        self.sources[number] = image
        return image

    def cover(self, number, width, height):
        """Return a PhotoImage that covers width x height (or None)."""
        source = self.load(number)
        if source is None or width < 2 or height < 2:
            return None
        key = (number, width, height)
        if key in self.cache:
            return self.cache[key]

        # Cover the area without stretching the picture.
        source_ratio = source.width / source.height
        target_ratio = width / height
        if source_ratio > target_ratio:
            new_h = height
            new_w = int(height * source_ratio)
        else:
            new_w = width
            new_h = int(width / source_ratio)

        resampling = getattr(Image, "Resampling", Image)
        resized = source.resize((max(new_w, width), max(new_h, height)),
                                resampling.LANCZOS)
        left = (resized.width - width) // 2
        top = (resized.height - height) // 2
        resized = resized.crop((left, top, left + width, top + height))

        photo = ImageTk.PhotoImage(resized)
        if len(self.cache) > 24:
            self.cache.clear()
        self.cache[key] = photo
        return photo


# ------------------------------------------------------------
# SCROLLABLE PAGE CONTAINER (stretches to fill the window)
# ------------------------------------------------------------

class ScrollFrame(tk.Frame):
    def __init__(self, parent, bg=BG):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.bar = ttk.Scrollbar(self, orient="vertical",
                                 command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.bar.set)
        self.bar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.body = tk.Frame(self.canvas, bg=bg)
        self.window = self.canvas.create_window(
            (0, 0), window=self.body, anchor="nw")
        self.body.bind("<Configure>", self._on_body)
        self.canvas.bind("<Configure>", lambda e: self._stretch())

    def _on_body(self, _event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._stretch()

    def _stretch(self):
        """Make the page at least as tall as the window (no empty strip),
        but still scrollable when the content is taller."""
        self.canvas.itemconfigure(
            self.window,
            width=self.canvas.winfo_width(),
            height=max(self.canvas.winfo_height(),
                       self.body.winfo_reqheight()))


# ------------------------------------------------------------
# MAIN APPLICATION
# ------------------------------------------------------------

class CyberGuardApp:
    def __init__(self, root):
        self.root = root
        root.title("CyberGuard | Threat Intelligence & Incident Response")
        # Never open a window bigger than the screen.
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        width, height = min(1500, sw - 40), min(900, sh - 90)
        root.geometry(f"{width}x{height}+20+10")
        root.minsize(min(1100, width), min(650, height))
        root.configure(bg=BG)

        self.bgm = BackgroundManager()
        self.incidents = []
        self.search_query = ""
        self.current_page = "Dashboard"
        self.analyst = "Anji"
        self.scroll = None
        self.tree = None
        self.threat_entry = None

        self.load_settings()
        self.load_data()
        self.setup_styles()
        self.build_shell()
        self.show_page("Dashboard")

        root.bind_all("<MouseWheel>", self.on_wheel)
        root.bind_all("<Button-4>", self.on_wheel)
        root.bind_all("<Button-5>", self.on_wheel)
        self.tick_clock()

    # --------------------------------------------------------
    # DATA
    # --------------------------------------------------------

    def load_settings(self):
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            self.analyst = str(data.get("analyst", "Anji")) or "Anji"
        except (OSError, ValueError, AttributeError):
            self.analyst = "Anji"

    def save_settings(self):
        try:
            SETTINGS_FILE.write_text(
                json.dumps({"analyst": self.analyst}, indent=2),
                encoding="utf-8")
        except OSError:
            pass

    def load_data(self):
        records = None
        try:
            if DATA_FILE.exists():
                records = json.loads(DATA_FILE.read_text(encoding="utf-8"))
                if not isinstance(records, list):
                    raise ValueError("bad format")
        except (OSError, ValueError):
            records = None

        if records is None:
            records = build_seed()

        clean = []
        for item in records:
            if not isinstance(item, dict):
                continue
            try:
                item["id"] = int(item.get("id"))
            except (TypeError, ValueError):
                continue
            item.setdefault("title", "Untitled")
            item.setdefault("type", "Other")
            if item.get("severity") not in SEVERITIES:
                item["severity"] = "Low"
            if item.get("status") not in STATUSES:
                item["status"] = "Open"
            item.setdefault("source", "Not specified")
            item.setdefault("created", datetime.now().strftime("%b %d, %H:%M"))
            item.setdefault("notes", "")
            clean.append(item)

        self.incidents = clean
        self.save_data()

    def save_data(self):
        try:
            DATA_FILE.write_text(json.dumps(self.incidents, indent=2),
                                 encoding="utf-8")
        except OSError as error:
            messagebox.showerror("Save error", str(error))

    def find(self, incident_id):
        for item in self.incidents:
            if item["id"] == incident_id:
                return item
        return None

    def next_id(self):
        return max([i["id"] for i in self.incidents] + [1000]) + 1

    def severity_counts(self):
        return {level: sum(1 for i in self.incidents
                           if i["severity"] == level)
                for level in ("Critical", "High", "Medium", "Low")}

    def type_counts(self):
        tally = {}
        for item in self.incidents:
            tally[item["type"]] = tally.get(item["type"], 0) + 1
        return sorted(tally.items(), key=lambda kv: (-kv[1], kv[0]))

    def active_incidents(self):
        return [i for i in self.incidents
                if i["status"] in ("Open", "Investigating")]

    def alert_incidents(self):
        return [i for i in self.active_incidents()
                if i["severity"] in ("High", "Critical")]

    def top_sources(self):
        tally = {}
        for item in self.incidents:
            name = country_of(item["source"])
            tally[name] = tally.get(name, 0) + 1
        ranked = sorted(tally.items(), key=lambda kv: -kv[1])
        top = ranked[:5]
        other = sum(v for _, v in ranked[5:])
        if other:
            top.append(("Others", other))
        return top

    def daily_series(self):
        counts = {}
        for item in self.incidents:
            moment = parse_created(item.get("created"))
            if moment:
                counts[moment.date()] = counts.get(moment.date(), 0) + 1
        days = sorted(counts)[-7:]
        return [d.strftime("%b %d") for d in days], [counts[d] for d in days]

    def category_levels(self):
        result = {}
        for name, kinds in CATEGORY_TYPES.items():
            scores = [risk_score(i) for i in self.active_incidents()
                      if i["type"] in kinds]
            result[name] = level_of(sum(scores) / len(scores)) if scores else "Low"
        return result

    def overall_risk(self):
        scores = [risk_score(i) for i in self.active_incidents()]
        if not scores:
            return "Low", 10
        average = sum(scores) / len(scores)
        return level_of(average), int(average)

    def filtered_incidents(self):
        records = list(self.incidents)
        sev = self.sev_filter.get() if hasattr(self, "sev_filter") else "All"
        status = self.status_filter.get() if hasattr(self, "status_filter") else "All"
        if sev != "All":
            records = [i for i in records if i["severity"] == sev]
        if status != "All":
            records = [i for i in records if i["status"] == status]
        if self.search_query:
            query = self.search_query.lower()
            records = [
                i for i in records
                if query in " ".join(
                    [incident_code(i["id"])] +
                    [str(i.get(k, "")) for k in
                     ("title", "type", "severity", "status",
                      "source", "notes")]).lower()
            ]
        return sorted(records, key=lambda i: i["id"], reverse=True)

    # --------------------------------------------------------
    # BUSINESS RULES
    # --------------------------------------------------------

    def status_error(self, incident, new_status):
        old = incident["status"]
        if STATUSES.index(new_status) <= STATUSES.index(old):
            return "Status can only move forward (resolved cases stay closed)."
        if (incident["severity"] in ("High", "Critical")
                and old == "Open" and new_status != "Investigating"):
            return "High/Critical incidents must be Investigating first."
        return None

    # --------------------------------------------------------
    # STYLES AND WIDGET HELPERS
    # --------------------------------------------------------

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=PANEL, foreground=WHITE,
                        fieldbackground=PANEL, rowheight=32,
                        borderwidth=0, font=("Arial", 9))
        style.configure("Treeview.Heading", background=CARD2,
                        foreground=CYAN, padding=8, relief="flat",
                        font=("Arial", 9, "bold"))
        style.map("Treeview",
                  background=[("selected", "#164b83")],
                  foreground=[("selected", WHITE)])
        style.configure("TCombobox", fieldbackground=CARD,
                        background=CARD2, foreground=WHITE,
                        arrowcolor=CYAN, selectbackground=CARD,
                        selectforeground=WHITE)
        style.map("TCombobox", fieldbackground=[("readonly", CARD)],
                  foreground=[("readonly", WHITE)])
        style.configure("Vertical.TScrollbar", background=CARD2,
                        troughcolor=BG, arrowcolor=CYAN, bordercolor=BG)
        self.root.option_add("*TCombobox*Listbox.background", CARD)
        self.root.option_add("*TCombobox*Listbox.foreground", WHITE)
        self.root.option_add("*TCombobox*Listbox.selectBackground", BLUE)

    def label(self, parent, text, size=10, color=WHITE, bold=False,
              bg=PANEL, **kwargs):
        return tk.Label(parent, text=text, bg=bg, fg=color,
                        font=("Arial", size, "bold" if bold else "normal"),
                        **kwargs)

    def button(self, parent, text, command, bg=CARD2, fg=WHITE, **kwargs):
        padx = kwargs.pop("padx", 10)
        pady = kwargs.pop("pady", 7)
        return tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                         activebackground=BLUE, activeforeground=WHITE,
                         relief="flat", bd=0, cursor="hand2",
                         font=("Arial", 9, "bold"), padx=padx, pady=pady,
                         **kwargs)

    def panel(self, parent, bg=PANEL):
        return tk.Frame(parent, bg=bg, highlightbackground=BORDER,
                        highlightthickness=1)

    def pill(self, parent, text, fill, fg=WHITE, bg=PANEL):
        holder = tk.Frame(parent, bg=bg)
        tk.Label(holder, text=text, bg=fill, fg=fg,
                 font=("Arial", 8, "bold"), padx=7, pady=1).pack(anchor="w")
        return holder

    def sev_pill(self, parent, severity, bg=PANEL):
        fg = WHITE if severity in ("High", "Critical") else DARK
        return self.pill(parent, severity, SEV_COLOR.get(severity, MUTED), fg, bg)

    def status_pill(self, parent, status, bg=PANEL):
        return self.pill(parent, status, STATUS_BG.get(status, CARD2), WHITE, bg)

    def make_dialog(self, title, width, height):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry(f"{width}x{height}")
        dialog.configure(bg=BG)
        dialog.transient(self.root)
        try:
            dialog.wait_visibility()
            dialog.grab_set()
        except tk.TclError:
            pass
        return dialog

    # --------------------------------------------------------
    # SHELL: SIDEBAR + TOPBAR
    # --------------------------------------------------------

    def build_shell(self):
        self.sidebar = tk.Frame(self.root, bg=SIDEBAR, width=260)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.workspace = tk.Frame(self.root, bg=BG)
        self.workspace.pack(side="left", fill="both", expand=True)

        self.build_brand()
        self.build_navigation()
        self.build_topbar()

        self.label(self.workspace,
                   "● SYSTEM ONLINE     |     EDUCATIONAL SIMULATOR     |     LOCAL DATA ONLY",
                   8, GREEN, True, bg=BG, anchor="w"
                   ).pack(side="bottom", fill="x", padx=20, pady=(0, 6))

        self.page_host = tk.Frame(self.workspace, bg=BG)
        self.page_host.pack(fill="both", expand=True)

    def build_brand(self):
        brand = tk.Frame(self.sidebar, bg=SIDEBAR)
        brand.pack(fill="x", padx=10, pady=(20, 14))

        logo = tk.Canvas(brand, width=44, height=52, bg=SIDEBAR,
                         highlightthickness=0)
        logo.pack(side="left", padx=(0, 6))
        logo.create_polygon(22, 2, 41, 10, 37, 31, 22, 48, 7, 31, 3, 10,
                            outline=PURPLE, fill=SIDEBAR, width=3)
        logo.create_line(11, 25, 19, 32, 33, 15, fill=CYAN, width=3)

        words = tk.Frame(brand, bg=SIDEBAR)
        words.pack(side="left", fill="x", expand=True)
        self.label(words, "CyberGuard", 15, WHITE, True, bg=SIDEBAR).pack(anchor="w")
        self.label(words, "THREAT INTELLIGENCE", 7, CYAN, True, bg=SIDEBAR).pack(anchor="w")
        self.label(words, "& INCIDENT RESPONSE", 7, MUTED, bg=SIDEBAR).pack(anchor="w")

        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(
            fill="x", padx=14, pady=(0, 10))

    def build_navigation(self):
        self.nav_buttons = {}
        pages = [("Dashboard", "⌂"), ("Incidents", "⚠"),
                 ("Threat Intelligence", "◉"), ("Reports", "▤"),
                 ("Analytics", "▥"), ("Settings", "⚙")]

        for page, symbol in pages:
            btn = tk.Button(
                self.sidebar, text=f"  {symbol}  {page}", anchor="w",
                bg=SIDEBAR, fg=MUTED, activebackground="#102b63",
                activeforeground=CYAN, relief="flat", bd=0,
                font=("Arial", 10), padx=12, pady=12, cursor="hand2",
                command=lambda p=page: self.show_page(p))
            btn.pack(fill="x", padx=9, pady=2)
            self.nav_buttons[page] = btn

        art = tk.Canvas(self.sidebar, bg=SIDEBAR, highlightthickness=0)
        art.pack(fill="both", expand=True, pady=6)
        art.bind("<Configure>",
                 lambda e: self.draw_hacker(art, e.width, e.height))

        for text, color in [("┃ DETECT", CYAN), ("┃ ANALYZE", ORANGE),
                            ("┃ RESPOND", ORANGE), ("┃ PROTECT", GREEN)]:
            self.label(self.sidebar, text, 10, color, True,
                       bg=SIDEBAR).pack(anchor="w", padx=23, pady=4)

        self.label(self.sidebar, "CyberGuard v1.0", 8, MUTED,
                   bg=SIDEBAR).pack(anchor="w", padx=19, pady=16)

    def build_topbar(self):
        bar = tk.Frame(self.workspace, bg=SIDEBAR, height=66)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        search_frame = tk.Frame(bar, bg=CARD, highlightbackground=BORDER,
                                highlightthickness=1)
        search_frame.pack(side="left", padx=18, pady=11)

        self.search_entry = tk.Entry(
            search_frame, width=42, bg=CARD, fg=WHITE,
            insertbackground=WHITE, relief="flat", font=("Arial", 10))
        self.search_entry.insert(0, "Search incidents, IPs, or keywords...")
        self.search_entry.pack(side="left", padx=10, pady=9)
        self.search_entry.bind("<FocusIn>", self.clear_search_hint)
        self.search_entry.bind("<Return>", lambda e: self.search_incidents())

        self.button(search_frame, "⌕", self.search_incidents, bg=CARD,
                    fg=CYAN, padx=8, pady=4).pack(side="left")

        # right side (first packed = rightmost)
        person = tk.Frame(bar, bg=SIDEBAR)
        person.pack(side="right", padx=(8, 18))
        self.user_label = self.label(person, self.analyst, 10, WHITE, True, bg=SIDEBAR)
        self.user_label.pack(anchor="w")
        self.label(person, "Security Analyst", 8, MUTED, bg=SIDEBAR).pack(anchor="w")

        avatar = tk.Canvas(bar, width=42, height=42, bg=SIDEBAR,
                           highlightthickness=0)
        avatar.pack(side="right", padx=4)
        avatar.create_oval(2, 2, 40, 40, fill=PURPLE, outline=BLUE, width=2)
        avatar.create_oval(15, 9, 27, 21, fill="#d9d4ff", outline="")
        avatar.create_arc(8, 22, 34, 46, start=0, extent=180,
                          fill="#d9d4ff", outline="")

        tk.Frame(bar, bg=BORDER, width=1).pack(side="right", fill="y", pady=12, padx=8)

        self.clock_var = tk.StringVar()
        clock = tk.Label(bar, textvariable=self.clock_var, bg=SIDEBAR,
                         fg=WHITE, font=("Arial", 9), justify="center")
        clock.pack(side="right", padx=8)

        self.bell = tk.Canvas(bar, width=44, height=44, bg=SIDEBAR,
                              highlightthickness=0, cursor="hand2")
        self.bell.pack(side="right", padx=8)
        self.bell.create_arc(12, 9, 32, 31, start=0, extent=180,
                             style="arc", outline=WHITE, width=2)
        self.bell.create_line(12, 20, 12, 29, fill=WHITE, width=2)
        self.bell.create_line(32, 20, 32, 29, fill=WHITE, width=2)
        self.bell.create_line(9, 30, 35, 30, fill=WHITE, width=2)
        self.bell.create_oval(19, 32, 25, 37, fill=WHITE, outline="")
        self.bell_badge = self.bell.create_oval(26, 2, 40, 16, fill=RED, outline="")
        self.bell_text = self.bell.create_text(33, 9, text="0", fill=WHITE,
                                               font=("Arial", 8, "bold"))
        self.bell.bind("<Button-1>", lambda e: self.show_alert_popup())
        self.tick_clock_now()

    def tick_clock_now(self):
        self.clock_var.set(datetime.now().strftime("%H:%M\n%b %d, %Y"))

    def tick_clock(self):
        self.tick_clock_now()
        self.root.after(20000, self.tick_clock)

    def refresh_bell(self):
        count = len(self.alert_incidents())
        self.bell.itemconfigure(self.bell_text, text=str(count))
        state = "normal" if count else "hidden"
        self.bell.itemconfigure(self.bell_badge, state=state)
        self.bell.itemconfigure(self.bell_text, state=state)

    def show_alert_popup(self):
        alerts = self.alert_incidents()
        if not alerts:
            messagebox.showinfo("Alerts", "No active high-severity alerts.")
            return
        lines = [f"{incident_code(i['id'])}  {i['severity']}  {i['title']}"
                 for i in alerts]
        messagebox.showwarning("Active high-severity alerts", "\n".join(lines))

    def clear_search_hint(self, _event=None):
        if self.search_entry.get().startswith("Search incidents"):
            self.search_entry.delete(0, "end")

    def search_incidents(self):
        query = self.search_entry.get().strip()
        if query.startswith("Search incidents"):
            query = ""
        self.search_query = query
        self.show_page("Incidents")

    def on_wheel(self, event):
        sf = self.scroll
        if sf is None or not sf.winfo_exists():
            return
        try:
            if event.widget.winfo_toplevel() is not self.root:
                return
        except (AttributeError, KeyError, tk.TclError):
            return
        if getattr(event, "num", 0) == 4:
            step = -1
        elif getattr(event, "num", 0) == 5:
            step = 1
        else:
            step = -1 if event.delta > 0 else 1
        sf.canvas.yview_scroll(step * 2, "units")

    # --------------------------------------------------------
    # PAGE ROUTER
    # --------------------------------------------------------

    def show_page(self, page):
        self.current_page = page
        for widget in self.page_host.winfo_children():
            widget.destroy()
        self.tree = None
        self.threat_entry = None

        for name, btn in self.nav_buttons.items():
            btn.configure(bg="#102b63" if name == page else SIDEBAR,
                          fg=CYAN if name == page else MUTED)

        self.scroll = ScrollFrame(self.page_host)
        self.scroll.pack(fill="both", expand=True, padx=18, pady=(12, 4))
        self.body = self.scroll.body
        self.refresh_bell()

        {
            "Dashboard": self.dashboard_page,
            "Incidents": self.incidents_page,
            "Threat Intelligence": self.threat_page,
            "Reports": self.reports_page,
            "Analytics": self.analytics_page,
            "Settings": self.settings_page,
        }[page]()

    def page_heading(self, title, subtitle):
        """Slim banner with a background picture at the top of a page."""
        image_no = PAGE_IMAGES.get(self.current_page, 1)
        canvas = tk.Canvas(self.body, height=74, bg=PANEL,
                           highlightthickness=1, highlightbackground=BORDER)
        canvas.pack(fill="x", pady=(2, 12))
        canvas.bind("<Configure>",
                    lambda e: self.draw_banner(canvas, e.width, e.height,
                                               title, subtitle, image_no, False))

    # --------------------------------------------------------
    # DRAWING HELPERS
    # --------------------------------------------------------

    def draw_hacker(self, canvas, w, h):
        canvas.delete("all")
        rng = random.Random(5)
        for _ in range(55):
            canvas.create_text(rng.randint(0, max(w, 1)), rng.randint(0, max(h, 1)),
                               text=rng.choice(["01", "{ }", "</>", "#", "10", "::"]),
                               fill="#0b3b6e", font=("Courier", 8))
        hood = [(.50, .18), (.64, .24), (.70, .40), (.84, .55), (.96, .80),
                (.96, 1.0), (.04, 1.0), (.04, .80), (.16, .55), (.30, .40),
                (.36, .24)]
        pts = []
        for x, y in hood:
            pts.extend([x * w, y * h])
        canvas.create_polygon(*pts, fill="#050f1f", outline="#1a4f8f", width=2)
        canvas.create_oval(w * .38, h * .30, w * .62, h * .58,
                           fill="#020812", outline="#0d3a6b")
        canvas.create_oval(w * .43, h * .40, w * .47, h * .43, fill=CYAN, outline="")
        canvas.create_oval(w * .53, h * .40, w * .57, h * .43, fill=CYAN, outline="")

    def draw_banner(self, canvas, w, h, title, subtitle, image_no=1, fancy=False):
        """Banner with a background picture (if available), title and subtitle.
        fancy=True adds the network-node decoration and the tagline."""
        canvas.delete("all")
        w, h = max(w, 200), max(h, 40)

        photo = self.bgm.cover(image_no, w, h)
        if photo is not None:
            canvas.photo = photo          # keep a reference
            canvas.create_image(0, 0, anchor="nw", image=photo)
        else:
            canvas.create_rectangle(0, 0, w, h, fill="#04132b", outline="")

        if fancy:
            rng = random.Random(12)
            nodes = [(rng.randint(int(w * .38), w), rng.randint(0, h))
                     for _ in range(40)]
            for x, y in nodes:
                for x2, y2 in nodes:
                    if x < x2 and abs(x - x2) < w * 0.15 and abs(y - y2) < h * 0.6:
                        canvas.create_line(x, y, x2, y2, fill="#104577")
            for index, (x, y) in enumerate(nodes):
                color = RED if index % 7 == 0 else CYAN
                r = 3 if index % 7 == 0 else 2
                canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")
            cx, cy = w * 0.62, h * 0.55
            rx, ry = w * 0.17, h * 0.45
            canvas.create_oval(cx - rx, cy - ry, cx + rx, cy + ry, outline="#1265a2", width=2)
            canvas.create_oval(cx - rx * .55, cy - ry, cx + rx * .55, cy + ry, outline="#0d4779")
            canvas.create_oval(cx - rx, cy - ry * .5, cx + rx, cy + ry * .5, outline="#0d4779")
            if w > 760:
                canvas.create_text(w - 160, h / 2 - 10, text="Smarter Analysis.",
                                   fill=CYAN, font=("Arial", 11, "bold"), anchor="w")
                canvas.create_text(w - 160, h / 2 + 10, text="Safer Tomorrow.",
                                   fill=CYAN, font=("Arial", 11, "bold"), anchor="w")

        canvas.create_text(18, h * 0.36, text=title, fill=WHITE,
                           font=("Arial", 20 if fancy else 18, "bold"), anchor="w")
        canvas.create_text(18, h * 0.74, text=subtitle, fill="#c7d9f5",
                           font=("Arial", 9), anchor="w")

    def draw_threat_map(self, canvas, w, h):
        canvas.delete("all")
        canvas.create_rectangle(0, 0, w, h, fill="#04142b", outline="")
        continents = [
            [(.04, .25), (.14, .14), (.24, .20), (.26, .32), (.20, .43), (.16, .60), (.10, .50), (.08, .36)],
            [(.30, .23), (.40, .16), (.46, .25), (.44, .38), (.38, .40), (.36, .54), (.30, .43)],
            [(.40, .45), (.50, .40), (.55, .52), (.51, .76), (.46, .84), (.42, .63)],
            [(.52, .23), (.64, .15), (.76, .25), (.82, .39), (.74, .46), (.66, .38), (.58, .43), (.52, .34)],
            [(.70, .58), (.80, .55), (.84, .67), (.76, .73)],
        ]
        for shape in continents:
            coords = []
            for x, y in shape:
                coords.extend([x * w, y * h])
            canvas.create_polygon(*coords, fill="#073967", outline=BLUE)

        points = [(.14, .34), (.18, .42), (.38, .31), (.45, .60), (.58, .35),
                  (.66, .30), (.74, .38), (.50, .48), (.28, .28), (.76, .62), (.46, .25)]
        for a, b in [(0, 3), (0, 8), (1, 4), (2, 5), (3, 6), (4, 7), (5, 9), (7, 10)]:
            canvas.create_line(points[a][0] * w, points[a][1] * h,
                               points[b][0] * w, points[b][1] * h,
                               fill="#a13c91", smooth=True)
        for x, y in points:
            canvas.create_oval(x * w - 7, y * h - 7, x * w + 7, y * h + 7,
                               outline=RED, width=2)
            canvas.create_oval(x * w - 2, y * h - 2, x * w + 2, y * h + 2,
                               fill="#ff6685", outline="")

    def draw_ring(self, canvas, cx, cy, radius, thickness, segments):
        total = sum(v for v, _ in segments)
        if total <= 0:
            canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                               outline=BORDER, width=thickness)
            return
        start = 90
        for value, color in segments:
            if value <= 0:
                continue
            extent = 360 * value / total
            canvas.create_arc(cx - radius, cy - radius, cx + radius, cy + radius,
                              start=start, extent=-min(extent, 359.9),
                              style="arc", outline=color, width=thickness)
            start -= extent

    def draw_line_chart(self, canvas, labels, values, w, h):
        canvas.delete("all")
        w, h = max(w, 300), max(h, 120)
        left, right, top, bottom = 42, w - 22, 16, h - 30
        peak = max(max(values, default=0), 1)
        step = max(1, -(-peak // 4))
        for tick in range(5):
            y = bottom - (bottom - top) * tick / 4
            canvas.create_line(left, y, right, y, fill="#102b4a")
            canvas.create_text(left - 10, y, text=str(tick * step),
                               fill=MUTED, font=("Arial", 8), anchor="e")
        if not values:
            canvas.create_text(w / 2, h / 2, text="No data yet",
                               fill=MUTED, font=("Arial", 10))
            return
        count = len(values)
        points = []
        for i, value in enumerate(values):
            x = left + (right - left) * (i / (count - 1) if count > 1 else 0.5)
            y = bottom - (bottom - top) * value / (step * 4)
            points.append((x, y))
            canvas.create_text(x, bottom + 14, text=labels[i], fill=MUTED,
                               font=("Arial", 8))
        area = [points[0][0], bottom]
        for x, y in points:
            area.extend([x, y])
        area.extend([points[-1][0], bottom])
        if count > 1:
            canvas.create_polygon(*area, fill="#16195a", outline="")
            flat = [c for p in points for c in p]
            canvas.create_line(*flat, fill=PURPLE, width=2)
        for (x, y), value in zip(points, values):
            canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill=CYAN, outline=WHITE)
            canvas.create_text(x, y - 12, text=str(value), fill=WHITE,
                               font=("Arial", 8, "bold"))

    def draw_bars(self, canvas, items, w, h, horizontal=False):
        canvas.delete("all")
        w, h = max(w, 300), max(h, 180)
        if not items:
            canvas.create_text(w / 2, h / 2, text="No data yet", fill=MUTED)
            return
        peak = max(max(v for _, v, _ in items), 1)
        if horizontal:
            slot = (h - 20) / len(items)
            for i, (name, value, color) in enumerate(items):
                y = 10 + slot * i
                canvas.create_text(8, y + slot * 0.4, text=name, fill=MUTED,
                                   font=("Arial", 9), anchor="w")
                length = (w - 230) * value / peak
                canvas.create_rectangle(150, y + slot * 0.15, 150 + length,
                                        y + slot * 0.65, fill=color, outline="")
                canvas.create_text(158 + length, y + slot * 0.4, text=str(value),
                                   fill=WHITE, font=("Arial", 9, "bold"), anchor="w")
        else:
            left, right, top, bottom = 45, w - 20, 25, h - 40
            canvas.create_line(left, top, left, bottom, fill=BORDER)
            canvas.create_line(left, bottom, right, bottom, fill=BORDER)
            for tick in range(peak + 1):
                y = bottom - (bottom - top) * tick / peak
                canvas.create_line(left, y, right, y, fill="#102b4a")
                canvas.create_text(left - 12, y, text=str(tick), fill=MUTED,
                                   font=("Arial", 8))
            slot = (right - left) / len(items)
            for i, (name, value, color) in enumerate(items):
                x = left + slot * i + slot * 0.26
                height = (bottom - top) * value / peak
                canvas.create_rectangle(x, bottom - height, x + slot * 0.48,
                                        bottom, fill=color, outline="")
                canvas.create_text(x + slot * 0.24, bottom - height - 10,
                                   text=str(value), fill=WHITE,
                                   font=("Arial", 9, "bold"))
                canvas.create_text(x + slot * 0.24, bottom + 16, text=name,
                                   fill=MUTED, font=("Arial", 9))

    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------

    def dashboard_page(self):
        body = self.body
        body.grid_columnconfigure(0, weight=5)
        body.grid_columnconfigure(1, weight=3, minsize=350)
        body.grid_rowconfigure(1, weight=1)       # row 1 absorbs spare height

        self.build_banner(body).grid(row=0, column=0, columnspan=2,
                                     sticky="ew", pady=(0, 10))
        left = tk.Frame(body, bg=BG)
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        right = tk.Frame(body, bg=BG)
        right.grid(row=1, column=1, sticky="nsew")

        self.dash_cards(left)
        self.dash_middle(left)
        self.dash_recent(left)
        self.dash_bottom(left)

        self.dash_alerts(right)
        self.dash_stats(right)
        self.dash_reports(right)

    def build_banner(self, parent):
        banner = self.panel(parent)
        art = tk.Canvas(banner, height=84, bg=PANEL, highlightthickness=0)
        art.pack(fill="both", expand=True)
        title = f"Welcome back, {self.analyst}"
        subtitle = "Here's what's happening in your security environment today."
        art.bind("<Configure>",
                 lambda e: self.draw_banner(art, e.width, e.height, title,
                                            subtitle, PAGE_IMAGES["Dashboard"], True))
        return banner

    def dash_cards(self, parent):
        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x", pady=(0, 10))
        total = len(self.incidents)
        sev = self.severity_counts()
        high = sev["High"] + sev["Critical"]

        def pct(n):
            return f"{round(100 * n / total)}%" if total else "0%"

        cards = [
            ("Total Incidents", total, f"{len(self.active_incidents())} active now", RED, "!"),
            ("High Severity", high, f"{pct(high)} of total · requires attention", ORANGE, "▲"),
            ("Medium Severity", sev["Medium"], f"{pct(sev['Medium'])} of total · under investigation", BLUE, "i"),
            ("Low Severity", sev["Low"], f"{pct(sev['Low'])} of total · resolved / monitored", GREEN, "✓"),
        ]
        for col, (title, value, desc, color, symbol) in enumerate(cards):
            row.grid_columnconfigure(col, weight=1, uniform="card")
            card = tk.Frame(row, bg=CARD, highlightbackground=color, highlightthickness=1)
            card.grid(row=0, column=col, sticky="nsew", padx=(0, 8 if col < 3 else 0))
            icon = tk.Canvas(card, width=46, height=46, bg=CARD, highlightthickness=0)
            icon.pack(side="left", padx=(10, 4), pady=10)
            icon.create_oval(3, 3, 43, 43, outline=color, width=2)
            icon.create_text(23, 23, text=symbol, fill=color, font=("Arial", 16, "bold"))
            text = tk.Frame(card, bg=CARD)
            text.pack(side="left", fill="x", expand=True, pady=8)
            self.label(text, title, 9, WHITE, bg=CARD).pack(anchor="w")
            self.label(text, str(value), 24, WHITE, True, bg=CARD).pack(anchor="w")
            self.label(text, desc, 7, MUTED, bg=CARD, wraplength=150,
                       justify="left").pack(anchor="w")

    def dash_middle(self, parent):
        mid = tk.Frame(parent, bg=BG)
        mid.pack(fill="both", expand=True, pady=(0, 10))
        mid.grid_rowconfigure(0, weight=1)
        mid.grid_columnconfigure(0, weight=3, uniform="mid")
        mid.grid_columnconfigure(1, weight=2, uniform="mid")

        # ---- global threat map
        map_panel = self.panel(mid)
        map_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.label(map_panel, "Global Threat Activity", 11, WHITE, True).pack(
            anchor="w", padx=12, pady=(10, 4))
        canvas = tk.Canvas(map_panel, height=170, bg=PANEL, highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        canvas.bind("<Configure>",
                    lambda e: self.draw_threat_map(canvas, e.width, e.height))

        sources = tk.Frame(map_panel, bg=CARD, highlightbackground=BORDER,
                           highlightthickness=1)
        sources.place(relx=1.0, x=-14, y=40, anchor="ne")
        self.label(sources, "Top Attack Sources", 8, WHITE, True, bg=CARD).pack(
            anchor="w", padx=8, pady=(6, 3))
        for name, count in self.top_sources():
            line = tk.Frame(sources, bg=CARD)
            line.pack(fill="x", padx=8, pady=1)
            self.label(line, name, 8, WHITE, bg=CARD, width=14, anchor="w").pack(side="left")
            self.label(line, str(count), 8, WHITE, True, bg=CARD).pack(side="right")
        self.label(sources, "simulated locations", 7, MUTED, bg=CARD).pack(
            anchor="w", padx=8, pady=(2, 5))

        legend = tk.Frame(map_panel, bg=PANEL)
        legend.place(relx=0, x=14, rely=1.0, y=-14, anchor="sw")
        for name, color in [("High", RED), ("Medium", ORANGE), ("Low", GREEN)]:
            line = tk.Frame(legend, bg=PANEL)
            line.pack(anchor="w")
            self.label(line, "●", 9, color).pack(side="left")
            self.label(line, " " + name, 8, WHITE).pack(side="left")

        # ---- donut by type
        donut = self.panel(mid)
        donut.grid(row=0, column=1, sticky="nsew")
        self.label(donut, "Incidents by Type", 11, WHITE, True).pack(
            anchor="w", padx=12, pady=(10, 4))
        chart = tk.Canvas(donut, height=170, bg=PANEL, highlightthickness=0)
        chart.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        chart.bind("<Configure>",
                   lambda e: self.draw_type_donut(chart, e.width, e.height))

    def draw_type_donut(self, chart, width, height):
        chart.delete("all")
        width, height = max(width, 260), max(height, 150)
        ranked = self.type_counts()
        shown = ranked[:4]
        other = sum(v for _, v in ranked[4:])
        if other:
            shown.append(("Other", other))
        total = len(self.incidents)
        segments = [(v, TYPE_COLORS[i % len(TYPE_COLORS)])
                    for i, (_, v) in enumerate(shown)]
        cx, cy = width * 0.26, height / 2
        radius = max(30, min(62, height / 2 - 14, width * 0.2))
        self.draw_ring(chart, cx, cy, radius, 20, segments)
        chart.create_text(cx, cy - 8, text=str(total), fill=WHITE, font=("Arial", 22, "bold"))
        chart.create_text(cx, cy + 14, text="Total", fill=MUTED, font=("Arial", 9))
        y = cy - 30 * (len(shown) - 1) / 2
        for i, (name, value) in enumerate(shown):
            color = TYPE_COLORS[i % len(TYPE_COLORS)]
            share = round(100 * value / total) if total else 0
            chart.create_oval(width * .52, y - 5, width * .52 + 10, y + 5, fill=color, outline="")
            chart.create_text(width * .52 + 18, y, text=name, fill=WHITE,
                              font=("Arial", 9), anchor="w")
            chart.create_text(width - 12, y, text=f"{value} ({share}%)",
                              fill=MUTED, font=("Arial", 9), anchor="e")
            y += 30

    def dash_recent(self, parent):
        panel = self.panel(parent)
        panel.pack(fill="x", pady=(0, 10))
        head = tk.Frame(panel, bg=PANEL)
        head.pack(fill="x", padx=12, pady=(10, 4))
        self.label(head, "Recent Incidents", 11, WHITE, True).pack(side="left")
        self.button(head, "View All →", lambda: self.show_page("Incidents"),
                    bg=PANEL, fg=BLUE, padx=5, pady=2).pack(side="right")

        grid = tk.Frame(panel, bg=PANEL)
        grid.pack(fill="x", padx=12, pady=(0, 10))
        grid.grid_columnconfigure(2, weight=1)
        headers = ["ID", "Date & Time", "Type", "Severity", "Status", "Source IP", "Action"]
        for col, text in enumerate(headers):
            self.label(grid, text, 8, MUTED).grid(row=0, column=col, sticky="w", padx=6, pady=4)
        tk.Frame(grid, bg=BORDER, height=1).grid(row=1, column=0, columnspan=7, sticky="ew")

        recent = sorted(self.incidents, key=lambda i: i["id"], reverse=True)[:6]
        for n, inc in enumerate(recent):
            r = 2 + 2 * n
            self.label(grid, incident_code(inc["id"]), 9, WHITE).grid(row=r, column=0, sticky="w", padx=6, pady=5)
            self.label(grid, inc["created"], 9, WHITE).grid(row=r, column=1, sticky="w", padx=6)
            self.label(grid, inc["type"], 9, WHITE).grid(row=r, column=2, sticky="w", padx=6)
            self.sev_pill(grid, inc["severity"]).grid(row=r, column=3, sticky="w", padx=6)
            self.status_pill(grid, inc["status"]).grid(row=r, column=4, sticky="w", padx=6)
            self.label(grid, inc["source"], 9, WHITE).grid(row=r, column=5, sticky="w", padx=6)
            tk.Button(grid, text="View", bg="#0c2a50", fg=BLUE, relief="flat", bd=0,
                      cursor="hand2", font=("Arial", 8, "bold"), padx=10,
                      activebackground=BLUE, activeforeground=WHITE,
                      command=lambda i=inc["id"]: self.view_incident(i)
                      ).grid(row=r, column=6, sticky="w", padx=6)
            tk.Frame(grid, bg=BORDER, height=1).grid(row=r + 1, column=0,
                                                     columnspan=7, sticky="ew")
        if not recent:
            self.label(grid, "No incidents recorded yet.", 9, MUTED).grid(
                row=2, column=0, columnspan=7, pady=14)

    def dash_bottom(self, parent):
        bottom = tk.Frame(parent, bg=BG)
        bottom.pack(fill="x")
        bottom.grid_columnconfigure(0, weight=1, uniform="b")
        bottom.grid_columnconfigure(1, weight=1, uniform="b")

        # ---- security risk level
        risk = self.panel(bottom)
        risk.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.label(risk, "Security Risk Level", 11, WHITE, True).pack(anchor="w", padx=12, pady=(10, 4))
        inner = tk.Frame(risk, bg=PANEL)
        inner.pack(fill="x", padx=8, pady=(0, 10))
        level, score = self.overall_risk()
        ring = tk.Canvas(inner, width=140, height=140, bg=PANEL, highlightthickness=0)
        ring.pack(side="left", padx=6)
        self.draw_ring(ring, 70, 70, 54, 12,
                       [(score, LEVEL_COLOR[level]), (100 - score, "#123e70")])
        ring.create_text(70, 64, text=level, fill=WHITE, font=("Arial", 14, "bold"))
        ring.create_text(70, 84, text="Overall Risk", fill=MUTED, font=("Arial", 8))
        cats = tk.Frame(inner, bg=PANEL)
        cats.pack(side="left", fill="x", expand=True, padx=10)
        for name, lvl in self.category_levels().items():
            line = tk.Frame(cats, bg=PANEL)
            line.pack(fill="x", pady=3)
            self.label(line, "●", 9, LEVEL_COLOR[lvl]).pack(side="left")
            self.label(line, " " + name, 9, WHITE, width=12, anchor="w").pack(side="left")
            self.label(line, lvl, 9, LEVEL_COLOR[lvl], True).pack(side="right")

        # ---- quick actions
        quick = self.panel(bottom)
        quick.grid(row=0, column=1, sticky="nsew")
        self.label(quick, "Quick Actions", 11, WHITE, True).pack(anchor="w", padx=12, pady=(10, 6))
        tiles = tk.Frame(quick, bg=PANEL)
        tiles.pack(fill="both", expand=True, padx=8, pady=(0, 10))
        tiles.grid_rowconfigure(0, weight=1)
        actions = [
            ("＋\nAdd\nIncident", self.add_incident_dialog),
            ("▤\nGenerate\nReport", lambda: self.show_page("Reports")),
            ("⌕\nSearch\nThreats", self.open_threat_search),
            ("▥\nView\nAnalytics", lambda: self.show_page("Analytics")),
        ]
        for col, (text, command) in enumerate(actions):
            tiles.grid_columnconfigure(col, weight=1, uniform="q")
            tk.Button(tiles, text=text, command=command, bg=CARD2, fg=CYAN,
                      activebackground=BLUE, activeforeground=WHITE,
                      relief="flat", bd=0, cursor="hand2",
                      font=("Arial", 9, "bold"), pady=10
                      ).grid(row=0, column=col, sticky="nsew", padx=3)

    def open_threat_search(self):
        self.show_page("Threat Intelligence")
        if self.threat_entry is not None:
            self.threat_entry.focus_set()

    def dash_alerts(self, parent):
        panel = self.panel(parent)
        panel.pack(fill="x", pady=(0, 10))
        head = tk.Frame(panel, bg=PANEL)
        head.pack(fill="x", padx=12, pady=(10, 4))
        self.label(head, "Recent Alerts", 12, WHITE, True).pack(side="left")
        self.button(head, "View All →", lambda: self.show_page("Incidents"),
                    bg=PANEL, fg=BLUE, padx=5, pady=2).pack(side="right")

        recent = sorted(self.incidents, key=lambda i: i["id"], reverse=True)[:5]
        for inc in recent:
            color = SEV_COLOR.get(inc["severity"], MUTED)
            row = tk.Frame(panel, bg=PANEL, cursor="hand2")
            row.pack(fill="x", padx=10, pady=5)
            icon = tk.Canvas(row, width=42, height=42, bg=PANEL, highlightthickness=0)
            icon.pack(side="left", padx=(0, 8))
            icon.create_oval(3, 3, 39, 39, outline=color, width=2, fill="#10172f")
            icon.create_text(21, 21, text="!", fill=color, font=("Arial", 15, "bold"))
            info = tk.Frame(row, bg=PANEL)
            info.pack(side="left", fill="x", expand=True)
            self.label(info, inc["title"], 9, WHITE, True, wraplength=180,
                       justify="left").pack(anchor="w")
            self.label(info, f"from {inc['source']}", 8, MUTED).pack(anchor="w")
            self.sev_pill(info, inc["severity"]).pack(anchor="w", pady=(3, 0))
            self.label(row, time_ago(parse_created(inc["created"])), 8, MUTED).pack(side="right")
            for widget in (row, icon, info):
                widget.bind("<Button-1>", lambda e, i=inc["id"]: self.view_incident(i))
        if not recent:
            self.label(panel, "No alerts.", 9, MUTED).pack(pady=14)

    def dash_stats(self, parent):
        panel = self.panel(parent)
        panel.pack(fill="both", expand=True, pady=(0, 10))
        self.label(panel, "Threat Statistics", 12, WHITE, True).pack(anchor="w", padx=12, pady=(10, 0))
        self.label(panel, "Threats detected (last 7 days with activity)", 8, MUTED).pack(
            anchor="w", padx=12, pady=(0, 4))
        chart = tk.Canvas(panel, height=120, bg=PANEL, highlightthickness=0)
        chart.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        labels, values = self.daily_series()
        chart.bind("<Configure>",
                   lambda e: self.draw_line_chart(chart, labels, values, e.width, e.height))

    def dash_reports(self, parent):
        panel = self.panel(parent)
        panel.pack(fill="x")
        head = tk.Frame(panel, bg=PANEL)
        head.pack(fill="x", padx=12, pady=(10, 4))
        self.label(head, "Latest Reports", 12, WHITE, True).pack(side="left")
        self.button(head, "View All →", lambda: self.show_page("Reports"),
                    bg=PANEL, fg=BLUE, padx=5, pady=2).pack(side="right")
        stamp = datetime.now().strftime("%b %d, %Y")
        for kind, name in REPORTS:
            size = len(self.build_report(kind).encode("utf-8")) / 1024
            row = tk.Frame(panel, bg=PANEL)
            row.pack(fill="x", padx=12, pady=5)
            self.label(row, "▤", 18, BLUE).pack(side="left", padx=(0, 8))
            info = tk.Frame(row, bg=PANEL)
            info.pack(side="left", fill="x", expand=True)
            self.label(info, name, 9, WHITE, True).pack(anchor="w")
            self.label(info, f"{stamp}  |  {size:.1f} KB", 8, MUTED).pack(anchor="w")
            tk.Button(row, text="Download", bg="#0c2a50", fg=BLUE, relief="flat",
                      bd=0, cursor="hand2", font=("Arial", 8, "bold"), padx=12,
                      pady=5, activebackground=BLUE, activeforeground=WHITE,
                      command=lambda k=kind: self.download_report(k)).pack(side="right")
        tk.Frame(panel, bg=PANEL, height=6).pack()

    # --------------------------------------------------------
    # INCIDENTS PAGE
    # --------------------------------------------------------

    def incidents_page(self):
        head = tk.Frame(self.body, bg=BG)
        head.pack(fill="x", pady=(0, 8))
        self.label(head, "Incident Management", 21, WHITE, True, bg=BG).pack(side="left")
        self.button(head, "+ Add Incident", self.add_incident_dialog, bg=BLUE).pack(side="right")

        bar = tk.Frame(self.body, bg=BG)
        bar.pack(fill="x", pady=(0, 8))
        self.sev_filter = tk.StringVar(value="All")
        self.status_filter = tk.StringVar(value="All")
        for var, values in ((self.sev_filter, ["All"] + SEVERITIES),
                            (self.status_filter, ["All"] + STATUSES)):
            combo = ttk.Combobox(bar, textvariable=var, values=values,
                                 state="readonly", width=13)
            combo.pack(side="left", ipady=4, padx=(0, 6))
            combo.bind("<<ComboboxSelected>>", lambda e: self.render_incident_table())
        self.button(bar, "View Details", self.view_selected).pack(side="left", padx=3)
        self.button(bar, "Update Status", self.update_selected).pack(side="left", padx=3)
        self.button(bar, "Delete Selected", self.delete_selected, bg="#54223b").pack(side="left", padx=3)
        self.button(bar, "Export CSV", self.export_csv, fg=CYAN).pack(side="left", padx=3)

        if self.search_query:
            chip = tk.Frame(self.body, bg=BG)
            chip.pack(fill="x", pady=(0, 6))
            self.label(chip, f'Search: "{self.search_query}"', 9, CYAN, True, bg=BG).pack(side="left")
            self.button(chip, "Clear", self.clear_search, bg=BG, fg=ORANGE,
                        padx=6, pady=2).pack(side="left", padx=8)

        self.table_host = self.panel(self.body)
        self.table_host.pack(fill="both", expand=True)
        self.render_incident_table()

    def clear_search(self):
        self.search_query = ""
        self.search_entry.delete(0, "end")
        self.show_page("Incidents")

    def render_incident_table(self):
        for widget in self.table_host.winfo_children():
            widget.destroy()
        records = self.filtered_incidents()
        if not records:
            self.tree = None
            self.label(self.table_host, "No incidents match the current filters.",
                       10, MUTED).pack(pady=40)
            return

        columns = ("id", "created", "title", "type", "severity", "status", "source", "risk")
        tree = ttk.Treeview(self.table_host, columns=columns, show="headings",
                            height=min(16, max(len(records), 4)),
                            selectmode="browse")
        for key, title, width in [("id", "ID", 80), ("created", "Date & Time", 115),
                                  ("title", "Incident", 240), ("type", "Type", 130),
                                  ("severity", "Severity", 80), ("status", "Status", 105),
                                  ("source", "Source IP", 120), ("risk", "Risk", 50)]:
            tree.heading(key, text=title)
            tree.column(key, width=width, anchor="w")
        for level, color in SEV_COLOR.items():
            tree.tag_configure(level, foreground=color)
        for inc in records:
            tree.insert("", "end", tags=(inc["severity"],), values=(
                incident_code(inc["id"]), inc["created"], inc["title"],
                inc["type"], inc["severity"], inc["status"], inc["source"],
                risk_score(inc)))
        tree.pack(fill="both", expand=True, padx=8, pady=8)
        tree.bind("<Double-1>", lambda e: self.view_selected())
        self.tree = tree

    def selected_id(self):
        if self.tree is None or not self.tree.winfo_exists():
            messagebox.showinfo("Select incident", "Open the Incidents page and select a row.")
            return None
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Select incident", "Select an incident row first.")
            return None
        code = str(self.tree.item(selection[0], "values")[0])
        try:
            return int(code.replace("CG-", ""))
        except ValueError:
            return None

    def view_selected(self):
        incident_id = self.selected_id()
        if incident_id is not None:
            self.view_incident(incident_id)

    def update_selected(self):
        incident_id = self.selected_id()
        incident = self.find(incident_id) if incident_id is not None else None
        if incident:
            self.status_dialog(incident)

    def delete_selected(self):
        incident_id = self.selected_id()
        incident = self.find(incident_id) if incident_id is not None else None
        if not incident:
            return
        if incident["status"] != "Resolved":
            messagebox.showwarning("Cannot delete",
                                   "Only Resolved incidents can be deleted.")
            return
        if messagebox.askyesno("Confirm deletion", f'Delete "{incident["title"]}"?'):
            self.incidents.remove(incident)
            self.save_data()
            self.show_page(self.current_page)

    # --------------------------------------------------------
    # DIALOGS: ADD / VIEW / STATUS
    # --------------------------------------------------------

    def add_incident_dialog(self):
        dialog = self.make_dialog("Register Security Incident", 470, 600)
        form = tk.Frame(dialog, bg=PANEL, padx=22, pady=16,
                        highlightbackground=BORDER, highlightthickness=1)
        form.pack(fill="both", expand=True, padx=12, pady=12)
        self.label(form, "REGISTER INCIDENT", 16, CYAN, True).pack(anchor="w", pady=(0, 8))

        def caption(text):
            self.label(form, text, 9, MUTED).pack(anchor="w", pady=(8, 3))

        def entry():
            widget = tk.Entry(form, bg=CARD, fg=WHITE, insertbackground=WHITE, relief="flat")
            widget.pack(fill="x", ipady=7)
            return widget

        caption("Incident title")
        title = entry()
        caption("Incident type")
        kind = tk.StringVar(value="Phishing")
        ttk.Combobox(form, textvariable=kind, state="readonly", values=TYPES).pack(fill="x", ipady=4)
        caption("Severity")
        severity = tk.StringVar(value="Medium")
        ttk.Combobox(form, textvariable=severity, state="readonly", values=SEVERITIES).pack(fill="x", ipady=4)
        caption("Source IPv4 address (e.g. 192.168.1.45)")
        source = entry()
        caption("Indicators / notes")
        notes = entry()

        def save():
            text = title.get().strip()
            ip = source.get().strip()
            note = notes.get().strip()
            problem = None
            if not text:
                problem = "Please enter an incident title."
            elif not valid_ip(ip):
                problem = "Enter a valid IPv4 address (four numbers 0-255)."
            elif severity.get() == "Critical" and not note:
                problem = "Critical incidents must include notes."
            else:
                for item in self.incidents:
                    if (item["title"].lower() == text.lower()
                            and item["source"] == ip
                            and item["status"] != "Resolved"):
                        problem = f"Duplicate of open incident {incident_code(item['id'])}."
                        break
            if problem:
                messagebox.showwarning("Cannot save", problem, parent=dialog)
                return
            self.incidents.append({
                "id": self.next_id(),
                "created": datetime.now().strftime("%b %d, %H:%M"),
                "title": text, "type": kind.get(), "severity": severity.get(),
                "status": "Open", "source": ip, "notes": note})
            self.save_data()
            dialog.destroy()
            self.show_page(self.current_page)

        self.button(form, "SAVE INCIDENT", save, bg=BLUE).pack(fill="x", pady=(18, 0))

    def view_incident(self, incident_id):
        incident = self.find(incident_id)
        if incident is None:
            messagebox.showinfo("Not found", "That incident no longer exists.")
            return
        dialog = self.make_dialog(f"Incident {incident_code(incident_id)}", 520, 470)
        box = tk.Frame(dialog, bg=PANEL, padx=20, pady=16,
                       highlightbackground=BORDER, highlightthickness=1)
        box.pack(fill="both", expand=True, padx=12, pady=12)
        self.label(box, f"{incident_code(incident_id)}  ·  {incident['title']}",
                   14, CYAN, True, wraplength=450, justify="left").pack(anchor="w", pady=(0, 10))
        rows = [("Type", incident["type"]), ("Severity", incident["severity"]),
                ("Status", incident["status"]), ("Source IP", incident["source"]),
                ("Location", country_of(incident["source"]) + " (simulated)"),
                ("Created", incident["created"]),
                ("Notes", incident["notes"] or "—")]
        for name, value in rows:
            line = tk.Frame(box, bg=PANEL)
            line.pack(fill="x", pady=3)
            self.label(line, name, 9, MUTED, width=10, anchor="w").pack(side="left")
            self.label(line, value, 9, WHITE, wraplength=330, justify="left").pack(side="left")
        score = risk_score(incident)
        self.label(box, f"Risk score: {score}/100", 9, MUTED).pack(anchor="w", pady=(10, 3))
        bar = tk.Canvas(box, width=320, height=14, bg=CARD, highlightthickness=0)
        bar.pack(anchor="w")
        bar.create_rectangle(0, 0, 320 * score / 100, 14,
                             fill=LEVEL_COLOR[level_of(score)], outline="")
        actions = tk.Frame(box, bg=PANEL)
        actions.pack(fill="x", pady=(18, 0))
        self.button(actions, "Update Status",
                    lambda: (dialog.destroy(), self.status_dialog(incident)),
                    bg=BLUE).pack(side="left")
        self.button(actions, "Close", dialog.destroy).pack(side="left", padx=8)

    def status_dialog(self, incident):
        dialog = self.make_dialog("Update status", 380, 230)
        box = tk.Frame(dialog, bg=PANEL, padx=20, pady=16,
                       highlightbackground=BORDER, highlightthickness=1)
        box.pack(fill="both", expand=True, padx=12, pady=12)
        self.label(box, f"{incident_code(incident['id'])}: currently {incident['status']}",
                   10, WHITE, True).pack(anchor="w", pady=(0, 10))
        nxt = min(STATUSES.index(incident["status"]) + 1, len(STATUSES) - 1)
        choice = tk.StringVar(value=STATUSES[nxt])
        ttk.Combobox(box, textvariable=choice, values=STATUSES,
                     state="readonly").pack(fill="x", ipady=4)

        def apply():
            problem = self.status_error(incident, choice.get())
            if problem:
                messagebox.showwarning("Not allowed", problem, parent=dialog)
                return
            incident["status"] = choice.get()
            self.save_data()
            dialog.destroy()
            self.show_page(self.current_page)

        self.button(box, "APPLY", apply, bg=BLUE).pack(fill="x", pady=(16, 0))

    # --------------------------------------------------------
    # THREAT INTELLIGENCE
    # --------------------------------------------------------

    def threat_page(self):
        self.page_heading("Threat Intelligence",
                          "Learn about common cybersecurity incidents and first response steps.")
        bar = tk.Frame(self.body, bg=BG)
        bar.pack(fill="x", pady=(0, 8))
        self.label(bar, "Search threats:", 9, MUTED, bg=BG).pack(side="left")
        self.threat_var = tk.StringVar()
        self.threat_entry = tk.Entry(bar, textvariable=self.threat_var, width=34,
                                     bg=CARD, fg=WHITE, insertbackground=WHITE,
                                     relief="flat", font=("Arial", 10))
        self.threat_entry.pack(side="left", padx=8, ipady=6)
        self.threat_entry.bind("<KeyRelease>", lambda e: self.render_threat_cards())
        self.grid_host = tk.Frame(self.body, bg=BG)
        self.grid_host.pack(fill="both", expand=True)
        self.render_threat_cards()
        self.label(self.body, "Risk scores are educational rules, not real threat detection.",
                   8, MUTED, bg=BG).pack(anchor="w", pady=6)

    def render_threat_cards(self):
        for widget in self.grid_host.winfo_children():
            widget.destroy()
        query = self.threat_var.get().strip().lower()
        shown = [t for t in THREATS if not query or query in " ".join(
            [t[0], t[2], t[3]]).lower()]
        self.grid_host.grid_columnconfigure(0, weight=1, uniform="t")
        self.grid_host.grid_columnconfigure(1, weight=1, uniform="t")
        if not shown:
            self.label(self.grid_host, "No matching threats.", 10, MUTED, bg=BG).grid(row=0, column=0, pady=20)
            return
        for index, (name, color, description, action) in enumerate(shown):
            matching = [i for i in self.incidents if i["type"].upper() == name]
            active = [i for i in matching if i["status"] in ("Open", "Investigating")]
            card = self.panel(self.grid_host)
            card.grid(row=index // 2, column=index % 2, sticky="nsew", padx=6, pady=6)
            self.label(card, "◈  " + name, 12, color, True).pack(anchor="w", padx=14, pady=(12, 6))
            self.label(card, description, 9, WHITE, wraplength=400, justify="left").pack(
                anchor="w", padx=14, pady=(0, 8))
            self.label(card, "RECOMMENDED FIRST STEP", 8, CYAN, True).pack(anchor="w", padx=14)
            self.label(card, action, 9, MUTED, wraplength=400, justify="left").pack(
                anchor="w", padx=14, pady=(3, 8))
            self.label(card, f"Recorded: {len(matching)}   |   Active: {len(active)}",
                       9, color, True).pack(anchor="w", padx=14, pady=(0, 12))

    # --------------------------------------------------------
    # REPORTS
    # --------------------------------------------------------

    def build_report(self, kind):
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        counts = self.severity_counts()
        lines = []
        if kind == "weekly":
            lines += ["CYBERGUARD WEEKLY SECURITY REPORT", f"Generated: {stamp}",
                      "Educational simulator; not a live threat assessment.", "",
                      f"Total incidents: {len(self.incidents)}",
                      f"Active incidents: {len(self.active_incidents())}", ""]
            lines += [f"{lvl} severity: {n}" for lvl, n in counts.items()]
            level, score = self.overall_risk()
            lines += ["", f"Overall risk: {level} (average active risk {score})", "",
                      "RISK BY AREA"]
            lines += [f"  {k}: {v}" for k, v in self.category_levels().items()]
        elif kind == "summary":
            lines += ["CYBERGUARD INCIDENT SUMMARY", f"Generated: {stamp}", "",
                      "INCIDENTS"]
            for i in sorted(self.incidents, key=lambda x: x["id"], reverse=True):
                lines.append(f"{incident_code(i['id'])} | {i['created']} | {i['severity']} | "
                             f"{i['status']} | {i['type']} | {i['title']} | {i['source']}")
        else:
            lines += ["CYBERGUARD THREAT INTELLIGENCE REPORT", f"Generated: {stamp}", ""]
            for name, _, desc, action in THREATS:
                total = sum(1 for i in self.incidents if i["type"].upper() == name)
                lines += [f"{name} ({total} recorded)", f"  What: {desc}",
                          f"  First step: {action}", ""]
        return "\n".join(lines)

    def download_report(self, kind):
        name = dict(REPORTS)[kind]
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text files", "*.txt")],
            initialfile=name.split(" (")[0].replace(" ", "_").lower() + ".txt")
        if not path:
            return
        try:
            Path(path).write_text(self.build_report(kind), encoding="utf-8")
            messagebox.showinfo("Report saved", f"{name} saved successfully.")
        except OSError as error:
            messagebox.showerror("Report error", str(error))

    def reports_page(self):
        self.page_heading("Reports & Exports",
                          "Download reports and export incident records for spreadsheets and backups.")
        cards = [(name, "Generate a readable text report from the current data.",
                  "DOWNLOAD", lambda k=kind: self.download_report(k))
                 for kind, name in REPORTS]
        cards += [("CSV Incident Register", "Export all records to a spreadsheet-friendly CSV file.",
                   "EXPORT CSV", self.export_csv),
                  ("JSON Data Backup", "Save a portable copy of all incident records.",
                   "BACK UP JSON", self.export_json)]
        for title, description, text, command in cards:
            card = self.panel(self.body)
            card.pack(fill="x", pady=6)
            self.label(card, "▤  " + title, 11, CYAN, True).pack(anchor="w", padx=16, pady=(12, 4))
            self.label(card, description, 9, MUTED).pack(anchor="w", padx=16, pady=(0, 8))
            self.button(card, text, command, bg=BLUE).pack(anchor="w", padx=16, pady=(0, 12))

    def export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")],
            initialfile="cyberguard_incidents.csv")
        if not path:
            return
        fields = ["id", "created", "title", "type", "severity", "status", "source", "notes"]
        try:
            with open(path, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=fields)
                writer.writeheader()
                for item in self.incidents:
                    writer.writerow({k: item.get(k, "") for k in fields})
            messagebox.showinfo("Export complete", "CSV file saved successfully.")
        except OSError as error:
            messagebox.showerror("Export error", str(error))

    def export_json(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON files", "*.json")],
            initialfile="cyberguard_backup.json")
        if not path:
            return
        try:
            Path(path).write_text(json.dumps(self.incidents, indent=2), encoding="utf-8")
            messagebox.showinfo("Backup complete", "JSON backup saved successfully.")
        except OSError as error:
            messagebox.showerror("Export error", str(error))

    # --------------------------------------------------------
    # ANALYTICS
    # --------------------------------------------------------

    def analytics_page(self):
        self.page_heading("Security Analytics",
                          "Statistics calculated from locally saved incident records.")
        counts = self.severity_counts()
        row = tk.Frame(self.body, bg=BG)
        row.pack(fill="x", pady=(0, 10))
        for col, level in enumerate(("Critical", "High", "Medium", "Low")):
            row.grid_columnconfigure(col, weight=1, uniform="a")
            card = self.panel(row)
            card.grid(row=0, column=col, sticky="nsew", padx=(0, 8 if col < 3 else 0))
            self.label(card, level.upper(), 9, SEV_COLOR[level], True).pack(anchor="w", padx=13, pady=(12, 2))
            self.label(card, str(counts[level]), 24, WHITE, True).pack(anchor="w", padx=13, pady=(0, 12))

        pair = tk.Frame(self.body, bg=BG)
        pair.pack(fill="both", expand=True, pady=(0, 10))
        pair.grid_rowconfigure(0, weight=1)
        pair.grid_columnconfigure(0, weight=1, uniform="p")
        pair.grid_columnconfigure(1, weight=1, uniform="p")

        sev_panel = self.panel(pair)
        sev_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.label(sev_panel, "INCIDENTS BY SEVERITY", 10, CYAN, True).pack(anchor="w", padx=14, pady=10)
        c1 = tk.Canvas(sev_panel, height=220, bg=PANEL, highlightthickness=0)
        c1.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        sev_items = [(lvl, counts[lvl], SEV_COLOR[lvl]) for lvl in ("Critical", "High", "Medium", "Low")]
        c1.bind("<Configure>", lambda e: self.draw_bars(c1, sev_items, e.width, e.height))

        type_panel = self.panel(pair)
        type_panel.grid(row=0, column=1, sticky="nsew")
        self.label(type_panel, "INCIDENTS BY TYPE", 10, CYAN, True).pack(anchor="w", padx=14, pady=10)
        c2 = tk.Canvas(type_panel, height=220, bg=PANEL, highlightthickness=0)
        c2.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        type_items = [(n, v, TYPE_COLORS[i % len(TYPE_COLORS)])
                      for i, (n, v) in enumerate(self.type_counts())]
        c2.bind("<Configure>", lambda e: self.draw_bars(c2, type_items, e.width, e.height, True))

        trend = self.panel(self.body)
        trend.pack(fill="both", expand=True)
        self.label(trend, "INCIDENTS PER DAY", 10, CYAN, True).pack(anchor="w", padx=14, pady=10)
        c3 = tk.Canvas(trend, height=200, bg=PANEL, highlightthickness=0)
        c3.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        labels, values = self.daily_series()
        c3.bind("<Configure>", lambda e: self.draw_line_chart(c3, labels, values, e.width, e.height))

    # --------------------------------------------------------
    # SETTINGS
    # --------------------------------------------------------

    def settings_page(self):
        self.page_heading("Settings", "Application information and local data controls.")

        profile = self.panel(self.body)
        profile.pack(fill="x", pady=(0, 10))
        self.label(profile, "ANALYST PROFILE", 10, CYAN, True).pack(anchor="w", padx=16, pady=(14, 6))
        line = tk.Frame(profile, bg=PANEL)
        line.pack(anchor="w", padx=16, pady=(0, 14))
        name_var = tk.StringVar(value=self.analyst)
        tk.Entry(line, textvariable=name_var, width=26, bg=CARD, fg=WHITE,
                 insertbackground=WHITE, relief="flat").pack(side="left", ipady=6)

        def save_name():
            value = name_var.get().strip()
            if not value:
                messagebox.showwarning("Missing name", "Please enter a name.")
                return
            self.analyst = value
            self.save_settings()
            self.user_label.configure(text=value)
            messagebox.showinfo("Saved", "Analyst name updated.")

        self.button(line, "Save name", save_name, bg=BLUE).pack(side="left", padx=8)

        info = self.panel(self.body)
        info.pack(fill="x", pady=(0, 10))
        self.label(info, "APPLICATION", 10, CYAN, True).pack(anchor="w", padx=16, pady=(14, 6))
        self.label(info, "CyberGuard v1.0  •  Threat Intelligence & Incident Response",
                   10, WHITE).pack(anchor="w", padx=16, pady=3)
        self.label(info, f"Data file: {DATA_FILE.name}   ({len(self.incidents)} records)",
                   9, MUTED).pack(anchor="w", padx=16, pady=3)
        self.label(info, "Records are saved locally beside main.py.", 9, MUTED).pack(
            anchor="w", padx=16, pady=(3, 14))

        limits = self.panel(self.body)
        limits.pack(fill="x", pady=(0, 10))
        self.label(limits, "EDUCATIONAL LIMITATIONS", 10, ORANGE, True).pack(anchor="w", padx=16, pady=(14, 6))
        self.label(limits,
                   "CyberGuard does not monitor live network traffic or scan devices. Sample "
                   "alerts and map locations are simulated, and risk scores use simple rules.",
                   9, MUTED, wraplength=850, justify="left").pack(anchor="w", padx=16, pady=(0, 14))

        buttons = tk.Frame(self.body, bg=BG)
        buttons.pack(anchor="w")
        self.button(buttons, "Restore demo sample data", self.restore_demo, fg=CYAN).pack(side="left", padx=(0, 8))
        self.button(buttons, "Clear all incidents", self.clear_all, bg="#54223b").pack(side="left")

    def restore_demo(self):
        if messagebox.askyesno("Restore demo data",
                               "Replace all current incidents with the demo records?"):
            self.incidents = build_seed()
            self.save_data()
            self.show_page("Dashboard")

    def clear_all(self):
        if messagebox.askyesno("Clear all", "Delete every incident? This cannot be undone."):
            self.incidents = []
            self.save_data()
            self.show_page("Dashboard")


# ------------------------------------------------------------
# START APPLICATION
# ------------------------------------------------------------

def launch_gui():
    root = tk.Tk()
    CyberGuardApp(root)
    root.mainloop()


if __name__ == "__main__":
    if "--gui" in sys.argv:
        launch_gui()
    else:
        import cli
        cli.main()