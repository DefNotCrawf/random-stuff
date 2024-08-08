class collatz():
	def __init__(self) -> None: # ask user for input
		pass
		# self.day = int(input("Enter the day (in numbers): ").strip())
		# self.month = int(input("Enter the month (in numbers): ").strip())
		# self.year = int(input("Enter the year (in numbers): ").strip())
		# self.day_of_week = self.doomsday_algorithm()

	@property
	def month(self):
		return self._month

	@month.setter
	def month(self, value):
		if value < 1 or value > 12:
			raise ValueError("Invalid month")
		self._month = value

	def doomsday_algorithm(self):
		pass
	
	def write_to_csv(self):
		pass
	
	def get(self):
		pass
	
	def even(self):
		pass
	
	def odd(self):
		pass
	
	def __str__(self) -> str: # return the day of the week
		pass
		if self.day_of_week == 1:
			return "The day of the week is Monday."
		elif self.day_of_week == 2:
			return "The day of the week is Tuesday."
		elif self.day_of_week == 3:
			return "The day of the week is Wednesday."
		elif self.day_of_week == 4:
			return "The day of the week is Thursday."
		elif self.day_of_week == 5:
			return "The day of the week is Friday."
		elif self.day_of_week == 6:
			return "The day of the week is Saturday."
		elif self.day_of_week == 0:
			return "The day of the week is Sunday."

def main():
	pass

if __name__ == "__main__":
	main()