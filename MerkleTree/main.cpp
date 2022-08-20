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

// Computes the SHA-256 hash of a string
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

// Given a number (e.g. 10) compute the next power of two (e.g. 16)
int nextPowerOfTwo(int num) {
	double n = log2(num);
	return (int)pow(2, ceil(n));
}

// Update the hash at an index within the tree
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