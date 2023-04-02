import datetime
import os
import pyshark
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
	line += 'Protocol,'
	line += 'Source,'
	line += 'Destination,'
	line += 'Packet size (B),'
	line += 'Bitcoin Messages,'
	return line

def log(packet):
	timestamp = packet.sniff_time
	timestamp_seconds = (timestamp - datetime.datetime(1970, 1, 1)).total_seconds()
	source_address = packet.ip.src
	source_port = packet[packet.transport_layer].srcport
	source = f'{source_address}:{source_port}'
	destination_address = packet.ip.dst
	destination_port = packet[packet.transport_layer].dstport
	destination = f'{destination_address}:{destination_port}'
	size = packet.length

	tcpLayer = None
	bitcoinLayers = []
	for i, layer in enumerate(packet.layers):
		if layer._layer_name == 'bitcoin':
			bitcoinLayers.append(layer)
		elif layer._layer_name == 'tcp':
			tcpLayer = layer

	command = ''
	protocol = 'TCP'
	if len(bitcoinLayers) > 0:
		protocol = 'BITCOIN'
		for layer in bitcoinLayers:
			command += layer.command + ' '
	command = command.strip()

	line = f'{timestamp},'
	line += f'{timestamp_seconds},'
	line += f'{protocol},'
	line += f'{source},'
	line += f'{destination},'
	line += f'{size},'
	line += f'{command},'
	return line


pcapName = selectFile('.*\.pcap', True)
outputFileName = pcapName[:-5] + '_parsed.csv'

if os.path.exists(outputFileName):
	print()
	print(f'The file "{outputFileName}" already exists.')
	overwrite = input(f'Proceed to overwrite it? (y/n): ').lower() in ['y', 'yes']
	if not overwrite: sys.exit()

print('\nOpening', pcapName)
pcap = pyshark.FileCapture(pcapName)

print('\nOpening', outputFileName)
outputFile = open(outputFileName, 'w', newline='')
file = open(outputFileName, 'w+')
file.write(header() + '\n')

count = 0
for packet in pcap:
	if count % 100 == 0:
		print('Processing packet', count)
	line = log(packet)
	file.write(line + '\n')
	count += 1

print(f'Saved to "{outputFileName}".')

try: pcap.close()
except: pass
file.close()

print('Goodbye.')
sys.exit()