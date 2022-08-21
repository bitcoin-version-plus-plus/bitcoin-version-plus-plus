# Copy this script to the desktop before running
if [[ "$PWD" = "/home/${USER}/Desktop" ]]; then
    rm -rf bitcoin-verack-plus-plus
    git clone https://github.com/bitcoin-verack-plus-plus/bitcoin-verack-plus-plus.git
    cd bitcoin-verack-plus-plus
    cp /media/sf_Shared_Folder/minisketch/ src/ -r
    ./first_compile.sh
else
    echo "Put this script on the Desktop, then execute it."
fi