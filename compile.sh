#rm -rf src/*.o
#rm -rf src/bitcoind
#rm -rf src/bitcoin-cli

make -j$(nproc)

params=""
for var in "$@"; do
    params="$params $var"
done
./run.sh $params
