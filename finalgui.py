import os
import sys
import csv
import math
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from datetime import date


TARGET_PERCENT = 75


# ---------------- SAFE DATA DIRECTORY ----------------
def get_data_directory():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.join(os.getenv("APPDATA"), "AttendanceTracker")
    else:
        base_dir = os.path.join(os.getcwd(), "data")

    os.makedirs(base_dir, exist_ok=True)
    return base_dir


DATA_DIR = get_data_directory()
DATA_FILE = os.path.join(DATA_DIR, "attendance.csv")


def ensure_data_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "subject", "status"])


def read_attendance():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, newline="") as f:
        return list(csv.DictReader(f))


def write_attendance(rows):
    with open(DATA_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "subject", "status"])
        writer.writeheader()
        writer.writerows(rows)


def classes_needed(present, total):
    if total == 0:
        return 0
    if (present / total) * 100 >= TARGET_PERCENT:
        return 0
    return math.ceil((TARGET_PERCENT * total - 100 * present) / (100 - TARGET_PERCENT))


def progress_style(percent):
    if percent < 75:
        return DANGER
    elif percent <= 85:
        return WARNING
    return SUCCESS


class AttendanceApp(ttk.Window):

    def __init__(self):
        super().__init__(
            title="📘 Attendance Tracker",
            themename="flatly",
            size=(500, 720),
            resizable=(False, False)
        )

        self.is_dark = False
        self.container = ttk.Frame(self, padding=20)
        self.container.pack(fill=BOTH, expand=True)

        ensure_data_file()
        self.show_home()

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.style.theme_use("darkly" if self.is_dark else "flatly")
        self.show_home()

    def clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    # ---------------- HOME ----------------
    def show_home(self):
        self.clear()

        top = ttk.Frame(self.container)
        top.pack(fill=X)

        ttk.Button(
            top,
            text="☀️ Light" if self.is_dark else "🌙 Dark",
            bootstyle=LINK,
            command=self.toggle_theme
        ).pack(side=RIGHT)

        ttk.Label(
            self.container,
            text="📘 Attendance Tracker",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=20)

        ttk.Button(self.container, text="➕ Add Attendance",
                   width=30, bootstyle=SUCCESS,
                   command=self.show_add_attendance).pack(pady=8)

        ttk.Button(self.container, text="📊 Attendance Summary",
                   width=30, bootstyle=INFO,
                   command=self.show_summary).pack(pady=8)

        ttk.Button(self.container, text="🧺 Manage Data",
                   width=30, bootstyle=WARNING,
                   command=self.show_manage).pack(pady=8)

        ttk.Button(self.container, text="❌ Exit",
                   width=30, bootstyle=DANGER,
                   command=self.destroy).pack(pady=15)

    # ---------------- ADD ATTENDANCE ----------------
    def show_add_attendance(self):
        self.clear()

        ttk.Label(self.container, text="➕ Add Attendance",
                  font=("Segoe UI", 16, "bold")).pack(pady=15)

        ttk.Label(self.container, text="📘 Subject").pack(anchor=W)
        subject = ttk.Entry(self.container, width=30)
        subject.pack(pady=5)

        ttk.Label(self.container, text="📅 Date").pack(anchor=W)
        date_entry = ttk.Entry(self.container, width=30)
        date_entry.insert(0, date.today().isoformat())
        date_entry.pack(pady=5)

        status = tk.StringVar(value="Present")

        ttk.Radiobutton(self.container, text="Present",
                        variable=status, value="Present").pack(anchor=W)
        ttk.Radiobutton(self.container, text="Absent",
                        variable=status, value="Absent").pack(anchor=W)

        ttk.Button(
            self.container, text="💾 Save",
            bootstyle=PRIMARY,
            command=lambda: self.save_attendance(
                subject.get(), date_entry.get(), status.get())
        ).pack(pady=15)

        ttk.Button(self.container, text="⬅ Back",
                   bootstyle=SECONDARY,
                   command=self.show_home).pack()

    def save_attendance(self, subject, date_value, status):
        if not subject.strip():
            Messagebox.show_error("Subject cannot be empty")
            return

        with open(DATA_FILE, "a", newline="") as f:
            csv.writer(f).writerow([date_value, subject.strip(), status])

        Messagebox.show_info("Attendance saved successfully")
        self.show_home()

    # ---------------- SUMMARY ----------------
    def show_summary(self):
        self.clear()
        data = read_attendance()

        ttk.Label(self.container, text="📊 Attendance Summary",
                  font=("Segoe UI", 16, "bold")).pack(pady=10)

        if not data:
            ttk.Label(self.container, text="No data available").pack(pady=20)
            ttk.Button(self.container, text="⬅ Back",
                       command=self.show_home).pack()
            return

        summary = {}
        total_p = total_c = 0

        for r in data:
            summary.setdefault(r["subject"], {"P": 0, "A": 0})
            summary[r["subject"]][r["status"][0]] += 1

        for subject, c in summary.items():
            total = c["P"] + c["A"]
            percent = (c["P"] / total) * 100
            need = classes_needed(c["P"], total)

            total_p += c["P"]
            total_c += total

            ttk.Label(self.container,
                      text=f"📘 {subject} — {percent:.1f}%",
                      font=("Segoe UI", 11, "bold")).pack(anchor=W)

            ttk.Progressbar(
                self.container, value=percent, maximum=100,
                bootstyle=progress_style(percent),
                length=400
            ).pack(pady=4)

            ttk.Label(
                self.container,
                text=f"Present: {c['P']} | Absent: {c['A']} | Classes needed: {need}",
                wraplength=450
            ).pack(anchor=W, pady=(0, 10))

        overall = (total_p / total_c) * 100

        ttk.Separator(self.container).pack(fill=X, pady=10)

        ttk.Label(self.container,
                  text=f"📈 Overall Attendance — {overall:.1f}%",
                  font=("Segoe UI", 12, "bold")).pack(anchor=W)

        ttk.Progressbar(
            self.container, value=overall, maximum=100,
            bootstyle=progress_style(overall),
            length=400
        ).pack(pady=8)

        ttk.Button(self.container, text="⬅ Back",
                   command=self.show_home).pack(pady=10)

    # ---------------- MANAGE DATA ----------------
    def show_manage(self):
        self.clear()

        ttk.Label(self.container, text="🧺 Manage Data",
                  font=("Segoe UI", 18, "bold")).pack(pady=20)

        ttk.Button(self.container, text="🧾 Delete Individual Classes",
                   width=30, bootstyle=WARNING,
                   command=self.show_delete_class).pack(pady=10)

        ttk.Button(self.container, text="📚 Delete Entire Subject",
                   width=30, bootstyle=DANGER,
                   command=self.show_delete_subject).pack(pady=10)

        ttk.Button(self.container, text="⬅ Back",
                   bootstyle=SECONDARY,
                   command=self.show_home).pack(pady=20)

    # ---------------- DELETE CLASS ----------------
    def show_delete_class(self):
        self.clear()
        rows = read_attendance()

        ttk.Label(self.container, text="🧾 Delete Classes",
                  font=("Segoe UI", 16, "bold")).pack(pady=10)

        subjects = sorted(set(r["subject"] for r in rows))

        if not subjects:
            ttk.Label(self.container, text="No data available").pack(pady=10)
            ttk.Button(self.container, text="⬅ Back",
                       command=self.show_manage).pack()
            return

        subject_var = tk.StringVar()
        subject_rows = []

        ttk.Combobox(self.container, textvariable=subject_var,
                     values=subjects, state="readonly",
                     width=30).pack(pady=5)

        listbox = tk.Listbox(self.container, selectmode=MULTIPLE,
                             width=50, height=10)
        listbox.pack(pady=10)

        def load_classes(*_):
            listbox.delete(0, END)
            subject_rows.clear()
            for r in rows:
                if r["subject"] == subject_var.get():
                    subject_rows.append(r)
                    listbox.insert(END, f"{r['date']} — {r['status']}")

        subject_var.trace_add("write", load_classes)

        def delete_selected():
            selected = listbox.curselection()
            if not selected:
                Messagebox.show_warning("Select at least one class")
                return

            remaining_subject_rows = [
                r for i, r in enumerate(subject_rows)
                if i not in selected
            ]

            new_rows = [r for r in rows if r["subject"] != subject_var.get()]
            new_rows.extend(remaining_subject_rows)

            write_attendance(new_rows)
            Messagebox.show_info("Selected classes deleted")
            self.show_manage()

        ttk.Button(self.container, text="🗑 Delete Selected",
                   bootstyle=DANGER,
                   command=delete_selected).pack(pady=10)

        ttk.Button(self.container, text="⬅ Back",
                   bootstyle=SECONDARY,
                   command=self.show_manage).pack()

    # ---------------- DELETE SUBJECT ----------------
    def show_delete_subject(self):
        self.clear()
        rows = read_attendance()

        ttk.Label(self.container, text="📚 Delete Subject",
                  font=("Segoe UI", 16, "bold")).pack(pady=15)

        subjects = sorted(set(r["subject"] for r in rows))

        if not subjects:
            ttk.Label(self.container, text="No subjects available").pack(pady=10)
            ttk.Button(self.container, text="⬅ Back",
                       command=self.show_manage).pack()
            return

        subject_var = tk.StringVar()

        ttk.Combobox(self.container,
                     textvariable=subject_var,
                     values=subjects,
                     state="readonly",
                     width=30).pack(pady=10)

        def delete_subject():
            if not subject_var.get():
                Messagebox.show_warning("Select a subject first")
                return

            new_rows = [r for r in rows if r["subject"] != subject_var.get()]
            write_attendance(new_rows)

            Messagebox.show_info("Subject deleted successfully")
            self.show_manage()

        ttk.Button(self.container, text="🗑 Delete Subject",
                   bootstyle=DANGER,
                   command=delete_subject).pack(pady=10)

        ttk.Button(self.container, text="⬅ Back",
                   bootstyle=SECONDARY,
                   command=self.show_manage).pack()


if __name__ == "__main__":
    AttendanceApp().mainloop()
