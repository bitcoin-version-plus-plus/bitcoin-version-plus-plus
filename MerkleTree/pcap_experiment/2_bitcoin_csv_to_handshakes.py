import csv
import os
import re
import sys
import time

# Given a regular expression, list the files that match it, and ask for user input
def selectFile(regex, subdirs = False):
	files = []
	if subdirs:
		for (dirpath, dirnames, filenames) in os.walk('.'):
			for file in filenames:
				path = os.path.join(dirpath, file)
				if path[:2] == '.\\': path = path[2:]
				if bool(re.match(regex, path)):
					files.append(path)
	else:
		for file in os.listdir(os.curdir):
			if os.path.isfile(file) and bool(re.match(regex, file)):
				files.append(file)
	
	print()
	if len(files) == 0:
		print(f'No files were found that match "{regex}"')
		print()
		return ''

	print('List of files:')
	for i, file in enumerate(files):
		print(f'  File {i + 1}  -  {file}')
	print()

	selection = None
	while selection is None:
		try:
			i = int(input(f'Please select a file (1 to {len(files)}): '))
		except KeyboardInterrupt:
			sys.exit()
		except:
			pass
		if i > 0 and i <= len(files):
			selection = files[i - 1]
	print()
	return selection

# Given a regular expression, list the directories that match it, and ask for user input
def selectDir(regex, subdirs = False):
	dirs = []
	if subdirs:
		for (dirpath, dirnames, filenames) in os.walk('.'):
			if dirpath[:2] == '.\\': dirpath = dirpath[2:]
			if bool(re.match(regex, dirpath)):
				dirs.append(dirpath)
	else:
		for obj in os.listdir(os.curdir):
			if os.path.isdir(obj) and bool(re.match(regex, obj)):
				dirs.append(obj)

	print()
	if len(dirs) == 0:
		print(f'No directories were found that match "{regex}"')
		print()
		return ''

	print('List of directories:')
	for i, directory in enumerate(dirs):
		print(f'  Directory {i + 1}  -  {directory}')
	print()

	selection = None
	while selection is None:
		try:
			i = int(input(f'Please select a directory (1 to {len(dirs)}): '))
		except KeyboardInterrupt:
			sys.exit()
		except:
			pass
		if i > 0 and i <= len(dirs):
			selection = dirs[i - 1]
	print()
	return selection

# List the files with a regular expression
def listFiles(regex, directory = ''):
	path = os.path.join(os.curdir, directory)
	return [os.path.join(path, file) for file in os.listdir(path) if os.path.isfile(os.path.join(path, file)) and bool(re.match(regex, file))]

def header():
	line = 'Timestamp,'
	line += 'Timestamp (s),'
	line += 'Handshake duration (s),'
	line += 'Handshake size (B),'
	line += 'Number of packets,'
	line += 'Number of TCP packets,'
	line += 'Number of Bitcoin packets,'
	line += 'Time of VERSION 1 (s),'
	line += 'Time of VERSION 2 (s),'
	line += 'Time of VERACK 1 (s),'
	line += 'Time of VERACK 2 (s),'
	line += 'VERSION 1 size (B),'
	line += 'VERSION 2 size (B),'
	line += 'VERACK 1 size (B),'
	line += 'VERACK 2 size (B),'
	return line

inputFileName = selectFile('.*_parsed\.csv', False)
outputFileName = inputFileName[:-5] + '_handshake.csv'

print()
print('Opening', inputFileName)
inputFile = open(inputFileName, 'r')
reader = csv.reader(inputFile)
temp_header = next(reader)

print('Opening', outputFileName)
outputFile = open(outputFileName, 'w')
outputFile.write(header() + '\n')

handshake_tcp_count = 0
handshake_total_size = 0
handshake_total_packets = 0
handshake_total_tcp_packets = 0
handshake_total_bitcoin_packets = 0
handshake_end_timestamp = 0
handshake_versions = []
handshake_veracks = []
handshake_count = 0

ip_distribution = {}

