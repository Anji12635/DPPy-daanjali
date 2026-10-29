"""CyberGuard - terminal incident tracker (Rush00)."""

import csv
import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "incidents.json"

SEVERITIES = ["Low", "Medium", "High", "Critical"]
STATUSES = ["Open", "Investigating", "Contained", "Resolved"]
TYPES = ["Phishing", "Malware", "Brute Force", "Suspicious Login",
         "Data Breach", "Data Exfiltration", "Unauthorized Access", "Other"]

# Dictionaries used for the risk-score algorithm
BASE_RISK = {"Low": 15, "Medium": 35, "High": 60, "Critical": 80}
TYPE_RISK = {"Phishing": 10, "Malware": 15, "Brute Force": 12,
             "Suspicious Login": 10, "Data Breach": 20,
             "Data Exfiltration": 18}

DEMO_DATA = [
    {"id": 1024, "title": "Suspicious login detected", "type": "Suspicious Login",
     "severity": "High", "status": "Investigating", "source": "192.168.1.45",
     "created": "Oct 28, 21:32", "notes": "Multiple login attempts"},
    {"id": 1023, "title": "Malware attachment flagged", "type": "Malware",
     "severity": "High", "status": "Open", "source": "203.0.113.24",
     "created": "Oct 28, 18:17", "notes": "Suspicious executable attachment"},
    {"id": 1022, "title": "Repeated failed login attempts", "type": "Brute Force",
     "severity": "Medium", "status": "Contained", "source": "185.199.110.23",
     "created": "Oct 28, 16:03", "notes": "Repeated authentication failures"},
    {"id": 1021, "title": "Urgent account verification email", "type": "Phishing",
     "severity": "Medium", "status": "Open", "source": "10.0.0.12",
     "created": "Oct 28, 14:27", "notes": "Suspicious email link"},
    {"id": 1020, "title": "Unusual data transfer", "type": "Data Exfiltration",
     "severity": "Low", "status": "Resolved", "source": "172.16.5.8",
     "created": "Oct 28, 11:05", "notes": "Unexpected outbound traffic"},
]


# ---------------------------------------------------------------
# DATA FUNCTIONS
# ---------------------------------------------------------------

def load_incidents():
    """Load incidents from JSON; fall back to demo data."""
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except (OSError, ValueError):
        pass
    return [dict(item) for item in DEMO_DATA]


def save_incidents(incidents):
    try:
        DATA_FILE.write_text(json.dumps(incidents, indent=2), encoding="utf-8")
    except OSError as error:
        print(f"  ! Could not save data: {error}")


def risk_score(incident):
    """Return a 0-100 educational risk score."""
    score = BASE_RISK.get(incident.get("severity"), 15)
    score += TYPE_RISK.get(incident.get("type"), 5)
    if incident.get("notes"):
        score += 5
    return min(100, score)


def find_by_id(incidents, incident_id):
    """Return the incident with this id, or None if it does not exist."""
    for incident in incidents:
        if incident.get("id") == incident_id:
            return incident
    return None


def next_id(incidents):
    highest = 1000
    for incident in incidents:
        if incident.get("id", 0) > highest:
            highest = incident["id"]
    return highest + 1


# ---------------------------------------------------------------
# INPUT HELPERS (validation)
# ---------------------------------------------------------------

def read_int(prompt, low, high):
    """Keep asking until the user types an integer between low and high."""
    while True:
        text = input(prompt).strip()
        try:
            value = int(text)
        except ValueError:
            print("  ! Please enter a whole number.")
            continue
        if value < low or value > high:
            print(f"  ! Number must be between {low} and {high}.")
        else:
            return value


def read_choice(title, options):
    """Show a numbered list and return the chosen option."""
    print(title)
    for number, option in enumerate(options, start=1):
        print(f"   {number}. {option}")
    return options[read_int("  Choose: ", 1, len(options)) - 1]


def valid_ip(text):
    parts = text.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit() or int(part) > 255:
            return False
    return True


def print_table(records):
    if not records:
        print("  (no incidents to show)")
        return
    print(f"  {'ID':<6}{'Created':<16}{'Title':<34}{'Type':<19}"
          f"{'Severity':<10}{'Status':<14}{'Source IP':<17}{'Risk':>4}")
    print("  " + "-" * 121)
    for item in records:
        print(f"  {item['id']:<6}{item['created']:<16}{item['title'][:32]:<34}"
              f"{item['type']:<19}{item['severity']:<10}{item['status']:<14}"
              f"{item['source']:<17}{risk_score(item):>4}")


# ---------------------------------------------------------------
# MENU ACTIONS
# ---------------------------------------------------------------

def add_incident(incidents):
    print("\n--- Register incident ---")
    title = input("  Title: ").strip()
    if title == "":                                           # rule 1
        print("  ! Title cannot be empty.")
        return

    kind = read_choice("  Incident type:", TYPES)
    severity = read_choice("  Severity:", SEVERITIES)

    source = input("  Source IPv4 (e.g. 192.168.1.45): ").strip()
    if not valid_ip(source):                                  # rule 2
        print("  ! Invalid IPv4 address. Incident not saved.")
        return

    notes = input("  Indicators / notes: ").strip()
    if severity == "Critical" and notes == "":                # rule 3
        print("  ! Critical incidents must include notes.")
        return

    for item in incidents:                                    # rule 4
        if (item["title"].lower() == title.lower()
                and item["source"] == source
                and item["status"] != "Resolved"):
            print(f"  ! Duplicate of open incident #{item['id']}. Not saved.")
            return

    new_item = {
        "id": next_id(incidents),
        "created": datetime.now().strftime("%b %d, %H:%M"),
        "title": title, "type": kind, "severity": severity,
        "status": "Open", "source": source, "notes": notes,
    }
    incidents.append(new_item)
    save_incidents(incidents)
    print(f"  Incident #{new_item['id']} registered successfully!")


