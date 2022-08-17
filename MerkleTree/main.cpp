

#include <filesystem>
#include <string>
#include <vector>
#include <iostream>
#include <regex>

using namespace std;
namespace fs = std::filesystem;

class MerkleTree {
public:
	bool generatedHash = false;
	string hash = "";

	MerkleTree() {
		cout << "Init" << endl;
	}

	string getHash() {
		if(!generatedHash) {
			generateHash();
		}
		return hash;
	}

	void generateHash() {

	}

};

vector<string> getFiles(string directory) {
	vector<string> files;

	for(fs::recursive_directory_iterator i(".."), end; i != end; ++i) 
		if(!is_directory(i->path()))
			//string file=
			if(regex_match())
			//cout << i->path().filename() << "\n";
			files.push_back(i->path());

	return files;
}

int main() {
	cout << "Hello world" << endl;

	vector<string> files = getFiles("..");
	for(int i = 0; i < files.size(); i++)
		cout << files[i] << endl;

	MerkleTree tree;
	return 0;
}