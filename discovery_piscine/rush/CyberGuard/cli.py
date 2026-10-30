"""CyberGuard - terminal incident tracker (Rush00)."""

# Import csv to export incident records into a CSV file.
import csv

# Import json to store and retrieve incident information.
import json

# Import datetime to record when an incident is created.
from datetime import datetime

# Import Path to work with file and folder paths.
from pathlib import Path


# ---------------------------------------------------------------
# CONSTANTS AND CONFIGURATION
# ---------------------------------------------------------------

# Get the directory where this Python file is located.
# The incident data will be stored in incidents.json in this folder.
DATA_FILE = Path(__file__).resolve().parent / "incidents.json"

# Lists containing the available choices in the application.
# These lists are used when registering or updating incidents.
SEVERITIES = ["Low", "Medium", "High", "Critical"]
STATUSES = ["Open", "Investigating", "Contained", "Resolved"]
TYPES = ["Phishing", "Malware", "Brute Force", "Suspicious Login",
         "Data Breach", "Data Exfiltration", "Unauthorized Access", "Other"]


# ---------------------------------------------------------------
# RISK SCORE CONFIGURATION
# ---------------------------------------------------------------

# Dictionaries used by the risk-score algorithm.
# Each severity has a starting risk value.
BASE_RISK = {"Low": 15, "Medium": 35, "High": 60, "Critical": 80}

# Each incident type adds an additional risk value.
TYPE_RISK = {"Phishing": 10, "Malware": 15, "Brute Force": 12,
             "Suspicious Login": 10, "Data Breach": 20,
             "Data Exfiltration": 18}


# ---------------------------------------------------------------
# DEMO INCIDENT DATA
# ---------------------------------------------------------------

# Sample incidents displayed when no valid JSON data file exists.
# Each incident is represented by a dictionary.
# A list of dictionaries allows us to store multiple incidents.
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

    # Try to read the existing JSON file.
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

        # Make sure the loaded data is a list.
        if isinstance(data, list):
            return data

    # Handle missing files or invalid JSON without crashing.
    except (OSError, ValueError):
        pass

    # Return a copy of the demo data if loading fails.
    return [dict(item) for item in DEMO_DATA]


def save_incidents(incidents):
    # Convert the incident list into JSON and save it.
    # indent=2 makes the JSON file easier to read.
    try:
        DATA_FILE.write_text(
            json.dumps(incidents, indent=2),
            encoding="utf-8"
        )

    # Display an error if the file cannot be saved.
    except OSError as error:
        print(f"  ! Could not save data: {error}")


def risk_score(incident):
    """Return a 0-100 educational risk score."""

    # Get the starting risk based on severity.
    # If severity is not found, use 15 as the default.
    score = BASE_RISK.get(incident.get("severity"), 15)

    # Add extra risk based on the incident type.
    score += TYPE_RISK.get(incident.get("type"), 5)

    # Add 5 points if additional notes are available.
    if incident.get("notes"):
        score += 5

    # The final risk score cannot exceed 100.
    return min(100, score)


def find_by_id(incidents, incident_id):
    """Return the incident with this id, or None if it does not exist."""

    # Loop through every incident in the list.
    for incident in incidents:

        # Compare the incident ID with the requested ID.
        if incident.get("id") == incident_id:
            return incident

    # Return None if no matching incident is found.
    return None


def next_id(incidents):
    # Start with 1000 as the minimum ID.
    highest = 1000

    # Find the highest existing incident ID.
    for incident in incidents:
        if incident.get("id", 0) > highest:
            highest = incident["id"]

    # Generate the next ID by adding 1.
    return highest + 1


# ---------------------------------------------------------------
# INPUT HELPERS (VALIDATION)
# ---------------------------------------------------------------

def read_int(prompt, low, high):
    """Keep asking until the user types an integer between low and high."""

    while True:
        # Read the user's input and remove extra spaces.
        text = input(prompt).strip()

        # Try converting the input into an integer.
        try:
            value = int(text)

        # Handle input that is not a valid integer.
        except ValueError:
            print("  ! Please enter a whole number.")
            continue

        # Check whether the number is within the allowed range.
        if value < low or value > high:
            print(f"  ! Number must be between {low} and {high}.")

        # Return the valid number.
        else:
            return value


def read_choice(title, options):
    """Show a numbered list and return the chosen option."""

    # Display the question or menu title.
    print(title)

    # Display each option with a number starting from 1.
    for number, option in enumerate(options, start=1):
        print(f"   {number}. {option}")

    # Read the selected number and return its matching option.
    # Subtract 1 because Python list indexes start at 0.
    return options[read_int("  Choose: ", 1, len(options)) - 1]


def valid_ip(text):
    # Split the IP address into four parts using dots.
    parts = text.split(".")

    # IPv4 addresses must contain exactly four parts.
    if len(parts) != 4:
        return False

    # Check every part of the IP address.
    for part in parts:

        # Every part must contain digits and be no greater than 255.
        if not part.isdigit() or int(part) > 255:
            return False

    # Return True if all four parts pass validation.
    return True


