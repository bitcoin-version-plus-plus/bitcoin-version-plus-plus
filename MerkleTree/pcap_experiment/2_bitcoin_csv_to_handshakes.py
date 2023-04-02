import csv
import os
import re
import sys
import time

handshake_cutoff = 45000 # 0 for no cutoff

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
	line += 'Versions duration (s),'
	line += 'Versions size (B),'
	line += 'Versions number of packets,'
	line += 'Versions number of TCP packets,'
	line += 'Versions number of Bitcoin packets,'
	line += 'Versions Bitcoin message distribution,'
	line += 'Versions probabilities of Bitcoin message,'
	line += 'Veracks duration (s),'
	line += 'Veracks size (B),'
	line += 'Veracks number of packets,'
	line += 'Veracks number of TCP packets,'
	line += 'Veracks number of Bitcoin packets,'
	line += 'Veracks Bitcoin message distribution,'
	line += 'Veracks probabilities of Bitcoin message,'
	line += 'SendCMPCTs duration (s),'
	line += 'SendCMPCTs size (B),'
	line += 'SendCMPCTs number of packets,'
	line += 'SendCMPCTs number of TCP packets,'
	line += 'SendCMPCTs number of Bitcoin packets,'
	line += 'SendCMPCTs Bitcoin message distribution,'
	line += 'SendCMPCTs probabilities of Bitcoin message,'
	line += 'VERSION 1 size (B),'
	line += 'VERSION 2 size (B),'
	return line

