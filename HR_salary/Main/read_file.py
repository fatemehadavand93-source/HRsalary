import pandas as pd
import jdatetime


class AttendanceReader:
    '''
    **Purpose:**
    Reads employee attendance data from the `HR.TXT` file.
    
    **Main Method:**
    
    * `read(filename)` — Reads the attendance file and returns a Pandas DataFrame.
    
    **Example:**
    
    reader = AttendanceReader()
    df = reader.read("HR.TXT")
    
    **Used for:**
    Loading and preparing attendance data for further calculations.
    '''
    
    def __init__(self, file_path):
        self.file_path = file_path

    def read(self):
        
        df = pd.read_csv(self.file_path, header=None)

        df.columns = ["id", "hour", "date", "x", "y", "z"]

        df["date"] = df["date"].apply(
            lambda x: jdatetime.datetime.strptime(
                str(x), "%Y/%m/%d").date())

        df["hour"] = pd.to_timedelta(
            df["hour"].astype(str))

        return df