def print_table(records):
    # Check whether there are any records to display.
    if not records:
        print("  (no incidents to show)")
        return

    # Print the table headings with fixed column widths.
    print(f"  {'ID':<6}{'Created':<16}{'Title':<34}{'Type':<19}"
          f"{'Severity':<10}{'Status':<14}{'Source IP':<17}{'Risk':>4}")

    # Print a separator line.
    print("  " + "-" * 121)

    # Display each incident as one row in the table.
    for item in records:
        print(f"  {item['id']:<6}{item['created']:<16}{item['title'][:32]:<34}"
              f"{item['type']:<19}{item['severity']:<10}{item['status']:<14}"
              f"{item['source']:<17}{risk_score(item):>4}")


# ---------------------------------------------------------------
# MENU ACTIONS
# ---------------------------------------------------------------

def add_incident(incidents):
    """Register a new security incident."""

    print("\n--- Register incident ---")

    # Ask the user to enter an incident title.
    title = input("  Title: ").strip()

    # Rule 1: An incident cannot have an empty title.
    if title == "":
        print("  ! Title cannot be empty.")
        return

    # Ask the user to select an incident type and severity.
    kind = read_choice("  Incident type:", TYPES)
    severity = read_choice("  Severity:", SEVERITIES)

    # Ask for the source IPv4 address.
    source = input("  Source IPv4 (e.g. 192.168.1.45): ").strip()

    # Rule 2: Validate the IP address before saving.
    if not valid_ip(source):
        print("  ! Invalid IPv4 address. Incident not saved.")
        return

    # Ask for additional information about the incident.
    notes = input("  Indicators / notes: ").strip()

    # Rule 3: Critical incidents must contain notes.
    if severity == "Critical" and notes == "":
        print("  ! Critical incidents must include notes.")
        return

    # Rule 4: Prevent duplicate active incidents.
    for item in incidents:
        if (item["title"].lower() == title.lower()
                and item["source"] == source
                and item["status"] != "Resolved"):
            print(f"  ! Duplicate of open incident #{item['id']}. Not saved.")
            return

    # Create a dictionary containing the new incident information.
    new_item = {
        "id": next_id(incidents),
        "created": datetime.now().strftime("%b %d, %H:%M"),
        "title": title, "type": kind, "severity": severity,
        "status": "Open", "source": source, "notes": notes,
    }

    # Add the new dictionary to the incident list.
    incidents.append(new_item)

    # Save the updated list into the JSON file.
    save_incidents(incidents)

    print(f"  Incident #{new_item['id']} registered successfully!")


def view_incidents(incidents):
    """Display all incidents with a selected sorting method."""

    print("\n--- All incidents ---")

    if not incidents:
        print("  (no incidents recorded)")
        return

    # Allow the user to choose how incidents should be sorted.
    mode = read_choice("  Sort by:", ["Newest first", "Highest risk first"])

    # Sort by ID in descending order to show newest incidents first.
    if mode == "Newest first":
        records = sorted(incidents, key=lambda i: i["id"], reverse=True)

    # Sort by calculated risk score in descending order.
    else:
        records = sorted(incidents, key=risk_score, reverse=True)

    # Display the sorted incidents.
    print_table(records)


def update_status(incidents):
    """Change the status of an existing incident."""

    print("\n--- Update incident status ---")

    # Ask for the ID and search for the incident.
    incident = find_by_id(incidents, read_int("  Incident ID: ", 0, 999999))

    if incident is None:
        print("  ! No incident with that ID.")
        return

    # Store and display the current status.
    old = incident["status"]
    print(f"  Current status: {old}")

    # Ask the user to select the new status.
    new = read_choice("  New status:", STATUSES)

    # Rule 5: Incident statuses can only move forward.
    if STATUSES.index(new) <= STATUSES.index(old):
        print("  ! Status can only move forward (resolved cases stay closed).")

    # Rule 6: High and Critical incidents must be investigated first.
    elif (incident["severity"] in ("High", "Critical")
          and old == "Open" and new != "Investigating"):
        print("  ! High/Critical incidents must be Investigating first.")

    else:
        # Update the incident status.
        incident["status"] = new

        # Save the changes.
        save_incidents(incidents)

        print(f"  Incident #{incident['id']}: {old} -> {new}")


def delete_incident(incidents):
    """Delete an incident only when its status is Resolved."""

    print("\n--- Delete incident ---")

    # Find the incident using its ID.
    incident = find_by_id(incidents, read_int("  Incident ID: ", 0, 999999))

    if incident is None:
        print("  ! No incident with that ID.")

    # Rule 7: Only resolved incidents can be deleted.
    elif incident["status"] != "Resolved":
        print("  ! Only Resolved incidents can be deleted.")

    # Ask the user to confirm before deleting.
    elif input(f"  Delete '{incident['title']}'? (y/n): ").strip().lower() == "y":

        # Remove the incident from the list.
        incidents.remove(incident)

        # Save the updated list.
        save_incidents(incidents)

        print("  Incident deleted.")

    else:
        print("  Cancelled.")


