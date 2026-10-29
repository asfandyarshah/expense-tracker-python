"""
Personal Expense Tracker
Author: Syed Asfandyar Shah

A command-line app to record income and expenses, group them by category,
and print monthly summaries. Data is saved to expenses.json so it is still
there the next time the program runs.

Run:  python expense_tracker.py
"""

import json
import os
from collections import defaultdict
from datetime import datetime

DATA_FILE = "expenses.json"
DATE_FORMAT = "%Y-%m-%d"

EXPENSE_CATEGORIES = [
    "Food", "Transport", "Education", "Entertainment",
    "Health", "Bills", "Shopping", "Other",
]
INCOME_CATEGORIES = ["Allowance", "Salary", "Freelance", "Gift", "Other"]


# ---------- File handling ----------

def load_records():
    """Read all saved records. Returns an empty list if no file exists yet."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print("Warning: could not read the data file. Starting with an empty list.")
        return []


def save_records(records):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


# ---------- Input helpers (validation) ----------

def ask_amount(prompt):
    """Keep asking until the user enters a positive number."""
    while True:
        text = input(prompt).strip().replace(",", "")
        try:
            value = float(text)
            if value <= 0:
                print("  Amount must be greater than zero.")
                continue
            return round(value, 2)
        except ValueError:
            print("  Please enter a valid number, e.g. 1500 or 249.50")


def ask_date(prompt):
    """Ask for a date in YYYY-MM-DD format. Pressing Enter uses today."""
    while True:
        text = input(prompt + " (YYYY-MM-DD, Enter for today): ").strip()
        if not text:
            return datetime.today().strftime(DATE_FORMAT)
        try:
            return datetime.strptime(text, DATE_FORMAT).strftime(DATE_FORMAT)
        except ValueError:
            print("  Invalid date. Example: 2026-10-29")


def ask_category(options):
    print("Categories:")
    for i, name in enumerate(options, start=1):
        print(f"  {i}. {name}")
    while True:
        choice = input("Choose a category number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print("  Please pick a number from the list.")


# ---------- Core features ----------

def add_record(records, kind):
    """Add an 'income' or 'expense' record."""
    options = INCOME_CATEGORIES if kind == "income" else EXPENSE_CATEGORIES
    print(f"\n--- Add {kind} ---")
    amount = ask_amount("Amount: ")
    category = ask_category(options)
    date = ask_date("Date")
    note = input("Note (optional): ").strip()

    next_id = max((r["id"] for r in records), default=0) + 1
    records.append({
        "id": next_id, "type": kind, "amount": amount,
        "category": category, "date": date, "note": note,
    })
    save_records(records)
    print(f"Saved {kind} of {amount:,.2f} under {category}.")


def view_records(records):
    if not records:
        print("\nNo records yet.")
        return
    print(f"\n{'ID':<4} {'Date':<11} {'Type':<8} {'Category':<14} {'Amount':>10}  Note")
    print("-" * 70)
    for r in sorted(records, key=lambda r: r["date"]):
        print(f"{r['id']:<4} {r['date']:<11} {r['type']:<8} {r['category']:<14} "
              f"{r['amount']:>10,.2f}  {r['note']}")


def monthly_summary(records):
    """Totals for one month, plus spending broken down by category."""
    month = input("\nMonth to summarise (YYYY-MM, Enter for this month): ").strip()
    if not month:
        month = datetime.today().strftime("%Y-%m")
    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        print("Invalid month. Example: 2026-10")
        return

    in_month = [r for r in records if r["date"].startswith(month)]
    if not in_month:
        print(f"No records found for {month}.")
        return

    income = sum(r["amount"] for r in in_month if r["type"] == "income")
    expenses = sum(r["amount"] for r in in_month if r["type"] == "expense")
    by_category = defaultdict(float)
    for r in in_month:
        if r["type"] == "expense":
            by_category[r["category"]] += r["amount"]

    print(f"\n===== Summary for {month} =====")
    print(f"Total income:   {income:>12,.2f}")
    print(f"Total expenses: {expenses:>12,.2f}")
    print(f"Net savings:    {income - expenses:>12,.2f}")

    if by_category:
        print("\nSpending by category:")
        for cat, total in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
            share = total / expenses * 100
            bar = "#" * int(share // 5)
            print(f"  {cat:<14} {total:>10,.2f}  {share:5.1f}%  {bar}")
        top = max(by_category, key=by_category.get)
        print(f"\nBiggest spending category: {top}")


def delete_record(records):
    view_records(records)
    if not records:
        return
    choice = input("\nEnter the ID to delete (or press Enter to cancel): ").strip()
    if not choice.isdigit():
        print("Cancelled.")
        return
    target = int(choice)
    remaining = [r for r in records if r["id"] != target]
    if len(remaining) == len(records):
        print("No record with that ID.")
        return
    records[:] = remaining
    save_records(records)
    print("Record deleted.")


# ---------- Main menu ----------

MENU = """
========= EXPENSE TRACKER =========
1. Add expense
2. Add income
3. View all records
4. Monthly summary
5. Delete a record
6. Exit
"""


def main():
    records = load_records()
    while True:
        print(MENU)
        choice = input("Choose an option (1-6): ").strip()
        if choice == "1":
            add_record(records, "expense")
        elif choice == "2":
            add_record(records, "income")
        elif choice == "3":
            view_records(records)
        elif choice == "4":
            monthly_summary(records)
        elif choice == "5":
            delete_record(records)
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please enter a number from 1 to 6.")


if __name__ == "__main__":
    main()
