# HR Salary Management System

A Python-based application for managing employee attendance and calculating working hours using attendance records and calendar data.

## Features

- Read and process employee attendance records.
- Calculate working hours for a selected month.
- Handle calendar data and dates.
- Organize the application into separate Python modules.
- Provide a graphical user interface.

## Project Structure

```text
HR_salary/
├── Main/
│   ├── UI.py
│   ├── calendar_data.py
│   ├── read_file.py
│   ├── work_time.py
│   └── HR.TXT
├── .gitignore
└── README.md
```

## Requirements

- Python 3.10 or later
- pandas
- customtkinter
- requests
- jdatetime

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/fatemehadavand93-source/HRsalary.git
   ```

2. Navigate to the project directory:

   ```bash
   cd HRsalary
   ```

3. Install the required packages:

   ```bash
   pip install pandas customtkinter requests jdatetime
   ```

## Usage

Run the graphical interface:

```bash
python Main/UI.py
```

Make sure the required attendance and calendar data files are available before running the application.

## Technologies

- Python
- Pandas
- CustomTkinter

## Future Improvements

- Improve input validation and error handling.
- Add salary calculation and reporting features.
- Improve documentation and usability.

## Author

Fatemeh Hadavand
