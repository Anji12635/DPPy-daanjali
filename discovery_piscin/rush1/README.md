# StudySphere

Plan. Study. Achieve. A student life manager built for the 42 Bangkok Python Rush.

## Purpose
Manage tasks, study sessions and expenses in one place, with reports.

## Features
- Terminal menu (`main.py`): add / view / complete / delete tasks, log study sessions,
  add expenses, dashboard & reports, search.
- Lists + dictionaries for all records; validation and business rules in `data_manager.py`.
- Bonus: JSON storage (`data.json`), sorting and filters, reports, optional Tkinter GUI (`app.py`).

## Run
    python3 main.py          # terminal version
    python3 generate_images.py && python3 app.py   # GUI (needs python3-tk, Pillow optional)
