rm -rf src/bitcoind
rm -rf src/bitcoin-cli

make -j$(nproc)
./run.sh
