rm -rf main
g++-11 -g --std=c++17 main.cpp -o main -lssl -lcrypto

./main