import os

def terminal(cmd):
	return os.popen(cmd).read()

print('Beginning tcpdump logger')
terminal(f'sudo tcpdump -w ~/Desktop/bitcoin_pcap_handshake_log.pcap \'port 8333\'')