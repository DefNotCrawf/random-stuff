import string # for letters, digits and symbols
import secrets # for generating secure random characters
import getpass
import pyperclip # for copying to clipboard
import sys # for command line arguments
import subprocess # for clearing clipboard
from datetime import datetime, timedelta # for clearing clipboard from a fixed time afterwards
import os # for checking platform
import platform # for checking platform


i = 0
c_length = 16

if len(sys.argv) > 1:
	try:
		c_length = int(sys.argv[1])
	except ValueError:
		print("Please enter a valid number")
		sys.exit(1)
	if c_length < 16:
		print("Password length should be at least 16 characters")
		sys.exit(1)
else:
	while i < 5:
		try:
			c_length = int(input("Enter the length of the password: "))
			if c_length < 16:
				print("Password length should be at least 16 characters")
				i += 1
			else:
				break
		except ValueError:
			print("Please enter a valid number")
			i += 1
	else:
		print("Defaulting to 16 characters...")

alphabet = string.ascii_letters + string.digits + string.punctuation

while True:
	password = ''.join(secrets.choice(alphabet) for i in range(c_length))
	if (sum(c.islower() for c in password) >=4
			and sum(c.isupper() for c in password) >=4
			and sum(c.isdigit() for c in password) >=(c_length//5)
			and sum(c in string.punctuation for c in password) >=(c_length//4)):
		break
print(password)

if input("Do you want to copy the password to clipboard? (y/n): ").lower() == "y":
	pyperclip.copy(password)
	print("Password copied to clipboard")
	print("Clipboard will be cleared in 5 minutes. For users on Windows, a scheduled task has been created to clear the clipboard in 5 minutes. For users on other platforms, please clear the clipboard manually by running the command 'python clear_clipboard.py' in the terminal. Please note that manual clearing of clipboard may be needed.")
	if platform.system() == 'Windows':
		clear_time = (datetime.now() + timedelta(minutes=5)).strftime('%H:%M')
		subprocess.call(f'schtasks /Create /SC ONCE /TN "ClearClipboard" /TR "python clear_clipboard.py && schtasks /Delete /TN \'ClearClipboard\' /F" /ST {clear_time}', shell=True)
	else:
		os.system('echo "python clear_clipboard.py" | at now + 5 minutes')
else:
	print("Password not copied to clipboard")

if getpass.getpass("Press enter to exit..."): # to prevent the terminal from closing immediately
	sys.exit()