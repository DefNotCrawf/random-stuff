import datetime

def check_day(date):
    day_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day = datetime.datetime.strptime(date, '%d/%m/%Y').weekday()
    return day_of_week[day]

print(check_day('01/01/2000 '))  # Outputs: 'Monday'

