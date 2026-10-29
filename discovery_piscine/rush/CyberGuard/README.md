
# CyberGuard — Threat Intelligence & Incident Response Simulator

## Purpose
CyberGuard is an educational cybersecurity application that helps
users record, assess, and manage simulated security incidents.

## Target Users
- Cybersecurity and IT students
- Beginners learning incident response
- Educators demonstrating incident management
- Small teams practising incident documentation

## Value Proposition
CyberGuard provides a simple interface for recording incidents,
calculating educational risk scores, tracking status, and reviewing
incident statistics without requiring enterprise security software.

## Features
- Graphical dashboard built with Python and Tkinter
- Create, view, search, update, and delete incidents
- Rule-based risk scoring
- Severity and status tracking
- Incident analytics
- Local JSON data storage
- Command-line interface

## Requirements
- Python 3
- Tkinter for the graphical interface

## Run the graphical application
```bash
python3 main.py
```

## Run the terminal application
```bash
python3 cli.py
```

## Data Storage
Incident records are stored locally in `incidents.json`.

## Limitations
CyberGuard is an educational simulator. It does not scan live networks
or automatically detect real cyberattacks.
