import csv
import os
from collections import defaultdict
from datetime import datetime

from src.utils import calculate_stats
from src.storage import get_data_path


def has_data():
    path = get_data_path()
    return os.path.exists(path) and os.path.getsize(path) > 0


def load_records():
    path = get_data_path()
    if not os.path.exists(path):
        return []

    with open(path, "r", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
        return rows[1:] if len(rows) > 1 else []


def save_records(records):
    path = get_data_path()
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Subject", "Status"])
        writer.writerows(records)


def no_data_message():
    print("\n⚠️ No attendance data available.")
    input("Press Enter to continue...")


def mark_attendance():
    path = get_data_path()
    exists = os.path.exists(path)

    date = input("Enter date (YYYY-MM-DD) [leave blank for today]: ").strip()
    if not date:
        date = datetime.today().strftime("%Y-%m-%d")

    subject = input("Enter subject: ").strip()
    status = input("Present or Absent (P/A): ").strip().upper()
    status = "Present" if status == "P" else "Absent"

    with open(path, "a", newline="") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["Date", "Subject", "Status"])
        writer.writerow([date, subject, status])

    print("✅ Attendance recorded.")


def subject_summary(target):
    records = load_records()
    if not records:
        return no_data_message()

    data = defaultdict(lambda: {"total": 0, "present": 0})

    for date, subject, status in records:
        data[subject]["total"] += 1
        if status == "Present":
            data[subject]["present"] += 1

    for subject, stats in data.items():
        result = calculate_stats(stats["present"], stats["total"], target)
        print(f"\n{subject}")
        print(f"Total: {stats['total']}, Present: {stats['present']}")
        print(f"Attendance: {result['percentage']:.2f}%")
        print(f"Classes needed for {target}%: {result['needed']}")


def monthly_summary(target):
    records = load_records()
    if not records:
        return no_data_message()

    month = input("Enter month (YYYY-MM): ").strip()
    data = defaultdict(lambda: {"total": 0, "present": 0})

    for date, subject, status in records:
        if date.startswith(month):
            data[subject]["total"] += 1
            if status == "Present":
                data[subject]["present"] += 1

    if not data:
        print("⚠️ No records found for this month.")
        return

    for subject, stats in data.items():
        result = calculate_stats(stats["present"], stats["total"], target)
        print(f"\n{subject} ({month})")
        print(f"Total: {stats['total']}, Present: {stats['present']}")
        print(f"Attendance: {result['percentage']:.2f}%")


def overall_summary(target):
    records = load_records()
    if not records:
        return no_data_message()

    total = len(records)
    present = sum(1 for r in records if r[2] == "Present")

    result = calculate_stats(present, total, target)

    print("\n=== OVERALL ATTENDANCE ===")
    print(f"Total classes: {total}")
    print(f"Present: {present}")
    print(f"Attendance: {result['percentage']:.2f}%")
    print(f"Classes needed for {target}%: {result['needed']}")


def date_summary():
    records = load_records()
    if not records:
        return no_data_message()

    date = input("Enter date (YYYY-MM-DD): ").strip()
    found = False

    for d, subject, status in records:
        if d == date:
            print(f"{subject}: {status}")
            found = True

    if not found:
        print("⚠️ No records found for this date.")


def delete_entry():
    records = load_records()
    if not records:
        return no_data_message()

    for i, r in enumerate(records, 1):
        print(f"{i}. {r}")

    idx = input("Enter number to delete: ").strip()
    if idx.isdigit():
        records.pop(int(idx) - 1)
        save_records(records)
        print("✅ Entry deleted.")


def modify_entry():
    records = load_records()
    if not records:
        return no_data_message()

    for i, r in enumerate(records, 1):
        print(f"{i}. {r}")

    idx = int(input("Enter number to modify: ")) - 1
    date, subject, status = records[idx]

    date = input(f"New date [{date}]: ").strip() or date
    subject = input(f"New subject [{subject}]: ").strip() or subject
    status = input(f"New status [{status}]: ").strip() or status

    records[idx] = [date, subject, status]
    save_records(records)
    print("✅ Entry modified.")


def reset_data():
    confirm = input("This will delete ALL attendance data. Continue? (y/n): ")
    if confirm.lower() == "y":
        save_records([])
        print("✅ All data reset.")
