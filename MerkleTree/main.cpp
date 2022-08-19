#include <iostream>
#include <filesystem>
#include <fstream>
#include <vector>
#include <string>
#include <regex>
#include "merklecpp.h"
#include "openssl/sha.h"

using namespace std;
namespace fs = std::filesystem;

string sha256(const string str)
{
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256_CTX sha256;
    SHA256_Init(&sha256);
    SHA256_Update(&sha256, str.c_str(), str.size());
    SHA256_Final(hash, &sha256);
    stringstream ss;
    for(int i = 0; i < SHA256_DIGEST_LENGTH; i++)
    {
        ss << hex << setw(2) << setfill('0') << (int)hash[i];
    }
    return ss.str();
}

// inline uint32_t convert_endianness(uint32_t n){
// 	const uint32_t sz = sizeof(uint32_t);
// 	#if defined(htobe32)
// 	// If htobe32 happens to be a macro, use it.
// 	return htobe32(n);
// 	#elif defined(__LITTLE_ENDIAN__) || defined(__LITTLE_ENDIAN)
// 	// Just as fast.
// 	uint32_t r = 0;
// 	for (size_t i = 0; i < sz; i++)
// 	  r |= ((n >> (8 * ((sz - 1) - i))) & 0xFF) << (8 * i);
// 	return *reinterpret_cast<uint32_t*>(&r);
// 	#else
// 	// A little slower, but works for both endiannesses.
// 	uint8_t r[8];
// 	for (size_t i = 0; i < sz; i++)
// 	  r[i] = (n >> (8 * ((sz - 1) - i))) & 0xFF;
// 	return *reinterpret_cast<uint32_t*>(&r);
// 	#endif
// }

// // clang-format off
// /// @brief SHA256 compression function for tree node hashes
// /// @param l Left node hash
// /// @param r Right node hash
// /// @param out Output node hash
// /// @details This function is the compression function of SHA256, which, for
// /// the special case of hashing two hashes, is more efficient than a full
// /// SHA256 while providing similar guarantees.
// static inline void sha256_compress(const HashT<32> &l, const HashT<32> &r, HashT<32> &out) {
// static const uint32_t constants[] = {
//   0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
//   0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
//   0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
//   0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
//   0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
//   0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
//   0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
//   0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
// };

// uint8_t block[32 * 2];
// memcpy(&block[0], l.bytes, 32);
// memcpy(&block[32], r.bytes, 32);

// static const uint32_t s[8] = { 0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
//                                0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19 };

// uint32_t cws[64] = {0};

// for (int i=0; i < 16; i++)
//   cws[i] = convert_endianness(((int32_t *)block)[i]);

// for (int i = 16; i < 64; i++) {
//   uint32_t t16 = cws[i - 16];
//   uint32_t t15 = cws[i - 15];
//   uint32_t t7 = cws[i - 7];
//   uint32_t t2 = cws[i - 2];
//   uint32_t s1 = (t2 >> 17 | t2 << 15) ^ ((t2 >> 19 | t2 << 13) ^ t2 >> 10);
//   uint32_t s0 = (t15 >> 7 | t15 << 25) ^ ((t15 >> 18 | t15 << 14) ^ t15 >> 3);
//   cws[i] = (s1 + t7 + s0 + t16);
// }

// uint32_t h[8];
// for (int i=0; i < 8; i++)
//   h[i] = s[i];

// for (int i=0; i < 64; i++) {
//   uint32_t a0 = h[0], b0 = h[1], c0 = h[2], d0 = h[3], e0 = h[4], f0 = h[5], g0 = h[6], h03 = h[7];
//   uint32_t w = cws[i];
//   uint32_t t1 = h03 + ((e0 >> 6 | e0 << 26) ^ ((e0 >> 11 | e0 << 21) ^ (e0 >> 25 | e0 << 7))) + ((e0 & f0) ^ (~e0 & g0)) + constants[i] + w;
//   uint32_t t2 = ((a0 >> 2 | a0 << 30) ^ ((a0 >> 13 | a0 << 19) ^ (a0 >> 22 | a0 << 10))) + ((a0 & b0) ^ ((a0 & c0) ^ (b0 & c0)));
//   h[0] = t1 + t2;
//   h[1] = a0;
//   h[2] = b0;
//   h[3] = c0;
//   h[4] = d0 + t1;
//   h[5] = e0;
//   h[6] = f0;
//   h[7] = g0;
// }

