import csv

class collatz():
	def __init__(self) -> None:
		...
	def collatz(self) -> None:
		i = 1
		self.output = []
		self.output.append([i, self.number])
		while self.number != 1:
			if self.number % 2 == 0:
				self.number = self.even()
				i += 1
				self.output.append([i, self.number])
			else:
				self.number = self.odd()
				i += 1
				self.output.append([i, self.number])
		self.write_to_csv()

	def write_to_csv(self):
		try:
			with open('output.csv', 'w', newline='') as file:
				writer = csv.writer(file)
				writer.writerow(['Step', 'Number'])  # Add this line to write the header
				writer.writerows(self.output)
		except PermissionError:
			print("Permission denied: Unable to write to 'output.csv'. Please check if the file is open or write-protected.")
		with open('output.csv', 'w', newline='') as file:
				writer = csv.writer(file)
				writer.writerow(['Step', 'Number'])  # Add this line to write the header
				writer.writerows(self.output)

	def get(self):
		while True:
			try:
				self.number = int(input("Enter a number: "))
				break
			except ValueError:
				print("That's not a valid number! Please try again.")
		if self.number < 1:
			print("Invalid input")
			self.get()

	def even(self):
		return self.number // 2
	
	def odd(self):
		return 3 * self.number + 1




def main():
	number = collatz()
	number.get()
	number.collatz()
	re()

def re():
	option = input("Enter 'E' to exit or 'R' to restart: ").upper()

	if option == 'R':
		main()
	elif option == 'E':
		exit()
	else:
		exit()

main()