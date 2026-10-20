
from calendar_data import CalendarData
from read_file import AttendanceReader
from work_time import WorkHoursCalculator
from pathlib import Path
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
reader = AttendanceReader(BASE_DIR / "HR.TXT")

year = 1405
month = 2

calendar = CalendarData(year, month)
cale = calendar.get_calendar_data()

df = reader.read()

calculator = WorkHoursCalculator(df, cale, year, month)

calculator.filter_month()

mandatory_hours = calculator.calculate_mandatory_hours()
print("\nMandatory work hours:", mandatory_hours)
print("=" * 60)

calculator.adjust_delay()

operating_hours = calculator.calculate_operating_hours()

print("\nOne fingerprint:")
print(calculator.count[calculator.count == 1])
print("=" * 60)

print("\nOperating hours:")
print(calculator.format_hours(operating_hours))

difference = calculator.calculate_difference(
    operating_hours,
    mandatory_hours)

print("\nDifference:")
print(calculator.format_hours(difference))
