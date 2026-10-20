import pandas as pd


class WorkHoursCalculator:

    def __init__(self, df, cale, year, month, hourly_leave=None):
        self.df = df.copy()
        self.cale = cale
        self.year = year
        self.month = month
        self.hourly_leave = hourly_leave or {}
        self.count = None
        self.id_hour = None

    def filter_month(self):
        self.df = self.df[
            (self.df["date"].apply(lambda x: x.year) == self.year) &
            (self.df["date"].apply(lambda x: x.month) == self.month)
        ].copy()

    def calculate_mandatory_hours(self):
        shanbe = self.cale["Shanbe"]
        yekshanbe = self.cale["Yekshanbe"]
        doshanbe = self.cale["Doshanbe"]
        seshanbe = self.cale["Seshanbe"]
        chaharshanbe = self.cale["Chaharshanbe"]
        panjshanbe = self.cale["Panjshanbe"]

        mandatory = ((shanbe + yekshanbe + doshanbe
             + seshanbe + chaharshanbe) * 8
            + panjshanbe * 5)

        return mandatory

    def adjust_delay(self):
        delay = (
            (self.df["hour"] >= pd.Timedelta("09:00:00")) &
            (self.df["hour"] < pd.Timedelta("09:16:00")))

        self.df.loc[delay, "hour"] = pd.Timedelta("09:00:00")

    def calculate_daily_hours(self):
        self.count = self.df.groupby(["id", "date"])["hour"].count()

        valid_days = self.count[self.count > 1].index

        daily_hours = self.df.groupby(["id", "date"])["hour"].apply(
            lambda x: x.max() - x.min())

        self.id_hour = daily_hours.loc[valid_days].copy()
        return self.id_hour

    
    def calculate_operating_hours(self):
        if self.id_hour is None:
            self.calculate_daily_hours()
    
        daily_hours = self.id_hour.copy()
    
        for (employee_id, date), duration in daily_hours.items():
    
            key = (int(employee_id),
                date.year,
                date.month,
                date.day)
    
            leave_hours = float(self.hourly_leave.get(key, 0))
    
            leave_duration = pd.Timedelta(hours=leave_hours)
    
            net_duration = max(duration - leave_duration,
                pd.Timedelta(0))
    
            daily_hours.loc[(employee_id, date)] = net_duration
    
        return daily_hours.groupby(level="id").sum()


    def calculate_difference(self, operating_hours, mandatory_hours):
        difference = (
            pd.Timedelta(hours=mandatory_hours) - operating_hours)
        return difference

    def format_hours(self, hours):
        def format_one(value):
            total_seconds = int(value.total_seconds())

            sign = "-" if total_seconds < 0 else ""
            total_seconds = abs(total_seconds)

            h = total_seconds // 3600
            m = (total_seconds % 3600) // 60
            s = total_seconds % 60

            return f"{sign}{h}:{m:02d}:{s:02d}"

        return hours.apply(format_one)
