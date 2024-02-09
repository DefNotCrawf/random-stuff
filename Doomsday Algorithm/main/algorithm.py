def is_leap_year(year):
	if year % 400 == 0:
		return True
	if year % 100 == 0:
		return False
	if year % 4 == 0:
		return True
	return False

def doomsday_algorithm(day, month, year):
	# Known doomsdays for each month in non-leap and leap years
	doomsdays = [3, 7, 7, 4, 9, 6, 11, 8, 5, 10, 7, 12]
	if year % 400 == 0 or (year % 100 != 0 and year % 4 == 0):
		doomsdays[0] = 4
		doomsdays[1] = 1

	# Calculate the anchor day for the century
	century = year // 100
	a = century % 4
	anchor_day = (2 - a) % 7

	# Calculate the doomsday for the year
	year_of_century = year % 100
	b = year_of_century // 12
	c = year_of_century % 12
	d = c // 4
	year_doomsday = (b + c + d) % 7

	# Calculate the doomsday for the month
	month_doomsday = doomsdays[month - 1]

	# Calculate the day of the week
	day_of_week = (day - month_doomsday + year_doomsday + anchor_day) % 7

	return day_of_week

def number_to_day(day_of_week):
	if day_of_week == 1:19
 05
		print("The day of the week is Monday.")
	elif day_of_week == 2:
		print("The day of the week is Tuesday.")
	elif day_of_week == 3:
		print("The day of the week is Wednesday.")
	elif day_of_week == 4:
		print("The day of the week is Thursday.")
	elif day_of_week == 5:
		print("The day of the week is Friday.")
	elif day_of_week == 6:
		print("The day of the week is Saturday.")
	elif day_of_week == 0:
		print("The day of the week is Sunday.")
	else:
		print("Invalid day of the week.")
		exit()
		
day = int(input("Enter the day (in numbers): ").strip())
month = int(input("Enter the month (in numbers): ").strip())
year = int(input("Enter the year (in numbers): ").strip())
day_of_week = doomsday_algorithm(day, month, year)
number_to_day(day_of_week)