def search_incidents(incidents):
    """Data processing #1: keyword + severity search."""

    print("\n--- Search incidents ---")

    # Ask for a keyword or IP address.
    # An empty keyword matches all incident records.
    keyword = input("  Keyword / IP (Enter for all): ").strip().lower()

    # Ask for a severity filter.
    level = read_choice("  Severity filter:", ["Any"] + SEVERITIES)

    matches = []

    # Search through all incidents.
    for item in incidents:

        # Combine all dictionary values into one searchable string.
        text = " ".join(str(v) for v in item.values()).lower()

        # Check whether both the keyword and severity match.
        if keyword in text and (level == "Any" or item["severity"] == level):
            matches.append(item)

    # Display the number of matching records.
    print(f"\n  Matching records: {len(matches)}")

    # Display the matching incidents.
    print_table(matches)


def show_summary(incidents):
    """Data processing #2: counts, average and maximum risk."""

    print("\n--- Summary ---")

    if not incidents:
        print("  No data to summarise.")
        return

    # Create dictionaries to count incidents by severity and status.
    counts = {level: 0 for level in SEVERITIES}
    status_counts = {state: 0 for state in STATUSES}

    # Initialize the total risk score.
    total_risk = 0

    # Assume the first incident has the highest risk initially.
    top = incidents[0]

    # Process every incident.
    for item in incidents:

        # Increase the count for its severity.
        counts[item["severity"]] += 1

        # Increase the count for its status.
        status_counts[item["status"]] += 1

        # Add its risk score to the total.
        total_risk += risk_score(item)

        # Check whether this incident has a higher risk score.
        if risk_score(item) > risk_score(top):
            top = item

    # Display total incidents.
    print(f"  Total incidents : {len(incidents)}")

    # Display the number of incidents for each severity.
    for level in SEVERITIES:
        print(f"  {level:<9}: {'#' * counts[level]} {counts[level]}")

    # Display the number of incidents for each status.
    for state in STATUSES:
        print(f"  {state:<13}: {status_counts[state]}")

    # Calculate and display the average risk score.
    print(f"  Average risk    : {total_risk / len(incidents):.1f}")

    # Display the incident with the highest risk.
    print(f"  Highest risk    : #{top['id']} {top['title']} ({risk_score(top)})")


def export_csv(incidents):
    """Export incident records into a CSV file."""

    # Create the CSV file path in the same directory.
    path = Path(__file__).resolve().parent / "incidents_export.csv"

    # Define which incident fields should be exported.
    fields = ["id", "created", "title", "type", "severity",
              "status", "source", "notes"]

    try:
        # Open the CSV file in write mode.
        # newline="" prevents unwanted blank lines.
        with open(path, "w", newline="", encoding="utf-8") as file:

            # DictWriter writes dictionary data into CSV columns.
            writer = csv.DictWriter(file, fieldnames=fields)

            # Write the column headings.
            writer.writeheader()

            # Write each incident as a row.
            for item in incidents:
                writer.writerow({key: item.get(key, "") for key in fields})

        print(f"  Exported to {path.name}")

    # Handle file-writing errors.
    except OSError as error:
        print(f"  ! Export failed: {error}")


def open_dashboard():
    """Launch the Tkinter dashboard (bonus)."""

    try:
        # Import the launch_gui function from main.py.
        from main import launch_gui

        # Start the graphical dashboard.
        launch_gui()

    # Display an error if the GUI cannot be opened.
    except Exception as error:
        print(f"  ! Could not open the dashboard: {error}")


# ---------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------

def main():
    """Start the CyberGuard command-line application."""

    # Load existing incidents when the application starts.
    incidents = load_incidents()

    # Save the loaded data to ensure a JSON data file exists.
    save_incidents(incidents)

    # Keep displaying the menu until the user chooses Exit.
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

        # Read the user's menu selection.
        choice = input("Choose: ").strip()

        # Call the corresponding function for each menu option.
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
            # Open the graphical dashboard.
            open_dashboard()

            # Reload incidents in case they were changed in the GUI.
            incidents = load_incidents()

        elif choice == "0":
            # End the application.
            print("Goodbye!")
            break

        else:
            # Handle invalid menu selections.
            print("  ! Invalid choice, please enter 0-8.")


# ---------------------------------------------------------------
# PROGRAM ENTRY POINT
# ---------------------------------------------------------------

# This condition checks whether this file is being run directly.
# If it is imported by another Python file, main() will not run automatically.
if __name__ == "__main__":
    main()