def view_incidents(incidents):
    print("\n--- All incidents ---")
    if not incidents:
        print("  (no incidents recorded)")
        return
    mode = read_choice("  Sort by:", ["Newest first", "Highest risk first"])
    if mode == "Newest first":
        records = sorted(incidents, key=lambda i: i["id"], reverse=True)
    else:
        records = sorted(incidents, key=risk_score, reverse=True)
    print_table(records)


def update_status(incidents):
    print("\n--- Update incident status ---")
    incident = find_by_id(incidents, read_int("  Incident ID: ", 0, 999999))
    if incident is None:
        print("  ! No incident with that ID.")
        return

    old = incident["status"]
    print(f"  Current status: {old}")
    new = read_choice("  New status:", STATUSES)

    if STATUSES.index(new) <= STATUSES.index(old):            # rule 5
        print("  ! Status can only move forward (resolved cases stay closed).")
    elif (incident["severity"] in ("High", "Critical")
          and old == "Open" and new != "Investigating"):      # rule 6
        print("  ! High/Critical incidents must be Investigating first.")
    else:
        incident["status"] = new
        save_incidents(incidents)
        print(f"  Incident #{incident['id']}: {old} -> {new}")


def delete_incident(incidents):
    print("\n--- Delete incident ---")
    incident = find_by_id(incidents, read_int("  Incident ID: ", 0, 999999))
    if incident is None:
        print("  ! No incident with that ID.")
    elif incident["status"] != "Resolved":                    # rule 7
        print("  ! Only Resolved incidents can be deleted.")
    elif input(f"  Delete '{incident['title']}'? (y/n): ").strip().lower() == "y":
        incidents.remove(incident)
        save_incidents(incidents)
        print("  Incident deleted.")
    else:
        print("  Cancelled.")


def search_incidents(incidents):
    """Data processing #1: keyword + severity search."""
    print("\n--- Search incidents ---")
    keyword = input("  Keyword / IP (Enter for all): ").strip().lower()
    level = read_choice("  Severity filter:", ["Any"] + SEVERITIES)

    matches = []
    for item in incidents:
        text = " ".join(str(v) for v in item.values()).lower()
        if keyword in text and (level == "Any" or item["severity"] == level):
            matches.append(item)

    print(f"\n  Matching records: {len(matches)}")
    print_table(matches)


def show_summary(incidents):
    """Data processing #2: counts, average and maximum risk."""
    print("\n--- Summary ---")
    if not incidents:
        print("  No data to summarise.")
        return

    counts = {level: 0 for level in SEVERITIES}               # dictionary
    status_counts = {state: 0 for state in STATUSES}
    total_risk = 0
    top = incidents[0]
    for item in incidents:
        counts[item["severity"]] += 1
        status_counts[item["status"]] += 1
        total_risk += risk_score(item)
        if risk_score(item) > risk_score(top):
            top = item

    print(f"  Total incidents : {len(incidents)}")
    for level in SEVERITIES:
        print(f"  {level:<9}: {'#' * counts[level]} {counts[level]}")
    for state in STATUSES:
        print(f"  {state:<13}: {status_counts[state]}")
    print(f"  Average risk    : {total_risk / len(incidents):.1f}")
    print(f"  Highest risk    : #{top['id']} {top['title']} ({risk_score(top)})")


def export_csv(incidents):
    path = Path(__file__).resolve().parent / "incidents_export.csv"
    fields = ["id", "created", "title", "type", "severity",
              "status", "source", "notes"]
    try:
        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            for item in incidents:
                writer.writerow({key: item.get(key, "") for key in fields})
        print(f"  Exported to {path.name}")
    except OSError as error:
        print(f"  ! Export failed: {error}")


def open_dashboard():
    """Launch the Tkinter dashboard (bonus)."""
    try:
        from main import launch_gui
        launch_gui()
    except Exception as error:
        print(f"  ! Could not open the dashboard: {error}")


# ---------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------

def main():
    incidents = load_incidents()
    save_incidents(incidents)

    while True:
        print("\n===== CYBERGUARD - INCIDENT RESPONSE =====")
        print("1. Add incident")
        print("2. View incidents")
        print("3. Update status")
        print("4. Search incidents")
        print("5. Summary & risk analysis")
        print("6. Delete incident")
        print("7. Export CSV")
        print("8. Open dashboard (GUI)")
        print("0. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            add_incident(incidents)
        elif choice == "2":
            view_incidents(incidents)
        elif choice == "3":
            update_status(incidents)
        elif choice == "4":
            search_incidents(incidents)
        elif choice == "5":
            show_summary(incidents)
        elif choice == "6":
            delete_incident(incidents)
        elif choice == "7":
            export_csv(incidents)
        elif choice == "8":
            open_dashboard()
            incidents = load_incidents()      # reload changes made in the GUI
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("  ! Invalid choice, please enter 0-8.")


if __name__ == "__main__":
    main()
