import json
from collections import Counter
from pathlib import Path

import requests


class CalendarData:
    CACHE_DIR = Path(__file__).resolve().parent / "calendar_cache"
    MONTHS_NAME = [
        "Farvardin", "Ordibehesht", "Khordad", "Tir", "Mordad",
        "Shahrivar", "Mehr", "Aban", "Azar", "Dey", "Bahman", "Esfand"]

    def __init__(self, year, month):
        self.year = int(year)
        self.month = int(month)
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.CACHE_DIR / f"{self.year}_{self.month:02d}.json"

    def get_days(self, refresh=False):
        if not refresh and self.cache_file.exists():
            try:
                return json.loads(self.cache_file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass

        url = f"https://pnldev.com/api/calender?year={self.year}&month={self.month}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("status") is False or "result" not in data:
            raise ValueError(data.get("result", "Invalid calendar response"))

        days = data["result"]
        self.cache_file.write_text(
            json.dumps(days, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return days

    def get_calendar_data(self, refresh=False):
        days = self.get_days(refresh=refresh)
        counter = Counter()
        for item in days.values():
            weekday = item.get("solar", {}).get("dayWeek")
            if not item.get("holiday", False) and weekday:
                counter[weekday] += 1

        return {
            "Year": self.year,
            "Month": self.MONTHS_NAME[self.month - 1],
            "Shanbe": counter["ش"],
            "Yekshanbe": counter["ی"],
            "Doshanbe": counter["د"],
            "Seshanbe": counter["س"],
            "Chaharshanbe": counter["چ"],
            "Panjshanbe": counter["پ"]
        }

    def get_daily_work_hours(self, jalali_date):
        days = self.get_days()
        for key, item in days.items():
            solar = item.get("solar", {})
            day_number = solar.get("day", solar.get("dayNumber", key))
            try:
                day_number = int(day_number)
            except (ValueError, TypeError):
                continue
            if day_number == int(jalali_date.day):
                if item.get("holiday", False):
                    return 0
                weekday = solar.get("dayWeek")
                if weekday in ("ش", "ی", "د", "س", "چ"):
                    return 8
                if weekday == "پ":
                    return 5
                return 0
        raise ValueError(f"Day {jalali_date.day} not found in calendar")
