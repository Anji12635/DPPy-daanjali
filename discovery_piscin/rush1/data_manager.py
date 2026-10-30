"""Data layer for StudySphere: JSON storage + all business rules."""
import json
import os
from datetime import date, datetime, timedelta

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
PRIORITIES = ["High", "Medium", "Low"]
CATEGORIES = ["Assignment", "Exam", "Project", "Personal", "Other"]
EXPENSE_CATS = ["Food", "Transport", "Books", "Others"]


def load_data():
    data = {"tasks": [], "sessions": [], "expenses": [], "budget": 60000.0}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data.update(json.load(f))
    except (FileNotFoundError, ValueError, OSError):
        pass
    return data


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def parse_date(text):
    text = str(text).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise ValueError("Date must look like 2026-11-05 or 05/11/2026.")


def match_option(value, options, label):
    for option in options:
        if option.lower() == str(value).strip().lower():
            return option
    raise ValueError(f"{label} must be one of: {', '.join(options)}.")


def next_id(records):
    return max((r["id"] for r in records), default=0) + 1


# ---------------- tasks ----------------
def add_task(data, title, due, priority, category, desc=""):
    title = title.strip()
    if not title:
        raise ValueError("Title cannot be empty.")
    due_date = parse_date(due)
    if due_date < date.today():                       # rule 1
        raise ValueError("Due date cannot be in the past.")
    priority = match_option(priority, PRIORITIES, "Priority")
    category = match_option(category, CATEGORIES, "Category")
    for t in data["tasks"]:                           # rule 2
        if (t["title"].lower() == title.lower() and t["due"] == due_date.isoformat()
                and not t["done"]):
            raise ValueError("This task already exists for that date.")
    task = {"id": next_id(data["tasks"]), "title": title, "desc": desc.strip(),
            "due": due_date.isoformat(), "priority": priority,
            "category": category, "done": False}
    data["tasks"].append(task)
    return task


def find_task(data, task_id):
    for t in data["tasks"]:
        if t["id"] == task_id:
            return t
    raise ValueError(f"No task with ID {task_id}.")


def complete_task(data, task_id):
    task = find_task(data, task_id)
    if task["done"]:
        raise ValueError("That task is already completed.")
    task["done"] = True
    return task


def delete_task(data, task_id):
    data["tasks"].remove(find_task(data, task_id))


def is_overdue(task):
    return (not task["done"]) and task["due"] < date.today().isoformat()


def sorted_tasks(data, by="due", status="all"):
    chosen = []
    for t in data["tasks"]:
        if status == "pending" and t["done"]:
            continue
        if status == "completed" and not t["done"]:
            continue
        if status == "overdue" and not is_overdue(t):
            continue
        chosen.append(t)
    if by == "priority":
        chosen.sort(key=lambda t: (PRIORITIES.index(t["priority"]), t["due"]))
    else:
        chosen.sort(key=lambda t: (t["due"], PRIORITIES.index(t["priority"])))
    return chosen


def search_tasks(data, text):
    text = text.strip().lower()
    return [t for t in data["tasks"]
            if text in t["title"].lower() or text in t["desc"].lower()
            or text in t["category"].lower()]


# ---------------- study sessions ----------------
def hours_on(data, iso_day):
    return sum(s["hours"] for s in data["sessions"] if s["date"] == iso_day)


def add_session(data, subject, hours, note=""):
    subject = subject.strip()
    if not subject:
        raise ValueError("Subject cannot be empty.")
    try:
        hours = float(hours)
    except (TypeError, ValueError):
        raise ValueError("Hours must be a number.")
    if hours <= 0 or hours > 12:                      # rule 3
        raise ValueError("Hours must be between 0 and 12.")
    today = date.today().isoformat()
    if hours_on(data, today) + hours > 16:            # rule 4
        raise ValueError("You cannot log more than 16 study hours in one day.")
    session = {"id": next_id(data["sessions"]), "subject": subject,
               "hours": hours, "note": note.strip(), "date": today}
    data["sessions"].append(session)
    return session


# ---------------- expenses ----------------
def month_expenses(data):
    prefix = date.today().strftime("%Y-%m")
    return sum(e["amount"] for e in data["expenses"] if e["date"].startswith(prefix))


def add_expense(data, category, amount, note=""):
    category = match_option(category, EXPENSE_CATS, "Category")
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        raise ValueError("Amount must be a number.")
    if amount <= 0:
        raise ValueError("Amount must be greater than 0.")
    left = data["budget"] - month_expenses(data)
    if amount > left:                                 # rule 5 (insufficient budget)
        raise ValueError(f"Budget exceeded! Only LKR {left:,.0f} left this month.")
    expense = {"id": next_id(data["expenses"]), "category": category,
               "amount": amount, "note": note.strip(),
               "date": date.today().isoformat()}
    data["expenses"].append(expense)
    return expense


# ---------------- statistics (data processing) ----------------
def daily_hours_week(data):
    start = date.today() - timedelta(days=date.today().weekday())
    return [round(hours_on(data, (start + timedelta(days=i)).isoformat()), 2)
            for i in range(7)]


def study_hours_week(data):
    return sum(daily_hours_week(data))


def hours_by_subject(data):
    totals = {}
    for s in data["sessions"]:
        totals[s["subject"]] = totals.get(s["subject"], 0) + s["hours"]
    return totals


def expense_by_category(data):
    totals = {}
    for e in data["expenses"]:
        totals[e["category"]] = totals.get(e["category"], 0) + e["amount"]
    return totals


def top_subject(data):
    totals = hours_by_subject(data)
    return max(totals, key=totals.get) if totals else None
