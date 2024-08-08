import pyautogui
import time
import random

# Get the current mouse position
original_x, original_y = pyautogui.position()


t_end = time.time() + 5
time.sleep(1)


def move_randomly():
    while time.time() < t_end:
        # Generate random coordinates within your screen size
        random_x = random.randint(75, 2483)
        random_y = random.randint(256, 1457)
        print(f"{random_x}\t{random_y}", end="\n")
        pyautogui.moveTo(random_x, random_y, duration=0.3)
# Function to move the mouse randomly

pyautogui.moveTo(75, 256)
pyautogui.mouseDown()

move_randomly()

pyautogui.mouseUp()



# time.sleep(1)

pyautogui.moveTo(original_x, original_y)


# import pyautogui, sys
# print('Press Ctrl-C to quit.')
# try:
#     while True:
#         x, y = pyautogui.position()
#         positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
#         print(positionStr, end='')
#         print('\b' * len(positionStr), end='', flush=True)
# except KeyboardInterrupt:
#     print('\n')