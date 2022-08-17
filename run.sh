#!/bin/bash
# ./run.sh
# ./run.sh gui
# ./run.sh gui -debug=handshakeproof

params=""
if [[ $1 == -* ]] ; then
	params="$params $1"
fi
if [[ $2 == -* ]] ; then
	params="$params $2"
fi
if [[ $3 == -* ]] ; then
	params="$params $3"
fi
if [[ $4 == -* ]] ; then
	params="$params $4"
fi
if [[ $5 == -* ]] ; then
	params="$params $5"
fi

echo "Parameters to transfer to Bitcoin: \"$params\""
#exit 1

if [ ! -d "src" ] ; then
	cd .. # If located in src or any other level of depth 1, return
fi

pruned="false"
if [ -d "/media/sf_Bitcoin/blocks/" ] && [ ! -f "/media/sf_Bitcoin/bitcoind.pid" ] ; then
	dir="/media/sf_Bitcoin"
elif [ -d "/media/sf_BitcoinAttacker/blocks/" ] && [ ! -f "/media/sf_BitcoinAttacker/bitcoind.pid" ] ; then
	dir="/media/sf_BitcoinAttacker"
elif [ -d "/media/sf_BitcoinVictim/blocks/" ] && [ ! -f "/media/sf_BitcoinVictim/bitcoind.pid" ] ; then
	dir="/media/sf_BitcoinVictim"
elif [ -d "/media/sim/BITCOIN/blocks/" ] && [ ! -f "/media/sim/BITCOIN/bitcoind.pid" ] ; then
	dir="/media/sim/BITCOIN"
elif [ -d "/media/ubuntu1/Blockchains/Bitcoin/blocks/" ] && [ ! -f "/media/ubuntu1/Blockchains/Bitcoin/bitcoind.pid" ] ; then
	dir="/media/ubuntu1/Blockchains/Bitcoin"

# 5k full node
elif [ -d "/media/research/Long Term Storage/Bitcoin/blocks/" ] && [ ! -f "/media/research/Long Term Storage/Bitcoin/bitcoind.pid" ] ; then
	dir="/media/research/Long Term Storage/Bitcoin"


# For running multiple nodes on the same machine
elif [ -d "$HOME/.bitcoin/blocks/" ] && [ -f "$HOME/.bitcoin/bitcoind.pid" ] && 
	 [ -d "$HOME/.bitcoin2/blocks/" ] && [ ! -f "$HOME/.bitcoin2/bitcoind.pid" ] ; then
	dir="$HOME/.bitcoin2"
	pruned="true"
elif [ -d "$HOME/.bitcoin/blocks/" ] && [ -f "$HOME/.bitcoin/bitcoind.pid" ] && 
	 [ -d "$HOME/.bitcoin2/blocks/" ] && [ -f "$HOME/.bitcoin2/bitcoind.pid" ] && 
	 [ -d "$HOME/.bitcoin3/blocks/" ] && [ ! -f "$HOME/.bitcoin3/bitcoind.pid" ] ; then
	dir="$HOME/.bitcoin3"
	pruned="true"
elif [ -d "$HOME/.bitcoin/blocks/" ] && [ -f "$HOME/.bitcoin/bitcoind.pid" ] && 
	 [ -d "$HOME/.bitcoin2/blocks/" ] && [ -f "$HOME/.bitcoin2/bitcoind.pid" ] && 
	 [ -d "$HOME/.bitcoin3/blocks/" ] && [ -f "$HOME/.bitcoin3/bitcoind.pid" ] && 
	 [ -d "$HOME/.bitcoin4/blocks/" ] && [ ! -f "$HOME/.bitcoin4/bitcoind.pid" ] ; then
	dir="$HOME/.bitcoin4"
	pruned="true"

else
	dir="$HOME/.bitcoin"
	pruned="true"

	if [ ! -d "$dir" ] ; then
		mkdir "$dir"
	fi
