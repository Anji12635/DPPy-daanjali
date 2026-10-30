"""StudySphere - optional Tkinter GUI.  Run: python3 app.py"""
import calendar
import os
import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox, ttk

import data_manager as dm

try:
    from PIL import Image, ImageOps, ImageTk
except ImportError:           # GUI still works without pictures
    Image = None

BASE = os.path.dirname(os.path.abspath(__file__))
USER_NAME = "Anji"
DARK = {"bg": "#0d1024", "panel": "#161a38", "card": "#1f2450", "text": "#eef0ff",
        "muted": "#9aa0c8", "accent": "#a45ef0", "accent2": "#f08ad0"}
LIGHT = {"bg": "#f3f1fb", "panel": "#ffffff", "card": "#e7e2f7", "text": "#1b1740",
         "muted": "#6a6790", "accent": "#8b45e0", "accent2": "#d0509f"}
PRI_COL = {"High": "#e63b5a", "Medium": "#e8a317", "Low": "#3dbb6b"}
PAGES = ["Home", "Tasks", "Study Sessions", "Expenses", "Calendar", "Reports"]


class StudySphere(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("StudySphere - Plan. Study. Achieve.")
        self.geometry("1200x760")
        self.minsize(1100, 700)
        self.data = dm.load_data()
        self.t = DARK
        self.page = "Home"
        self.filter = "all"
        self.cal = [date.today().year, date.today().month]
        self.imgs = {}
        icon = self.photo("icon.png", 64, 64)
        if icon:
            self.iconphoto(True, icon)
        self.build()

    # ---------- helpers ----------
    def photo(self, name, w, h):
        if Image is None:
            return None
        path = os.path.join(BASE, "images", name)
        if not os.path.exists(path):
            return None
        img = ImageOps.fit(Image.open(path).convert("RGBA"), (w, h))
        self.imgs[(name, w, h)] = ImageTk.PhotoImage(img)
        return self.imgs[(name, w, h)]

    def lbl(self, parent, text, size=10, bold=False, fg=None, bg=None, **kw):
        return tk.Label(parent, text=text, bg=bg or parent.cget("bg"),
                        fg=fg or self.t["text"],
                        font=("Helvetica", size, "bold" if bold else "normal"), **kw)

    def btn(self, parent, text, cmd, color=None):
        return tk.Button(parent, text=text, command=cmd, bg=color or self.t["accent"],
                         fg="white", activebackground=self.t["accent2"], relief="flat",
                         bd=0, padx=14, pady=6, font=("Helvetica", 10, "bold"),
                         cursor="hand2")

    def card(self, parent):
        return tk.Frame(parent, bg=self.t["card"], padx=16, pady=14)

    def header(self, title, btn_text=None, cmd=None):
        bar = tk.Frame(self.content, bg=self.t["bg"])
        bar.pack(fill="x", padx=24, pady=(22, 8))
        self.lbl(bar, title, 20, True).pack(side="left")
        if btn_text:
            self.btn(bar, btn_text, cmd).pack(side="right")

    def table(self, cols, rows, widths):
        tv = ttk.Treeview(self.content, columns=cols, show="headings", height=13)
        for c, w in zip(cols, widths):
            tv.heading(c, text=c)
            tv.column(c, width=w, anchor="w")
        for name, color in PRI_COL.items():
            tv.tag_configure(name, foreground=color)
        tv.tag_configure("Done", foreground=self.t["muted"])
        for values, tag in rows:
            tv.insert("", "end", values=values, tags=(tag,))
        tv.pack(fill="both", expand=True, padx=24, pady=8)
        return tv

    def selected_id(self, tv):
        sel = tv.selection()
        return int(tv.item(sel[0])["values"][0]) if sel else None

    def dialog(self, title, fields, submit):
        t = self.t
        win = tk.Toplevel(self)
        win.title(title)
        win.configure(bg=t["panel"])
        win.resizable(False, False)
        win.transient(self)
        self.lbl(win, title, 15, True, t["accent2"]).grid(
            row=0, column=0, columnspan=2, padx=20, pady=(16, 4), sticky="w")
        values = {}
        for i, (name, default, options) in enumerate(fields, start=1):
            self.lbl(win, name, 9, fg=t["muted"]).grid(
                row=2 * i - 1, column=0, columnspan=2, sticky="w", padx=20, pady=(8, 0))
            var = tk.StringVar(value=default)
            values[name] = var
            if options:
                w = ttk.Combobox(win, textvariable=var, values=options,
                                 state="readonly", width=36)
            else:
                w = tk.Entry(win, textvariable=var, width=39, bg=t["card"],
                             fg=t["text"], insertbackground=t["text"], relief="flat")
            w.grid(row=2 * i, column=0, columnspan=2, padx=20, ipady=4)

        def go():
            try:
                submit({k: v.get() for k, v in values.items()})
            except ValueError as err:
                messagebox.showerror("Oops", str(err), parent=win)
                return
            dm.save_data(self.data)
            win.destroy()
            self.show(self.page)

        n = 2 * len(fields) + 1
        self.btn(win, "Cancel", win.destroy, t["card"]).grid(
            row=n, column=0, padx=(20, 6), pady=16, sticky="ew")
        self.btn(win, "Save", go).grid(row=n, column=1, padx=(6, 20), pady=16, sticky="ew")
        win.grab_set()

    # ---------- layout ----------
    def build(self):
        t = self.t
        for w in self.winfo_children():
            w.destroy()
        self.configure(bg=t["bg"])
        st = ttk.Style(self)
        st.theme_use("clam")
        st.configure("Treeview", background=t["card"], fieldbackground=t["card"],
                     foreground=t["text"], rowheight=30, borderwidth=0)
        st.configure("Treeview.Heading", background=t["panel"], foreground=t["text"],
                     relief="flat", font=("Helvetica", 10, "bold"))
        st.map("Treeview", background=[("selected", t["accent"])])
        st.configure("TCombobox", fieldbackground=t["card"], background=t["panel"],
                     foreground=t["text"], arrowcolor=t["text"])
        st.map("TCombobox", fieldbackground=[("readonly", t["card"])],
               foreground=[("readonly", t["text"])])

        side = tk.Frame(self, bg=t["panel"], width=210)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        logo = self.photo("icon.png", 56, 56)
        if logo:
            tk.Label(side, image=logo, bg=t["panel"]).pack(pady=(22, 0))
        self.lbl(side, "StudySphere", 17, True, t["accent2"]).pack(pady=(4, 0))
        self.lbl(side, "Plan · Study · Achieve", 9, fg=t["muted"]).pack(pady=(0, 22))
        self.nav = {}
        for name in PAGES:
            b = tk.Button(side, text=name, anchor="w", relief="flat", bd=0, padx=20,
                          pady=10, font=("Helvetica", 11), cursor="hand2",
                          command=lambda n=name: self.show(n))
            b.pack(fill="x", padx=12, pady=2)
            self.nav[name] = b
        self.btn(side, "Dark / Light mode", self.toggle_theme, t["card"]).pack(
            side="bottom", fill="x", padx=12, pady=16)
        self.content = tk.Frame(self, bg=t["bg"])
        self.content.pack(side="left", fill="both", expand=True)
        self.show(self.page)

    def toggle_theme(self):
        self.t = LIGHT if self.t is DARK else DARK
        self.build()

    def show(self, page):
        t = self.t
        self.page = page
        for w in self.content.winfo_children():
            w.destroy()
        for name, b in self.nav.items():
            on = name == page
            b.configure(bg=t["accent"] if on else t["panel"],
                        fg="white" if on else t["text"],
                        activebackground=t["accent2"])
        getattr(self, "page_" + page.lower().replace(" ", "_"))()

    # ---------- Home ----------
    def page_home(self):
        t, d = self.t, self.data
        banner = tk.Canvas(self.content, height=160, highlightthickness=0, bg=t["panel"])
        banner.pack(fill="x", padx=24, pady=(22, 10))
        img = self.photo("background1.jpg", 940, 160)
        if img:
            banner.create_image(0, 0, image=img, anchor="nw")
        hour = datetime.now().hour
        greet = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
        banner.create_text(26, 50, text=f"{greet}, {USER_NAME}!", anchor="w",
                           fill="white", font=("Helvetica", 24, "bold"))
        banner.create_text(26, 92, text="Small steps make big progress.", anchor="w",
                           fill="#ffd9f0", font=("Helvetica", 12))
        banner.create_text(26, 130, text="\"Discipline today, freedom tomorrow.\"",
                           anchor="w", fill="white", font=("Helvetica", 11, "italic"))

        pending = dm.sorted_tasks(d, "due", "pending")
        overdue = dm.sorted_tasks(d, "due", "overdue")
        stats = [("Pending Tasks", str(len(pending)), f"{len(overdue)} overdue"),
                 ("Study Hours", f"{dm.study_hours_week(d):.1f} h", "this week"),
                 ("Expenses", f"LKR {dm.month_expenses(d):,.0f}", "this month"),
                 ("Budget Left", f"LKR {d['budget'] - dm.month_expenses(d):,.0f}",
                  f"of {d['budget']:,.0f}")]
        row = tk.Frame(self.content, bg=t["bg"])
        row.pack(fill="x", padx=24)
        for i, (title, big, small) in enumerate(stats):
            c = self.card(row)
            c.grid(row=0, column=i, padx=(0 if i == 0 else 8, 0), sticky="ew")
            row.columnconfigure(i, weight=1)
            self.lbl(c, title, 9, fg=t["muted"]).pack(anchor="w")
            self.lbl(c, big, 18, True).pack(anchor="w")
            self.lbl(c, small, 9, fg=t["accent2"]).pack(anchor="w")

        cols = tk.Frame(self.content, bg=t["bg"])
        cols.pack(fill="both", expand=True, padx=24, pady=12)
        cols.columnconfigure((0, 1), weight=1, uniform="a")
        left, right = self.card(cols), self.card(cols)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        self.lbl(left, "Today's Tasks (by priority)", 12, True).pack(anchor="w", pady=(0, 6))
        self.lbl(right, "Upcoming Deadlines", 12, True).pack(anchor="w", pady=(0, 6))
        self.task_rows(left, dm.sorted_tasks(d, "priority", "pending")[:5])
        self.task_rows(right, pending[:5])
        if not pending:
            self.lbl(left, "No pending tasks. Add one!", 10, fg=t["muted"]).pack(anchor="w")

    def task_rows(self, parent, tasks):
        t = self.t
        for task in tasks:
            row = tk.Frame(parent, bg=t["card"])
            row.pack(fill="x", pady=3)
            tk.Button(row, text="☐", bg=t["card"], fg=t["text"], relief="flat", bd=0,
                      font=("Helvetica", 14), cursor="hand2", activebackground=t["card"],
                      command=lambda i=task["id"]: self.quick_done(i)).pack(side="left")
            self.lbl(row, task["title"][:26]).pack(side="left", padx=6)
            tk.Label(row, text=task["priority"], bg=PRI_COL[task["priority"]],
                     fg="white", font=("Helvetica", 8, "bold"), padx=6).pack(side="right")
            self.lbl(row, task["due"], 9, fg=t["muted"]).pack(side="right", padx=8)

    def quick_done(self, task_id):
        dm.complete_task(self.data, task_id)
        dm.save_data(self.data)
        self.show(self.page)

    # ---------- Tasks ----------
    def page_tasks(self):
        t = self.t
        self.header("Tasks", "+ Add Task", self.add_task_dialog)
        bar = tk.Frame(self.content, bg=t["bg"])
        bar.pack(fill="x", padx=24)
        for f in ["all", "pending", "completed", "overdue"]:
            self.btn(bar, f.capitalize(), lambda f=f: self.set_filter(f),
                     t["accent"] if f == self.filter else t["card"]).pack(side="left", padx=(0, 8))
        rows = []
        for task in dm.sorted_tasks(self.data, "due", self.filter):
            status = "Completed" if task["done"] else ("Overdue" if dm.is_overdue(task) else "Pending")
            rows.append(([task["id"], task["title"], task["priority"], task["category"],
                          task["due"], status], "Done" if task["done"] else task["priority"]))
        tv = self.table(["ID", "Title", "Priority", "Category", "Due", "Status"], rows,
                        [45, 320, 90, 120, 110, 100])
        acts = tk.Frame(self.content, bg=t["bg"])
        acts.pack(fill="x", padx=24, pady=(0, 16))
        self.btn(acts, "Mark Done", lambda: self.task_action(tv, dm.complete_task)).pack(side="left")
        self.btn(acts, "Delete", lambda: self.task_action(tv, dm.delete_task),
                 "#c93a55").pack(side="left", padx=8)

    def set_filter(self, f):
        self.filter = f
        self.show("Tasks")

    def task_action(self, tv, action):
        task_id = self.selected_id(tv)
        if task_id is None:
            messagebox.showinfo("StudySphere", "Select a task first.")
            return
        try:
            action(self.data, task_id)
        except ValueError as err:
            messagebox.showerror("Oops", str(err))
            return
        dm.save_data(self.data)
        self.show(self.page)

    def add_task_dialog(self):
        fields = [("Title", "", None), ("Description", "", None),
                  ("Due (YYYY-MM-DD)", date.today().isoformat(), None),
                  ("Priority", "Medium", dm.PRIORITIES),
                  ("Category", "Assignment", dm.CATEGORIES)]
        self.dialog("Add Task", fields, lambda v: dm.add_task(
            self.data, v["Title"], v["Due (YYYY-MM-DD)"], v["Priority"],
            v["Category"], v["Description"]))

    # ---------- Study sessions ----------
    def page_study_sessions(self):
        t, d = self.t, self.data
        self.header("Study Sessions", "+ Add Session", self.add_session_dialog)
        c = self.card(self.content)
        c.pack(fill="x", padx=24)
        today = dm.hours_on(d, date.today().isoformat())
        self.lbl(c, f"{today:g} h today", 22, True, t["accent2"]).pack(side="left")
        self.lbl(c, f"   {dm.study_hours_week(d):g} h this week   |   top subject: "
                 f"{dm.top_subject(d) or '-'}", 11, fg=t["muted"]).pack(side="left")
        rows = [([s["id"], s["date"], s["subject"], f"{s['hours']:g} h", s["note"]], "row")
                for s in sorted(d["sessions"], key=lambda s: (s["date"], s["id"]), reverse=True)]
        self.table(["ID", "Date", "Subject", "Hours", "Note"], rows, [45, 110, 200, 80, 320])

    def add_session_dialog(self):
        fields = [("Subject", "", None), ("Hours", "1", None), ("Note", "", None)]
        self.dialog("Add Study Session", fields, lambda v: dm.add_session(
            self.data, v["Subject"], v["Hours"], v["Note"]))

    # ---------- Expenses ----------
    def page_expenses(self):
        t, d = self.t, self.data
        self.header("Expense Tracker", "+ Add Expense", self.add_expense_dialog)
        spent, budget = dm.month_expenses(d), d["budget"]
        c = self.card(self.content)
        c.pack(fill="x", padx=24)
        self.lbl(c, f"LKR {spent:,.0f}", 22, True).pack(side="left")
        self.lbl(c, f" / LKR {budget:,.0f} this month", 11, fg=t["muted"]).pack(side="left")
        bar = tk.Canvas(self.content, width=900, height=14, bg=t["panel"], highlightthickness=0)
        bar.pack(padx=24, pady=8, anchor="w")
        bar.create_rectangle(0, 0, 900 * min(spent / budget, 1) if budget else 0, 14,
                             fill=t["accent"], outline="")
        rows = [([e["id"], e["date"], e["category"], f"LKR {e['amount']:,.0f}", e["note"]], "row")
                for e in sorted(d["expenses"], key=lambda e: (e["date"], e["id"]), reverse=True)]
        self.table(["ID", "Date", "Category", "Amount", "Note"], rows, [45, 110, 150, 130, 300])

    def add_expense_dialog(self):
        fields = [("Category", "Food", dm.EXPENSE_CATS), ("Amount", "", None), ("Note", "", None)]
        self.dialog("Add Expense", fields, lambda v: dm.add_expense(
            self.data, v["Category"], v["Amount"], v["Note"]))

    # ---------- Calendar ----------
    def page_calendar(self):
        t = self.t
        y, m = self.cal
        self.header("Calendar")
        nav = tk.Frame(self.content, bg=t["bg"])
        nav.pack(padx=24, anchor="w")
        self.btn(nav, "<", lambda: self.move_month(-1), t["card"]).pack(side="left")
        self.lbl(nav, f"  {calendar.month_name[m]} {y}  ", 14, True).pack(side="left")
        self.btn(nav, ">", lambda: self.move_month(1), t["card"]).pack(side="left")
        grid = tk.Frame(self.content, bg=t["bg"])
        grid.pack(padx=24, pady=10, anchor="w")
        for i, name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            self.lbl(grid, name, 9, fg=t["muted"]).grid(row=0, column=i, padx=4)
        due_days = {task["due"] for task in self.data["tasks"] if not task["done"]}
        for r, week in enumerate(calendar.monthcalendar(y, m), start=1):
            for c, day in enumerate(week):
                if day == 0:
                    continue
                iso = date(y, m, day).isoformat()
                color = t["card"]
                if iso in due_days:
                    color = "#7a3fc0"
                if iso == date.today().isoformat():
                    color = t["accent"]
                tk.Button(grid, text=str(day), width=6, height=2, bg=color,
                          fg="white" if color != t["card"] else t["text"],
                          relief="flat", bd=0, command=lambda i=iso: self.day_info(i)
                          ).grid(row=r, column=c, padx=3, pady=3)
        self.info = self.lbl(self.content, "Click a day to see its deadlines.", 11,
                             fg=t["muted"], justify="left")
        self.info.pack(padx=24, anchor="w")

    def move_month(self, step):
        y, m = self.cal
        m += step
        if m == 0:
            y, m = y - 1, 12
        elif m == 13:
            y, m = y + 1, 1
        self.cal = [y, m]
        self.show("Calendar")

    def day_info(self, iso):
        tasks = [t for t in self.data["tasks"] if t["due"] == iso]
        text = iso + "\n" + ("\n".join(f" - {t['title']} ({t['priority']})" for t in tasks)
                             if tasks else " nothing due")
        self.info.configure(text=text, fg=self.t["text"])

    # ---------- Reports ----------
    def bars(self, parent, labels, values, w=380, h=200):
        t = self.t
        cv = tk.Canvas(parent, width=w, height=h, bg=t["card"], highlightthickness=0)
        if not values:
            cv.create_text(w / 2, h / 2, text="No data yet", fill=t["muted"])
            return cv
        top = max(values + [1])
        bw = w / len(values)
        for i, (name, v) in enumerate(zip(labels, values)):
            x0, x1 = i * bw + 10, (i + 1) * bw - 10
            y1 = h - 24
            y0 = y1 - (h - 56) * v / top
            cv.create_rectangle(x0, y0, x1, y1, fill=t["accent"], outline="")
            cv.create_text((x0 + x1) / 2, h - 10, text=name[:7], fill=t["muted"], font=("Helvetica", 8))
            cv.create_text((x0 + x1) / 2, y0 - 9, text=f"{v:g}", fill=t["text"], font=("Helvetica", 8))
        return cv

    def page_reports(self):
        t, d = self.t, self.data
        self.header("Reports & Analytics")
        grid = tk.Frame(self.content, bg=t["bg"])
        grid.pack(padx=24, pady=6, anchor="w")
        subj = dm.hours_by_subject(d)
        exp = dm.expense_by_category(d)
        charts = [("Study hours this week", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                   dm.daily_hours_week(d)),
                  ("Hours by subject", list(subj), [round(v, 1) for v in subj.values()]),
                  ("Spending by category (LKR)", list(exp), [round(v) for v in exp.values()])]
        for i, (title, names, vals) in enumerate(charts):
            c = self.card(grid)
            c.grid(row=i // 2, column=i % 2, padx=6, pady=6)
            self.lbl(c, title, 11, True).pack(anchor="w")
            self.bars(c, names, vals).pack()
        done = len(dm.sorted_tasks(d, "due", "completed"))
        total = len(d["tasks"])
        c = self.card(grid)
        c.grid(row=1, column=1, padx=6, pady=6, sticky="nsew")
        self.lbl(c, "Productivity", 11, True).pack(anchor="w")
        self.lbl(c, f"{done}/{total} tasks completed", 20, True, t["accent2"]).pack(pady=30)


if __name__ == "__main__":
    StudySphere().mainloop()
