import datetime

def check_day(date):
    day_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day = datetime.datetime.strptime(date, '%d/%m/%Y').weekday()
    return day_of_week[day]

print(check_day('19/05/2008'))  # Outputs: 'Monday'