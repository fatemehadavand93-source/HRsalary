
import json
import sys
from pathlib import Path
from tkinter import ttk, messagebox

import customtkinter as ctk
import jdatetime
import pandas as pd

from calendar_data import CalendarData
from read_file import AttendanceReader
from work_time import WorkHoursCalculator


ANNUAL_LEAVE_LIMIT = 26

if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).resolve().parent
else:
    APP_DIR = Path(__file__).resolve().parent

LEAVES_FILE = APP_DIR / "leaves.json"


class HRApp:

    def __init__(self, root):
        self.root = root
        self.startup_failed = False

        self.root.title("HR Salary System")
        self.root.geometry("1250x740")
        self.root.minsize(950, 600)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        try:
            self.df = AttendanceReader(
                str(APP_DIR / "HR.TXT")).read()

        except Exception as exc:
            messagebox.showerror(
                "File error",
                f"Could not read HR.TXT:\n"
                f"{APP_DIR / 'HR.TXT'}\n\n{exc}")
            self.startup_failed = True
            return

        self.leaves = self.load_leaves()
        self.calendar = None

        self.create_ui()

    # --------------------------------------------------
    # Load and save leave data
    # --------------------------------------------------

    def load_leaves(self):
        if not LEAVES_FILE.exists():
            return {}

        try:
            data = json.loads(
                LEAVES_FILE.read_text(encoding="utf-8")
            )

            return {
                int(employee_id): records
                for employee_id, records in data.items()
            }

        except (OSError, ValueError, TypeError):
            messagebox.showwarning(
                "Leave data",
                "Could not read leaves.json. An empty leave list will be used."
            )
            return {}

    def save_leaves(self):
        LEAVES_FILE.write_text(
            json.dumps(
                self.leaves,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

    # --------------------------------------------------
    # Main window
    # --------------------------------------------------

    def create_ui(self):
        header = ctk.CTkFrame(
            self.root,
            corner_radius=14
        )
        header.pack(
            fill="x",
            padx=18,
            pady=(18, 8)
        )

        ctk.CTkLabel(
            header,
            text="HR Salary System",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=18,
            pady=(14, 2)
        )

        ctk.CTkLabel(
            header,
            text="Monthly employee attendance and leave summary"
        ).pack(
            anchor="w",
            padx=18,
            pady=(0, 14)
        )

        filters = ctk.CTkFrame(
            self.root,
            corner_radius=14
        )
        filters.pack(
            fill="x",
            padx=18,
            pady=8
        )

        ctk.CTkLabel(
            filters,
            text="Year"
        ).grid(
            row=0,
            column=0,
            padx=(12, 4),
            pady=12
        )

        self.year_entry = ctk.CTkEntry(
            filters,
            width=90,
            placeholder_text="1405"
        )
        self.year_entry.grid(
            row=0,
            column=1,
            padx=4,
            pady=12
        )

        ctk.CTkLabel(
            filters,
            text="Month"
        ).grid(
            row=0,
            column=2,
            padx=(10, 4),
            pady=12
        )

        self.month_entry = ctk.CTkEntry(
            filters,
            width=70,
            placeholder_text="2"
        )
        self.month_entry.grid(
            row=0,
            column=3,
            padx=4,
            pady=12
        )

        ctk.CTkLabel(
            filters,
            text="Employee ID (optional)"
        ).grid(
            row=0,
            column=4,
            padx=(10, 4),
            pady=12
        )

        self.id_entry = ctk.CTkEntry(
            filters,
            width=145,
            placeholder_text="Blank = all employees"
        )
        self.id_entry.grid(
            row=0,
            column=5,
            padx=4,
            pady=12
        )

        ctk.CTkButton(
            filters,
            text="Show Status",
            command=self.show_status,
            width=120
        ).grid(
            row=0,
            column=6,
            padx=6,
            pady=12
        )

        ctk.CTkButton(
            filters,
            text="Register Leave",
            command=self.open_leave_window,
            width=125,
            fg_color="#16856b",
            hover_color="#106b55"
        ).grid(
            row=0,
            column=7,
            padx=(4, 12),
            pady=12
        )

        ctk.CTkButton(
            filters,
            text="Refresh Calendar",
            command=self.refresh_calendar,
            width=140,
            fg_color="#7657b7",
            hover_color="#5f4396"
        ).grid(
            row=1,
            column=6,
            padx=6,
            pady=(0, 12)
        )

        self.calendar_status = ctk.CTkLabel(
            filters,
            text="Enter a Jalali year and month."
        )
        self.calendar_status.grid(
            row=1,
            column=0,
            columnspan=6,
            sticky="w",
            padx=14,
            pady=(0, 12)
        )

        # Results table
        frame = ctk.CTkFrame(
            self.root,
            corner_radius=14
        )
        frame.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(8, 18)
        )

        self.columns = (
            "id",
            "mandatory",
            "recorded",
            "hourly_leave",
            "net_work",
            "leave_credit",
            "balance",
            "annual",
            "sick",
            "remaining"
        )

        self.tree = ttk.Treeview(
            frame,
            columns=self.columns,
            show="headings"
        )

        labels = {
            "id": "Employee ID",
            "mandatory": "Mandatory Hours",
            "recorded": "Attendance Hours",
            "hourly_leave": "Hourly Leave",
            "net_work": "Net Hours",
            "leave_credit": "Full-day Leave Credit",
            "balance": "Balance",
            "annual": "Annual Leave (days)",
            "sick": "Sick Leave (days)",
            "remaining": "Annual Leave Left"
        }

        widths = {
            "id": 95,
            "mandatory": 120,
            "recorded": 125,
            "hourly_leave": 115,
            "net_work": 105,
            "leave_credit": 145,
            "balance": 105,
            "annual": 125,
            "sick": 115,
            "remaining": 130
        }

        for col in self.columns:
            self.tree.heading(
                col,
                text=labels[col]
            )
            self.tree.column(
                col,
                width=widths[col],
                anchor="center"
            )

        ybar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=self.tree.yview
        )

        xbar = ttk.Scrollbar(
            frame,
            orient="horizontal",
            command=self.tree.xview
        )

        self.tree.configure(
            yscrollcommand=ybar.set,
            xscrollcommand=xbar.set
        )

        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(10, 0),
            pady=(10, 0)
        )

        ybar.grid(
            row=0,
            column=1,
            sticky="ns",
            pady=(10, 0),
            padx=(0, 10)
        )

        xbar.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=(10, 0),
            pady=(0, 10)
        )

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            rowheight=30,
            font=("Arial", 10)
        )
        style.configure(
            "Treeview.Heading",
            font=("Arial", 10, "bold")
        )

    # --------------------------------------------------
    # Year and month
    # --------------------------------------------------

    def get_year_month(self):
        try:
            year = int(self.year_entry.get().strip())
            month = int(self.month_entry.get().strip())

            if year < 1 or not 1 <= month <= 12:
                raise ValueError

            return year, month

        except ValueError:
            messagebox.showerror(
                "Invalid input",
                "Enter a valid Jalali year and month."
            )
            return None

    def refresh_calendar(self):
        ym = self.get_year_month()

        if ym is None:
            return

        year, month = ym

        try:
            CalendarData(
                year,
                month
            ).get_calendar_data(refresh=True)

            self.calendar_status.configure(
                text=f"Calendar refreshed for {year}/{month:02d}."
            )

            messagebox.showinfo(
                "Calendar",
                "Calendar updated successfully."
            )

        except Exception as exc:
            messagebox.showerror(
                "Calendar error",
                str(exc)
            )

    # --------------------------------------------------
    # Format hours as H:MM:SS
    # --------------------------------------------------

    def fmt_hours(self, value):
        total = int(value.total_seconds())

        sign = "-" if total < 0 else ""
        total = abs(total)

        h, rem = divmod(total, 3600)
        m, s = divmod(rem, 60)

        return f"{sign}{h}:{m:02d}:{s:02d}"

    # --------------------------------------------------
    # Get employee leave records for a month
    # --------------------------------------------------

    def month_leaves(self, employee_id, year, month):
        results = []

        for leave in self.leaves.get(int(employee_id), []):
            try:
                date = jdatetime.datetime.strptime(
                    leave["date"],
                    "%Y/%m/%d"
                ).date()

            except (ValueError, KeyError, TypeError):
                continue

            if date.year == year and date.month == month:
                results.append((leave, date))

        return results

    # --------------------------------------------------
    # Calculate and show monthly status
    # --------------------------------------------------

    
    
    def show_status(self):
        try:
            year, month = self.get_year_month()
    
            # بارگذاری اطلاعات تقویم
            self.calendar = CalendarData(year, month)
            cale = self.calendar.get_calendar_data()
    
            # خواندن اطلاعات حضور و غیاب
            reader = AttendanceReader("HR.TXT")
            df = reader.read()
    
            # محاسبه ساعت کاری
            calc = WorkHoursCalculator(
                df=df,
                cale=cale,
                year=year,
                month=month
            )
    
            calc.filter_month()
            mandatory_hours = calc.calculate_mandatory_hours()
            calc.adjust_delay()
    
            # ساعت کاری روزانه معتبر و مجموع ساعت کاری ثبت‌شده
            daily_hours = calc.calculate_daily_hours()
            recorded_hours = daily_hours.groupby(level="id").sum()
    
            # جمع مرخصی ساعتی هر کارمند در ماه انتخاب‌شده
            hourly_leave_by_employee = {}
    
            for employee_id, records in self.leaves.items():
                for leave in records:
                    if leave.get("type") != "Hourly":
                        continue
    
                    leave_date = jdatetime.datetime.strptime(
                        leave["date"], "%Y/%m/%d"
                    ).date()
    
                    if leave_date.year == year and leave_date.month == month:
                        hourly_leave_by_employee[employee_id] = (
                            hourly_leave_by_employee.get(employee_id, 0)
                            + float(leave.get("hours", 0))
                        )
    
            # محاسبه ساعت کاری خالص پس از کسر مرخصی ساعتی
            hourly_leave = {}
    
            for (employee_id, date), duration in daily_hours.items():
                key = (
                    int(employee_id),
                    date.year,
                    date.month,
                    date.day
                )
    
                # مجموع مرخصی ساعتی ثبت‌شده برای همان روز
                leave_hours = sum(
                    float(leave.get("hours", 0))
                    for leave in self.leaves.get(int(employee_id), [])
                    if leave.get("type") == "Hourly"
                    and jdatetime.datetime.strptime(
                        leave["date"], "%Y/%m/%d"
                    ).date() == date
                )
    
                hourly_leave[key] = leave_hours
    
            calc.hourly_leave = hourly_leave
            net_hours = calc.calculate_operating_hours()
    
            # فیلتر شناسه کارمند، در صورت وارد شدن
            employee_text = self.id_entry.get().strip()
            if employee_text:
                selected_id = int(employee_text)
                employee_ids = {selected_id}
            else:
                employee_ids = set(recorded_hours.index)
                employee_ids.update(hourly_leave_by_employee.keys())
    
            # پاک کردن ردیف‌های قبلی جدول
            for item in self.tree.get_children():
                self.tree.delete(item)
    
            # نمایش وضعیت هر کارمند
            for employee_id in sorted(employee_ids):
                recorded = recorded_hours.get(
                    employee_id, pd.Timedelta(0)
                )
                net = net_hours.get(
                    employee_id, pd.Timedelta(0)
                )
    
                leave_hours = hourly_leave_by_employee.get(employee_id, 0)
    
                balance = (
                    pd.Timedelta(hours=mandatory_hours) - net
                )
    
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        employee_id,
                        calc.format_hours(
                            pd.Series([pd.Timedelta(hours=mandatory_hours)])
                        ).iloc[0],
                        calc.format_hours(
                            pd.Series([recorded])
                        ).iloc[0],
                        f"{leave_hours:g}",
                        calc.format_hours(
                            pd.Series([net])
                        ).iloc[0],
                        "—",
                        calc.format_hours(
                            pd.Series([net - pd.Timedelta(hours=mandatory_hours)])
                        ).iloc[0],
                        "—",
                        "—",
                        "—"
                    )
                )
    
        except Exception as exc:
            messagebox.showerror(
                "Show Status Error",
                f"Could not calculate employee status:\n\n{exc}"
            )
    


    # --------------------------------------------------
    # Hourly leave details
    # --------------------------------------------------

    def show_hourly_leave_details(self):
        ym = self.get_year_month()

        if ym is None:
            return

        year, month = ym
        raw_id = self.id_entry.get().strip()

        try:
            selected_id = int(raw_id) if raw_id else None

        except ValueError:
            messagebox.showerror(
                "Invalid ID",
                "Employee ID must be numeric."
            )
            return

        lines = []
        total_by_employee = {}

        for employee_id, records in sorted(self.leaves.items()):
            employee_id = int(employee_id)

            if (
                selected_id is not None
                and employee_id != selected_id
            ):
                continue

            for leave, date in self.month_leaves(
                employee_id,
                year,
                month
            ):
                if leave.get("type") != "Hourly":
                    continue

                hours = float(leave.get("hours", 0))
                date_text = (
                    f"{date.year:04d}/"
                    f"{date.month:02d}/"
                    f"{date.day:02d}"
                )

                lines.append(
                    (date_text, employee_id, hours)
                )

                total_by_employee[employee_id] = (
                    total_by_employee.get(employee_id, 0.0)
                    + hours
                )

        if not lines:
            messagebox.showinfo(
                "Hourly Leave Details",
                "No hourly leave found for this month."
            )
            return

        lines.sort(
            key=lambda item: (item[1], item[0])
        )

        details = [
            f"{date_text} | Employee {employee_id} | "
            f"{hours:g} hour(s)"
            for date_text, employee_id, hours in lines
        ]

        details.append("\nMonthly totals:")

        details.extend(
            f"Employee {employee_id}: {hours:g} hour(s)"
            for employee_id, hours
            in sorted(total_by_employee.items())
        )

        messagebox.showinfo(
            "Hourly Leave Details",
            "\n".join(details)
        )

    # --------------------------------------------------
    # Register leave
    # --------------------------------------------------

    def open_leave_window(self):
        win = ctk.CTkToplevel(self.root)
        win.title("Register Leave")
        win.geometry("460x420")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        ctk.CTkLabel(
            win,
            text="Register Employee Leave",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        ).pack(pady=(18, 10))

        form = ctk.CTkFrame(
            win,
            fg_color="transparent"
        )
        form.pack(
            padx=25,
            pady=5
        )

        fields = [
            ("Employee ID", "id"),
            ("Leave date (Jalali)", "date"),
            ("Amount", "amount")
        ]

        entries = {}

        for row, (label, key) in enumerate(fields):
            ctk.CTkLabel(
                form,
                text=label
            ).grid(
                row=row,
                column=0,
                sticky="w",
                padx=6,
                pady=10
            )

            entry = ctk.CTkEntry(
                form,
                width=200
            )
            entry.grid(
                row=row,
                column=1,
                padx=6,
                pady=10
            )

            entries[key] = entry

        entries["date"].insert(0, "1405/02/15")
        entries["amount"].insert(0, "1")

        ctk.CTkLabel(
            form,
            text="Leave type"
        ).grid(
            row=3,
            column=0,
            sticky="w",
            padx=6,
            pady=10
        )

        # Define kind before using it.
        kind = ctk.CTkComboBox(
            form,
            values=[
                "Estahghaghi",
                "Estealaji",
                "Hourly"
            ],
            state="readonly",
            width=200
        )

        kind.set("Estahghaghi")
        kind.grid(
            row=3,
            column=1,
            padx=6,
            pady=10
        )

        amount_label = ctk.CTkLabel(
            form,
            text="Days"
        )
        amount_label.grid(
            row=2,
            column=2,
            padx=(4, 0),
            pady=10
        )

        def update_amount_label(choice):
            if choice == "Hourly":
                amount_label.configure(text="Hours")
            else:
                amount_label.configure(text="Days")

        kind.configure(
            command=update_amount_label
        )

        ctk.CTkLabel(
            win,
            text=(
                "Use Jalali date YYYY/MM/DD.\n"
                "For Hourly leave, enter the number of hours."
            ),
            text_color="gray"
        ).pack(pady=5)

        def save():
            try:
                employee_id = int(
                    entries["id"].get().strip()
                )

                if employee_id <= 0:
                    raise ValueError

                date_text = entries["date"].get().strip()

                date = jdatetime.datetime.strptime(
                    date_text,
                    "%Y/%m/%d"
                ).date()

                amount = float(
                    entries["amount"].get().strip()
                )

                if amount <= 0:
                    raise ValueError

            except (ValueError, TypeError):
                messagebox.showerror(
                    "Invalid input",
                    "Enter a valid employee ID, Jalali date "
                    "(YYYY/MM/DD), and a positive amount.",
                    parent=win
                )
                return

            leave_type = kind.get()
            date_value = (
                f"{date.year:04d}/"
                f"{date.month:02d}/"
                f"{date.day:02d}"
            )

            # Do not modify the stored records until saving succeeds.
            old_records = self.leaves.get(
                employee_id,
                []
            )
            records = list(old_records)

            if leave_type == "Hourly":
                records.append({
                    "date": date_value,
                    "type": "Hourly",
                    "hours": amount
                })

                success_text = (
                    f"{amount:g} hour(s) of hourly leave "
                    f"saved for {date_value}."
                )

            else:
                days = amount

                # Count annual leave in the same Jalali year.
                previous_annual = 0.0

                for item in records:
                    if item.get("type") != "Estahghaghi":
                        continue

                    try:
                        item_date = jdatetime.datetime.strptime(
                            item["date"],
                            "%Y/%m/%d"
                        ).date()
                    except (ValueError, KeyError, TypeError):
                        continue

                    if item_date.year == date.year:
                        previous_annual += float(
                            item.get("days", 0)
                        )

                deduction = 0.0

                if leave_type == "Estahghaghi":
                    available = max(
                        0,
                        ANNUAL_LEAVE_LIMIT - previous_annual
                    )

                    deduction = max(
                        0,
                        days - available
                    )

                    if deduction:
                        messagebox.showwarning(
                            "Annual leave limit exceeded",
                            f"{deduction:g} day(s) exceed the "
                            "annual allowance and are marked "
                            "for salary deduction.",
                            parent=win
                        )

                records.append({
                    "date": date_value,
                    "days": days,
                    "type": leave_type,
                    "salary_deduction_days": deduction
                })

                success_text = "Leave registered and saved."

            self.leaves[employee_id] = records

            try:
                self.save_leaves()

            except OSError as exc:
                if old_records:
                    self.leaves[employee_id] = old_records
                else:
                    self.leaves.pop(employee_id, None)

                messagebox.showerror(
                    "Save error",
                    str(exc),
                    parent=win
                )
                return

            messagebox.showinfo(
                "Success",
                success_text,
                parent=win
            )

            win.destroy()

    # Save button must be outside save(), but inside open_leave_window().
        ctk.CTkButton(
            win,
            text="Save Leave",
            command=save,
            width=180,
            fg_color="#16856b",
            hover_color="#106b55"
        ).pack(pady=15)


if __name__ == "__main__":
    root = ctk.CTk()
    app = HRApp(root)

    if app.startup_failed:
        root.destroy()
    else:
        root.mainloop()