// for (int i=0; i < 8; i++)
//   ((uint32_t*)out.bytes)[i] = convert_endianness(s[i] + h[i]);
// }
// // clang-format on

// Recursively list the files in a directory
vector<string> getFiles(string directory, string regexStr, bool ignore_current_directory = true) {
    string current_path = fs::current_path();


	vector<string> files;
	for(fs::recursive_directory_iterator i(".."), end; i != end; ++i) {
		if(!is_directory(i->path())) {
			string str = i->path();
			if(regex_match(str, regex(regexStr))) {

				if(ignore_current_directory) {
					string parent = str.substr(0, str.find_last_of("/\\"));
					if(fs::equivalent(parent, current_path)) {
						continue;
					}
				}

				files.push_back(str);
			}
		}
	}
	return files;
}

// Read the contents of a file at a given file path
string getContents(string filePath) {
	string contents = "";
	ifstream f(filePath);
	while(f) {
		string line;
		getline(f, line);
		contents += line + '\n';
	}
	return contents;
}

int nextPowerOfTwo(int num) {
	double n = log2(num);
	return (int)pow(2, ceil(n));
}

void updateHashAtIndex(merkle::Tree &tree, int index, string hash_string) {
	merkle::TreeT<32, merkle::sha256_compress>::Node* ID = tree.walk_to(index, true, [](merkle::TreeT<32, merkle::sha256_compress>::Node* n, bool go_right) {
		n->dirty = true;
        return true;
    });
    merkle::Tree::Hash newHash(hash_string);
    ID->hash = newHash;
	tree.compute_root();
}


int main() {
	// Get the list of code file names

	vector<string> files = getFiles("..", ".*(\\.cpp|\\.c|\\.h|\\.cc|\\.py|\\.sh)", true);
	vector<string> hashes (files.size());
	// Compute the hash of the files
	for(int i = 0; i < files.size(); i++) {
		hashes.at(i) = sha256(getContents(files[i]));
	}
	// Set the initial ID
	hashes.insert(hashes.begin(), "0000000000000000000000000000000000000000000000000000000000000000");
	// Adjust the size to make it a full binary tree
	int targetSize = nextPowerOfTwo(hashes.size()), i = 0;
	while(hashes.size() < targetSize) {
		hashes.push_back(hashes.at(i));
		i++;
	}

	// Cybersecurity Lab: Testing a mini tree
	// vector<string> hashes (16);
	// for(int i = 0; i < 16; i++) {
	// 	hashes.at(i) = sha256(to_string(i + 1));
	// }




	// Convert the hashes to Merkle node objects
	vector<merkle::Tree::Hash> leaves (hashes.size());
	for(int i = 0; i < hashes.size(); i++) {
		merkle::Tree::Hash hash(hashes.at(i));
		leaves.at(i) = hash;
	}

	// Create the tree
	merkle::Tree tree;
	tree.insert(leaves);

	// Update the ID
	updateHashAtIndex(tree, 0, "0000000000000000000000000000000000000000000000000000000000000000");

	if(tree.root().to_string() == "456efa01e00ba92e05e56253fae45b17de8f1a258b96c4908c1eb5abfb4432b0") {
		cout << "Correct version" << endl;
	} else {
		cout << "Incorrect version: " << tree.root().to_string() << endl;
	}


	// auto root = tree.root();
	// auto path = tree.path(0);
	// assert(path->verify(root));
	return 0;
}