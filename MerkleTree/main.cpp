using namespace std;

#include <filesystem>
#include <string>
#include <iostream>

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

int main() {
	cout << "Hello world" << endl;
	
	std::filesystem::path cwd = std::filesystem::current_path() / "filename.txt";
	std::ofstream file(cwd.string());
	file.close();
	cout << buffer << endl;

	MerkleTree tree;
	return 0;
}