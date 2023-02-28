# Copy this script to the desktop before running
if [[ "$PWD" = "/home/${USER}/Desktop" ]]; then
    rm -rf bitcoin-version-plus-plus
    git clone https://github.com/bitcoin-version-plus-plus/bitcoin-version-plus-plus.git
    cd bitcoin-version-plus-plus
    cp /media/sf_Shared_Folder/minisketch/ src/ -r
    ./first_compile.sh
else
    echo "Put this script on the Desktop, then execute it."
fi
