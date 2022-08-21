import os
import json
import time
import re
import readline

numSamples = 100000

def bitcoin(cmd):
	return os.popen(f'src/bitcoin-cli {cmd}').read()

def disconnectNodes():
	peerinfo = json.loads(bitcoin('getpeerinfo'))
	for peer in peerinfo:
		address = peer['addr']
		print('Disconnecting ' + address)
		bitcoin('disconnectnode ' + address)


for i in range(numSamples):
	print('Sample number', i + 1)
	while(int(bitcoin('getconnectioncount')) == 0):
		time.sleep(1)

	while(int(bitcoin('getconnectioncount')) > 0):
		disconnectNodes()
		time.sleep(1)