fi

if [ -f "$dir/bitcoind.pid" ] ; then
	echo "The directory \"$dir\" has bitcoind.pid, meaning that Bitcoin is already running. In order to ensure that the blockchain does not get corrupted, the program will now terminate."
	exit 1
fi

echo "datadir = $dir"

rpcport=8332
port=8333
echo "Checking ports..."
while [[ $(lsof -i:$port) ]] | [[ $(lsof -i:$rpcport) ]]; do
	echo "port: $port, rpcport: $rpcport, ALREADY CLAIMED"
	rpcport=$((rpcport+2))
	port=$((port+2))
done
echo "port: $port, rpcport: $rpcport, SELECTED"

if [ ! -f "$dir/bitcoin.conf" ] ; then #| [ port != 8333 ] ; then
	echo "Resetting configuration file"
	echo "server=1" > "$dir/bitcoin.conf"
	echo "rpcuser=cybersec" >> "$dir/bitcoin.conf"
	echo "rpcpassword=kZIdeN4HjZ3fp9Lge4iezt0eJrbjSi8kuSuOHeUkEUbQVdf09JZXAAGwF3R5R2qQkPgoLloW91yTFuufo7CYxM2VPT7A5lYeTrodcLWWzMMwIrOKu7ZNiwkrKOQ95KGW8kIuL1slRVFXoFpGsXXTIA55V3iUYLckn8rj8MZHBpmdGQjLxakotkj83ZlSRx1aOJ4BFxdvDNz0WHk1i2OPgXL4nsd56Ph991eKNbXVJHtzqCXUbtDELVf4shFJXame" >> "$dir/bitcoin.conf"
	echo "port=$port" >> "$dir/bitcoin.conf"
	echo "rpcport=$rpcport" >> "$dir/bitcoin.conf"
	#echo "rpcallowip=0.0.0.0/0" >> "$dir/bitcoin.conf"
	#echo "rpcbind = 0.0.0.0:8332" >> "$dir/bitcoin.conf"
	#echo "upnp=1" >> "$dir/bitcoin.conf"
	echo "listen=1" >> "$dir/bitcoin.conf"
fi

if [ "$1" == "gui" ] ; then
	if [ "$pruned" == "true" ] ; then
		echo "Pruned mode activated, only keeping 550 block transactions"
		echo
		src/qt/bitcoin-qt -prune=550 -datadir="$dir" $params #-debug=handshakeproof
	else
		echo
		src/qt/bitcoin-qt -datadir="$dir" $params #-debug=handshakeproof
	fi
else

	# Only open the console if not already open
	if ! wmctrl -l | grep -q "Custom Bitcoin Verack++ Console" ; then
		# Find the right terminal
		if [ -x "$(command -v mate-terminal)" ] ; then
			mate-terminal -t "Custom Bitcoin Verack++ Console" -- python3 bitcoin_console.py
		elif [ -x "$(command -v xfce4-terminal)" ] ; then
			xfce4-terminal -t "Custom Bitcoin Verack++ Console" -- python3 bitcoin_console.py
		else
			gnome-terminal -t "Custom Bitcoin Verack++ Console" -- python3 bitcoin_console.py
		fi
	fi

	if [ "$pruned" == "true" ] ; then
		echo "Pruned mode activated, only keeping 550 block transactions"
		echo
		src/bitcoind -prune=550 -datadir="$dir" $params -debug=handshakeproof #-reindex-chainstate
	else
		echo
		src/bitcoind -datadir="$dir" -txindex=1 $params -debug=handshakeproof
		# Reindexing the chainstate:
		#src/bitcoind -datadir="/media/sf_Bitcoin" -debug=handshakeproof -reindex-chainstate
		
		# Reindexing the transaction index database
		#src/bitcoind -datadir="$dir" -txindex=1 -reindex $params -debug=handshakeproof
	fi
fi
