"""StudySphere - terminal version (mandatory part of the Rush)."""
import data_manager as dm


def ask(prompt):
    return input(prompt).strip()


def ask_number(prompt):
    while True:
        try:
            return float(ask(prompt))
        except ValueError:
            print("Please enter a number.")


def ask_choice(prompt, options):
    while True:
        text = ask(f"{prompt} ({'/'.join(options)}): ").lower()
        for option in options:
            if option.lower() == text:
                return option
        print("Invalid choice, try again.")


def pick_task(data):
    text = ask("Task ID: ")
    if not text.isdigit():
        print("The ID must be a whole number.")
        return None
    try:
        return dm.find_task(data, int(text))
    except ValueError as err:
        print(f"Error: {err}")
        return None


def print_tasks(tasks):
    if not tasks:
        print("No tasks found.")
        return
    print(f"{'ID':<4}{'Title':<28}{'Priority':<10}{'Due':<12}Status")
    for t in tasks:
        status = "Done" if t["done"] else ("OVERDUE" if dm.is_overdue(t) else "Pending")
        print(f"{t['id']:<4}{t['title'][:26]:<28}{t['priority']:<10}{t['due']:<12}{status}")


def add_task_flow(data):
    print("\n--- Add Task ---")
    title = ask("Title: ")
    desc = ask("Description (optional): ")
    due = ask("Due date (YYYY-MM-DD): ")
    priority = ask_choice("Priority", dm.PRIORITIES)
    category = ask_choice("Category", dm.CATEGORIES)
    try:
        task = dm.add_task(data, title, due, priority, category, desc)
    except ValueError as err:
        print(f"Error: {err}")
        return
    dm.save_data(data)
    print(f"Task #{task['id']} added!")


def view_tasks_flow(data):
    status = ask_choice("Show", ["all", "pending", "completed", "overdue"])
    by = ask_choice("Sort by", ["due", "priority"])
    print_tasks(dm.sorted_tasks(data, by, status))


def complete_task_flow(data):
    task = pick_task(data)
    if task is None:
        return
    try:
        dm.complete_task(data, task["id"])
    except ValueError as err:
        print(f"Error: {err}")
        return
    dm.save_data(data)
    print("Nice work! Task completed.")


def delete_task_flow(data):
    task = pick_task(data)
    if task is None:
        return
    if ask(f"Delete '{task['title']}'? (y/n): ").lower() == "y":
        dm.delete_task(data, task["id"])
        dm.save_data(data)
        print("Task deleted.")
    else:
        print("Cancelled.")


def session_flow(data):
    print("\n--- Log Study Session ---")
    subject = ask("Subject: ")
    hours = ask_number("Hours studied: ")
    note = ask("Note (optional): ")
    try:
        dm.add_session(data, subject, hours, note)
    except ValueError as err:
        print(f"Error: {err}")
        return
    dm.save_data(data)
    print("Session saved!")


def expense_flow(data):
    print("\n--- Add Expense ---")
    category = ask_choice("Category", dm.EXPENSE_CATS)
    amount = ask_number("Amount (LKR): ")
    note = ask("Note (optional): ")
    try:
        dm.add_expense(data, category, amount, note)
    except ValueError as err:
        print(f"Error: {err}")
        return
    dm.save_data(data)
    print("Expense saved!")


def search_flow(data):
    text = ask("Search for: ")
    if not text:
        print("Please type something to search.")
        return
    found = dm.search_tasks(data, text)
    print(f"Matching tasks: {len(found)}")
    print_tasks(found)


def dashboard_flow(data):
    pending = dm.sorted_tasks(data, "due", "pending")
    overdue = dm.sorted_tasks(data, "due", "overdue")
    spent = dm.month_expenses(data)
    print("\n========== DASHBOARD ==========")
    print(f"Pending tasks : {len(pending)} ({len(overdue)} overdue)")
    print(f"Study hours   : {dm.study_hours_week(data):.1f} h this week")
    print(f"Spent         : LKR {spent:,.0f} / {data['budget']:,.0f}")
    top = dm.top_subject(data)
    print(f"Top subject   : {top if top else 'no sessions yet'}")
    print("\nHours by subject:")
    for subject, hours in dm.hours_by_subject(data).items():
        print(f"  {subject:<15}{'#' * int(hours * 2)} {hours:g} h")
    print("\nSpending by category:")
    for cat, amount in dm.expense_by_category(data).items():
        print(f"  {cat:<15}LKR {amount:,.0f}")


def print_menu():
    print("\n===== STUDYSPHERE - Plan. Study. Achieve. =====")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Mark Task as Done")
    print("4. Delete Task")
    print("5. Log Study Session")
    print("6. Add Expense")
    print("7. Dashboard & Reports")
    print("8. Search Tasks")
    print("0. Exit")


def main():
    data = dm.load_data()
    try:
        while True:
            print_menu()
            choice = ask("Choose: ")
            if choice == "1":
                add_task_flow(data)
            elif choice == "2":
                view_tasks_flow(data)
            elif choice == "3":
                complete_task_flow(data)
            elif choice == "4":
                delete_task_flow(data)
            elif choice == "5":
                session_flow(data)
            elif choice == "6":
                expense_flow(data)
            elif choice == "7":
                dashboard_flow(data)
            elif choice == "8":
                search_flow(data)
            elif choice == "0":
                print("Goodbye! Keep showing up.")
                break
            else:
                print("Invalid choice, please enter a number from 0 to 8.")
    except (KeyboardInterrupt, EOFError):
        print("\nBye!")
    dm.save_data(data)


if __name__ == "__main__":
    main()
