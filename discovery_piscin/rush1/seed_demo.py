"""Optional: fills data.json with demo data so the GUI looks full."""
from datetime import date, timedelta
import data_manager as dm


def day(n):
    return (date.today() + timedelta(days=n)).isoformat()


d = {"budget": 60000.0, "tasks": [], "sessions": [], "expenses": []}
for i, (title, due, pri, cat) in enumerate([
        ("Finish AI project report", 1, "High", "Project"),
        ("Math assignment", 2, "High", "Assignment"),
        ("Read chapter 6 (Robotics)", 3, "Medium", "Personal"),
        ("Gym / Dance practice", 3, "Low", "Personal"),
        ("English essay", 7, "Medium", "Assignment"),
        ("Physics lab report", 5, "Medium", "Assignment")], start=1):
    d["tasks"].append({"id": i, "title": title, "desc": "", "due": day(due),
                       "priority": pri, "category": cat, "done": False})
for i, (subj, h) in enumerate([("AI Project", 2), ("Math", 1.5), ("Robotics", 1.25)], start=1):
    d["sessions"].append({"id": i, "subject": subj, "hours": h, "note": "", "date": day(-(i - 1))})
for i, (cat, amt) in enumerate([("Food", 12000), ("Transport", 5000), ("Books", 8500),
                                ("Others", 13000)], start=1):
    d["expenses"].append({"id": i, "category": cat, "amount": amt, "note": "", "date": day(0)})
dm.save_data(d)
print("Demo data written.")
