import requests
import time
import argparse
import sys
import threading

# Set up argument parser
parser = argparse.ArgumentParser(description="Check the uptime of a website.")
parser.add_argument('website_url', type=str, help='The URL of the website to check. Accepts both http://, https://, and localhost URLs.')
parser.add_argument('--interval', '-i', type=int, default=60, help='Time in seconds between checks (default: 60 seconds).')
parser.add_argument('--timeout', '-t', type=int, default=5, help='Timeout in seconds for the request (default: 5 seconds).')
args = parser.parse_args()

website_url = args.website_url
check_interval = args.interval
request_timeout = args.timeout

# Check if the website URL starts with http://, https://, or localhost
if not (website_url.startswith('http://') or website_url.startswith('https://') or website_url.startswith('localhost')):
	print("Error: The website URL must start with 'http://', 'https://', or 'localhost'.")
	sys.exit(1)

# Prepend 'http://' to localhost URLs if not already present
if website_url.startswith('localhost'):
	website_url = 'http://' + website_url

# Initialize timers
start_time = time.time()
total_online_time = 0
total_offline_time = 0
stop_flag = threading.Event()

def handle_response_status(response, duration):
	global total_online_time, total_offline_time
	print(f"Debug: Response status code: {response.status_code}")  # Debugging information
	if response.status_code == 200:
		print(f"[{time.strftime('%d-%m-%Y %H:%M:%S')}] Website is up!")
		total_online_time += duration
	elif response.status_code in {400, 401, 403, 404, 500, 502, 503, 504}:
		print(f"[{time.strftime('%d-%m-%Y %H:%M:%S')}] Website is down! Status code: {response.status_code}")
		total_offline_time += duration
	else:
		print(f"[{time.strftime('%d-%m-%Y %H:%M:%S')}] Website is down! Status code: {response.status_code}")
		total_offline_time += duration

def check_website():
	global total_offline_time
	start_check_time = time.time()
	try:
		response = requests.get(website_url, timeout=request_timeout)
		end_check_time = time.time()
		handle_response_status(response, end_check_time - start_check_time)
		return response
	except requests.exceptions.ConnectionError:
		print(f"[{time.strftime('%d-%m-%Y %H:%M:%S')}] Error: Unable to connect to the website. Please check the URL or your internet connection.") # Error Code: 503
		end_check_time = time.time()
		total_offline_time += end_check_time - start_check_time
	except requests.exceptions.Timeout:
		print(f"[{time.strftime('%d-%m-%Y %H:%M:%S')}] Error: The request timed out. The server may be too slow or unresponsive.") # Error Code: 408
		end_check_time = time.time()
		total_offline_time += end_check_time - start_check_time
	except requests.exceptions.RequestException as e:
		print(f"[{time.strftime('%d-%m-%Y %H:%M:%S')}] An unexpected error occurred: {e}") # Unknown Error
		end_check_time = time.time()
		total_offline_time += end_check_time - start_check_time
	return None

def monitor_website():
	global total_online_time, total_offline_time
	while not stop_flag.is_set():
		start_loop_time = time.time()
		response = check_website()
		end_loop_time = time.time()
		actual_duration = end_loop_time - start_loop_time
		if response and response.status_code == 200:
			total_online_time += check_interval
		else:
			total_offline_time += check_interval
		time.sleep(max(0, check_interval - actual_duration))

try:
	monitor_thread = threading.Thread(target=monitor_website)
	monitor_thread.start()
	while monitor_thread.is_alive():
		monitor_thread.join(1)
except KeyboardInterrupt:
	stop_flag.set()
	monitor_thread.join()
	end_time = time.time()
	total_elapsed_time = end_time - start_time
	print("\nProgram terminated by user.")
	print(f"Total elapsed time: {total_elapsed_time:.2f} seconds")
	print(f"Total online time: {total_online_time:.2f} seconds")
	print(f"Total offline time: {total_offline_time:.2f} seconds")
	print(f"Sum of online and offline time: {total_online_time + total_offline_time:.2f} seconds")
	sys.exit(0)