import datetime
import os
import pyshark
import re
import sys
import time

considerTCP = False
handshakeCutoff = 100000

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
	line = 'Connection Count,'
	line += 'Handshake Duration (s),'
	if considerTCP: line += 'TCP Ending Handshake Timestamp (s),'
	line += 'Version 1 Timestamp (s),'
	line += 'Version 1 Bytes,'
	line += 'Version 2 Timestamp (s),'
	line += 'Version 2 Bytes,'
	line += 'Verack 1 Timestamp (s),'
	line += 'Verack 1 Bytes,'
	line += 'Verack 2 Timestamp (s),'
	line += 'Verack 2 Bytes,'

	return line

connectionCount = 0
handshakeVersionCount = 0
handshakeVerackCount = 0

lastCommand = ''
tcpEndTime = 0
version1t = 0
version1b = 0
version2t = 0
version2b = 0
verack1t = 0
verack1b = 0
verack2t = 0
verack2b = 0

def log(packet, layer):
	global lastCommand, tcpEndTime
	global connectionCount, handshakeVersionCount, handshakeVerackCount
	global version1t, version1b, version2t, version2b
	global verack1t, verack1b, verack2t, verack2b

	timestamp = packet.sniff_time
	timestamp_seconds = (timestamp - datetime.datetime(1970, 1, 1)).total_seconds()
	command = bitcoinLayer.command
	numBytes = packet.length

	#print(command, end=' ')

	if command == 'version':
		if handshakeVerackCount == 0:
			handshakeVersionCount += 1
			if handshakeVersionCount == 1:
				version1t = timestamp_seconds
				version1b = numBytes

			elif handshakeVersionCount == 2:
				version2t = timestamp_seconds
				version2b = numBytes

			else:
				version1t = version2t
				version1b = version2b
				version2t = timestamp_seconds
				version2b = numBytes
		else:
			#print('CORRUPT VERSION, RESETTING HANDSHAKE')
			# Corrupt handshake detected, ignore this handshake
			tcpEndTime = 0
			version1t = 0
			version1b = 0
			version2t = 0
			version2b = 0
			verack1t = 0
			verack1b = 0
			verack2t = 0
			verack2b = 0
			handshakeVersionCount = 0
			handshakeVerackCount = 0
			return


	# Force the versions to be completed before proceeding
	if command == 'verack':
		if handshakeVersionCount >= 2:

			handshakeVerackCount += 1
			if handshakeVerackCount == 1:
				verack1t = timestamp_seconds
				verack1b = numBytes

			elif handshakeVerackCount == 2:
				verack2t = timestamp_seconds
				verack2b = numBytes

			else:
				verack1t = verack2t
				verack1b = verack2b
				verack2t = timestamp_seconds
				verack2b = numBytes
		else:
			#print('CORRUPT VERACK, RESETTING HANDSHAKE')
			# Corrupt handshake detected, ignore this handshake
			tcpEndTime = 0
			version1t = 0
			version1b = 0
			version2t = 0
			version2b = 0
			verack1t = 0
			verack1b = 0
			verack2t = 0
			verack2b = 0
			handshakeVersionCount = 0
			handshakeVerackCount = 0
			return


	if handshakeVersionCount >= 2 and handshakeVerackCount >= 2:
		if connectionCount % 100 == 0:
			print('Processed connection', connectionCount)
		handshakeVersionCount = 0
		handshakeVerackCount = 0
		connectionCount += 1
		if considerTCP:
			handshakeDuration = max(tcpEndTime, version1t, version2t, verack1t, verack2t) - min(tcpEndTime, version1t, version2t, verack1t, verack2t)
			line = f'{connectionCount},{handshakeDuration},{tcpEndTime},{version1t},{version1b},{version2t},{version2b},{verack1t},{verack1b},{verack2t},{verack2b}'
		else:
			handshakeDuration = max(version1t, version2t, verack1t, verack2t) - min(version1t, version2t, verack1t, verack2t)
			line = f'{connectionCount},{handshakeDuration},{version1t},{version1b},{version2t},{version2b},{verack1t},{verack1b},{verack2t},{verack2b}'


		file.write(line + '\n')
		
		tcpEndTime = 0

	lastCommand = command


pcapName = selectFile('.*\.pcap', False) #'bitcoin_pcap_handshake_log.pcap'


print('\nOpening', pcapName)
if considerTCP:
	fileName = pcapName[:-5] + '_parsed.csv'
else:
	fileName = pcapName[:-5] + '_parsed_notcp.csv'

outputFile = open(fileName, 'w', newline='')

file = open(fileName, 'w+')
file.write(header() + '\n')

pcap = pyshark.FileCapture(pcapName)

for packet in pcap:
	if connectionCount > handshakeCutoff:
		print('Reached handshake cutoff')
		break

	tcpLayer = None
	bitcoinLayer = None
	for i, layer in enumerate(packet.layers):
		if layer._layer_name == 'bitcoin':
			bitcoinLayer = layer
		elif layer._layer_name == 'tcp':
			tcpLayer = layer

	if tcpLayer is not None:
		if tcpLayer.flags == '0x00000018':
			timestamp = packet.sniff_time
			timestamp_seconds = (timestamp - datetime.datetime(1970, 1, 1)).total_seconds()
			tcpEndTime = timestamp_seconds

	if bitcoinLayer is None: continue

	if tcpEndTime == 0:
		print('Bitcoin packet before handshake, skipping')
		continue


	command = bitcoinLayer.command

	if command == 'version' or command == 'verack':
		log(packet, bitcoinLayer)


print(f'Saved to "{fileName}".')

pcap.close()
file.close()

print('Goodbye.')
sys.exit()

# import pyshark

# pcap_data = pyshark.FileCapture('WIRESHARK_LOG.pcap')

# for packet in pcap_data:
# 	print(f'Index: {packet.number}')
# 	print(f'Timestamp: {packet.sniff_time}')
# 	print(f'Bytes: {packet.length}')
# 	print(f'Layers: {packet.layers}')

# 	#for layer in packet:
# 	#	if layer.layer_name == 'quic':