rows = []
for row in reader:
	rows.append(row)
	source_ip = row[3].split(':')[0]
	destination_ip = row[4].split(':')[0]
	if source_ip not in ip_distribution:
		ip_distribution[source_ip] = 1
	else: ip_distribution[source_ip] += 1
	if destination_ip not in ip_distribution:
		ip_distribution[destination_ip] = 1
	else: ip_distribution[destination_ip] += 1

ip_distribution = dict(sorted(ip_distribution.items(), key=lambda item: item[1], reverse=True))
experiment_ips = [[*ip_distribution][0], [*ip_distribution][1]]
print(f'Number of packets stored in memory={len(rows)}')
print(f'Experiment IP addresses: {experiment_ips}')
time.sleep(5)

for i, row in enumerate(rows):
	timestamp = row[0]
	timestamp_seconds = float(row[1])
	assert timestamp_seconds > 0, 'Error: Timestamp cannot be zero.'
	protocol = row[2]
	source = row[3]
	destination = row[4]
	source_ip = source.split(':')[0]
	destination_ip = destination.split(':')[0]
	size = int(row[5])
	command = row[6]

	# Only process our IP addresses, all other IPs (hopefully there are none) get ignored
	if source_ip not in experiment_ips: continue
	if destination_ip not in experiment_ips: continue

	# Only process Bitcoin version/verack messages
	# if command != 'version' and command != 'verack': continue

	if protocol == 'TCP':
		handshake_tcp_count += 1
	
	if protocol == 'BITCOIN':
		if command == 'version':
			# If a verack was received, something is off, restart the handshake
			if len(handshake_veracks) > 0:
				handshake_versions = []

			handshake_versions.append([timestamp_seconds, size, handshake_total_size, handshake_total_packets, handshake_total_tcp_packets, handshake_total_bitcoin_packets])
			while len(handshake_versions) > 2: # Only remember the latest two
				handshake_versions.pop(0)
			handshake_veracks = []

		elif command == 'verack':
			if len(handshake_versions) != 2: continue
			handshake_veracks.append([timestamp_seconds, size])
			while len(handshake_veracks) > 2: # Only remember the latest two
				handshake_veracks.pop(0)

	if len(handshake_versions) > 1: # Handshake has started, so log the data
		handshake_total_size += size
		handshake_total_packets += 1
		if protocol == 'TCP': handshake_total_tcp_packets += 1
		else: handshake_total_bitcoin_packets += 1

	if len(handshake_versions) == 2 and len(handshake_veracks) == 2:
		if i + 1 < len(rows):
			nextRow = rows[i + 1]
			handshake_end_timestamp = float(nextRow[1])
		else:
			handshake_end_timestamp = handshake_verack_2_timestamp
		line = f'{timestamp},'
		line += f'{timestamp_seconds},'
		line += f'{handshake_end_timestamp - handshake_versions[0][0]},'
		line += f'{handshake_total_size - handshake_versions[0][2]},'
		line += f'{handshake_total_packets - handshake_versions[0][3]},'
		line += f'{handshake_total_tcp_packets - handshake_versions[0][4]},'
		line += f'{handshake_total_bitcoin_packets - handshake_versions[0][5]},'
		line += f'{handshake_versions[0][0] - handshake_versions[0][0]},'
		line += f'{handshake_versions[1][0] - handshake_versions[0][0]},'
		line += f'{handshake_veracks[0][0] - handshake_versions[0][0]},'
		line += f'{handshake_veracks[1][0] - handshake_versions[0][0]},'
		line += f'{handshake_versions[0][1]},'
		line += f'{handshake_versions[1][1]},'
		line += f'{handshake_veracks[0][1]},'
		line += f'{handshake_veracks[1][1]},'
		outputFile.write(line + '\n')

		# Reset all the handshake data for the next handshake
		handshake_tcp_count = 0
		handshake_total_size = 0
		handshake_total_packets = 0
		handshake_total_tcp_packets = 0
		handshake_total_bitcoin_packets = 0
		handshake_end_timestamp = 0
		handshake_versions = []
		handshake_veracks = []

		# Increment the handshake counter
		handshake_count += 1
		if handshake_count % 10 == 0:
			print('Processing handshake', handshake_count)

print(f'Saved to "{outputFileName}".')

inputFile.close()
outputFile.close()

print('Goodbye.')
sys.exit()