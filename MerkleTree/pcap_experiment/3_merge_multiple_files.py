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
	#while selection is None:
	try:
		i = int(input(f'Please select a file (1 to {len(files)}): '))
	except KeyboardInterrupt:
		sys.exit()
	except:
		i = 0
	if i > 0 and i <= len(files):
		selection = files[i - 1]
	else:
		selection = ''
	print()
	return selection


selections = []
selection = selectFile(r'.*_handshake\.csv')
while selection != '':
	selections.append(selection)
	print(f'Print selected file {len(selections)}. Type "" to proceed with the merge.')
	selection = selectFile(r'.*_handshake\.csv')

outputFileName = 'MERGED_HANDSHAKES.csv'
output = open(outputFileName, 'w')

for i, inputFileName in enumerate(selections):
	print(f'Merging in "{inputFileName}".')
	file = open(inputFileName, 'r')
	contents = file.read()
	if i > 0 and inputFileName.endswith('.csv'):
		print('Removing the header from the CSV file...')
		lines = contents.lstrip().split('\n')
		print('Header:', lines[0])
		lines.pop(0)
		contents = '\n'.join(lines)
	output.write(contents)
	file.close()
output.close()
print()
print(f'Successfully wrote to "{outputFileName}".')
print()