inputFileName = selectFile('.*_parsed\.csv', True)
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
handshake_bitcoin_messages = {}
versions_bitcoin_message_probabilities = {}
veracks_bitcoin_message_probabilities = {}
sendcmpct_bitcoin_message_probabilities = {}
handshake_versions = []
handshake_veracks = []
sendheaders_received = 0
sendcmpct_received = 0

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
		commands = command.split()
		for c in commands:
			if c not in handshake_bitcoin_messages:
				handshake_bitcoin_messages[c] = 1
			else:
				handshake_bitcoin_messages[c] += 1

		if 'version' in command:
			handshake_versions.append([timestamp_seconds, size, handshake_total_size, handshake_total_packets, handshake_total_tcp_packets, handshake_total_bitcoin_packets, handshake_bitcoin_messages.copy()])
			while len(handshake_versions) > 2: # Only remember the latest two
				handshake_versions.pop(0)
			handshake_veracks = []
			sendheaders_received = 0
			sendcmpct_received = 0

		if 'verack' in command:
			handshake_veracks.append([timestamp_seconds, size, handshake_total_size, handshake_total_packets, handshake_total_tcp_packets, handshake_total_bitcoin_packets, handshake_bitcoin_messages.copy()])
			while len(handshake_veracks) > 2: # Only remember the latest two
				handshake_veracks.pop(0)

		if 'sendheaders' in command:
			sendheaders_received += 1

		if 'sendcmpct' in command:
			sendcmpct_received += 1

	if len(handshake_versions) > 1: # Handshake has started, so log the data
		handshake_total_size += size
		handshake_total_packets += 1
		if protocol == 'TCP': handshake_total_tcp_packets += 1
		else: handshake_total_bitcoin_packets += 1

	handshake_is_complete = False
	if len(handshake_versions) >= 2 and len(handshake_veracks) >= 2:
		if i + 1 == len(rows): handshake_is_complete = True
		elif 'version' in rows[i + 1][6].split(): handshake_is_complete = True
		elif sendheaders_received >= 2 and sendcmpct_received >= 2: handshake_is_complete = True

	if handshake_is_complete:
		starting_baseline_bitcoin_messages = handshake_versions[0][6].copy()
		if starting_baseline_bitcoin_messages['version'] > 0:
			# The initial version should not be subtracted from the total, so remove it early
			starting_baseline_bitcoin_messages['version'] -= 1
		version_bitcoin_messages = handshake_versions[1][6]
		verack_bitcoin_messages = handshake_veracks[1][6]
		sendcmpct_bitcoin_messages = handshake_bitcoin_messages.copy()

		for c in starting_baseline_bitcoin_messages: # Only count when the handshake began
			version_bitcoin_messages[c] -= starting_baseline_bitcoin_messages[c]
			verack_bitcoin_messages[c] -= starting_baseline_bitcoin_messages[c]
			sendcmpct_bitcoin_messages[c] -= starting_baseline_bitcoin_messages[c]

			if version_bitcoin_messages[c] <= 0: del version_bitcoin_messages[c]
			if verack_bitcoin_messages[c] <= 0: del verack_bitcoin_messages[c]
			if sendcmpct_bitcoin_messages[c] <= 0: del sendcmpct_bitcoin_messages[c]


		# Construct the message probabilities
		for c in version_bitcoin_messages:
			if c not in versions_bitcoin_message_probabilities:
				versions_bitcoin_message_probabilities[c] = 0
			versions_bitcoin_message_probabilities[c] += version_bitcoin_messages[c]
		for c in verack_bitcoin_messages:
			if c not in veracks_bitcoin_message_probabilities:
				veracks_bitcoin_message_probabilities[c] = 0
			veracks_bitcoin_message_probabilities[c] += verack_bitcoin_messages[c]
		for c in sendcmpct_bitcoin_messages:
			if c not in sendcmpct_bitcoin_message_probabilities:
				sendcmpct_bitcoin_message_probabilities[c] = 0
			sendcmpct_bitcoin_message_probabilities[c] += sendcmpct_bitcoin_messages[c]

		versions_probs = {}
		veracks_probs = {}
		sendcmpct_probs = {}
		for c in versions_bitcoin_message_probabilities:
			versions_probs[c] = versions_bitcoin_message_probabilities[c] / (handshake_count + 1)
		for c in veracks_bitcoin_message_probabilities:
			veracks_probs[c] = veracks_bitcoin_message_probabilities[c] / (handshake_count + 1)
		for c in sendcmpct_bitcoin_message_probabilities:
			sendcmpct_probs[c] = sendcmpct_bitcoin_message_probabilities[c] / (handshake_count + 1)

		version_bitcoin_messages = dict(sorted(version_bitcoin_messages.items(), key=lambda item: item[1], reverse=True))
		verack_bitcoin_messages = dict(sorted(verack_bitcoin_messages.items(), key=lambda item: item[1], reverse=True))
		sendcmpct_bitcoin_messages = dict(sorted(sendcmpct_bitcoin_messages.items(), key=lambda item: item[1], reverse=True))

		"""
line = 'Timestamp,'
line += 'Timestamp (s),'
line += 'Versions duration (s),'
line += 'Versions size (B),'
line += 'Versions number of packets,'
line += 'Versions number of TCP packets,'
line += 'Versions number of Bitcoin packets,'
line += 'Versions Bitcoin message distribution,'
line += 'Versions probabilities of Bitcoin message,'
line += 'Veracks duration (s),'
line += 'Veracks size (B),'
line += 'Veracks number of packets,'
line += 'Veracks number of TCP packets,'
line += 'Veracks number of Bitcoin packets,'
line += 'Veracks Bitcoin message distribution,'
line += 'Veracks probabilities of Bitcoin message,'
line += 'SendCMPCTs duration (s),'
line += 'SendCMPCTs size (B),'
line += 'SendCMPCTs number of packets,'
line += 'SendCMPCTs number of TCP packets,'
line += 'SendCMPCTs number of Bitcoin packets,'
line += 'SendCMPCTs Bitcoin message distribution,'
line += 'SendCMPCTs probabilities of Bitcoin message,'
line += 'VERSION 1 size (B),'
line += 'VERSION 2 size (B),'
		"""
		line = f'{timestamp},'
		line += f'{timestamp_seconds},'

		# VERSIONs
		line += f'{handshake_versions[1][0] - handshake_versions[0][0]},' # Duration (s)
		line += f'{handshake_versions[1][2] - handshake_versions[0][2]},' # Size (B),
		line += f'{handshake_versions[1][3] - handshake_versions[0][3]},' # Number of packets
		line += f'{handshake_versions[1][4] - handshake_versions[0][4]},' # Number of TCP packets
		line += f'{handshake_versions[1][5] - handshake_versions[0][5]},' # Number of Bitcoin packets
		line += f'"{version_bitcoin_messages}",' # Bitcoin message distribution
		line += f'"{versions_probs}",' # Bitcoin message distribution probability

		# VERACKs
		line += f'{handshake_veracks[1][0] - handshake_versions[0][0]},' # Duration (s)
		line += f'{handshake_veracks[1][2] - handshake_versions[0][2]},' # Size (B),
		line += f'{handshake_veracks[1][3] - handshake_versions[0][3]},' # Number of packets
		line += f'{handshake_veracks[1][4] - handshake_versions[0][4]},' # Number of TCP packets
		line += f'{handshake_veracks[1][5] - handshake_versions[0][5]},' # Number of Bitcoin packets
		line += f'"{verack_bitcoin_messages}",' # Bitcoin message distribution
		line += f'"{veracks_probs}",' # Bitcoin message distribution probability

		# SENDHEADERS / SENDCMPCTs
		currentState = [timestamp_seconds, size, handshake_total_size, handshake_total_packets, handshake_total_tcp_packets, handshake_total_bitcoin_packets, handshake_bitcoin_messages]
		line += f'{currentState[0] - handshake_versions[0][0]},' # Duration (s)
		line += f'{currentState[2] - handshake_versions[0][2]},' # Size (B),
		line += f'{currentState[3] - handshake_versions[0][3]},' # Number of packets
		line += f'{currentState[4] - handshake_versions[0][4]},' # Number of TCP packets
		line += f'{currentState[5] - handshake_versions[0][5]},' # Number of Bitcoin packets
		line += f'"{sendcmpct_bitcoin_messages}",' # Bitcoin message distribution
		line += f'"{sendcmpct_probs}",' # Bitcoin message distribution probability

		line += f'{handshake_versions[0][1]},'
		line += f'{handshake_versions[1][1]},'
		outputFile.write(line + '\n')

		# Reset all the handshake data for the next handshake
		handshake_tcp_count = 0
		handshake_total_size = 0
		handshake_total_packets = 0
		handshake_total_tcp_packets = 0
		handshake_total_bitcoin_packets = 0
		handshake_end_timestamp = 0
		handshake_bitcoin_messages = {}
		handshake_versions = []
		handshake_veracks = []
		sendheaders_received = 0
		sendcmpct_received = 0

		# Increment the handshake counter
		handshake_count += 1
		if handshake_count % 10 == 0:
			print('Processing handshake', handshake_count)
		if handshake_count >= handshake_cutoff: break

print(f'Saved to "{outputFileName}".')

inputFile.close()
outputFile.close()

print('Goodbye.')
sys.exit()