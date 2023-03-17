import os
import json
import time
import subprocess

numSamples = 100000

def bitcoin(cmd):
	result = os.popen(f'src/bitcoin-cli {cmd}').read()
	if result.startswith('Loading block index'):
		time.sleep(10)
	return result

def terminal(cmd):
	return os.popen(cmd).read()

def isBitcoinUp():
	return winexists('Custom Bitcoin Core Instance')

def winexists(target):
	for line in subprocess.check_output(['wmctrl', '-l']).splitlines():
		window_name = line.split(None, 3)[-1].decode()
		if window_name == target:
			return True
	return False

def isTcpdumpUp():
	process = terminal('ps -A | grep tcpdump')
	return process != ''

def startTcpDump():
	subprocess.Popen(['gnome-terminal -t "Bitcoin TCPDUMP Logger" -- python3 MerkleTree/pcap_experiment/log_bitcoin_pcaps.py'], shell=True)

def connectNode(address = '10.0.2.4'):
	bitcoin('addnode ' + address + ' onetry')

def disconnectNodes():
	peerinfo = json.loads(bitcoin('getpeerinfo'))
	for peer in peerinfo:
		address = peer['addr']
		print('Disconnecting ' + address)
		bitcoin('disconnectnode ' + address)

def getConnectionCount():
	try:
		return int(bitcoin('getconnectioncount'))
	except:
		return 0

for i in range(numSamples):
	if not isTcpdumpUp():
		startTcpDump()

	if not isBitcoinUp():
		print('Restarting the node...')
		terminal('rm -rf ~/.bitcoin/bitcoind.pid')
		subprocess.Popen(['gnome-terminal -t "Custom Bitcoin Core Instance" -- bash ./run.sh nogui'], shell=True)
		time.sleep(10)

	print('Sample number', i + 1)
	while(isBitcoinUp() and getConnectionCount() == 0):
		connectNode()
		time.sleep(0.5)

	while(isBitcoinUp() and getConnectionCount() > 0):
		disconnectNodes()
		time.sleep(0.3)
