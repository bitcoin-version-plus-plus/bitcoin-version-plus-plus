#include <filesystem>
#include <fstream>
#include <string>
#include <vector>
#include <iostream>
#include <regex>
#include <math.h>
#include <assert.h>

using namespace std;
namespace fs = std::filesystem;

class MerkleTreeNode {
public:
	string name = "";
	string value;
	MerkleTreeNode* leftNode;
	MerkleTreeNode* rightNode;
	MerkleTreeNode* parent;

	// ToString
	friend ostream& operator<<(std::ostream &strm, const MerkleTreeNode &node) {
		return strm << "Node(" << node.value << ", " << node.leftNode << ", " << node.rightNode << ", " << node.parent << ")";
	}

	// Constructor
	MerkleTreeNode(string _value = "", MerkleTreeNode* _leftNode = NULL, MerkleTreeNode* _rightNode = NULL, MerkleTreeNode* _parent = NULL, string _name = "")
		: value(_value),
		leftNode(_leftNode),
		rightNode(_rightNode),
		parent(_parent),
		name(_name) {
		cout << "Creating " << name << endl;
	}

	// Destructor
	~MerkleTreeNode() {
		cout << "Deleting " << name << endl;
		// if(leftNode != NULL)
		// 	if(leftNode->value == "")
		// 		delete leftNode;
		// if(rightNode != NULL)
		// 	if(rightNode->value == "")
		// 		delete rightNode;
		if(leftNode != NULL) delete leftNode;
		if(rightNode != NULL) delete rightNode;
		// delete parent;
	}

	MerkleTreeNode& operator=(MerkleTreeNode const& other) {
		cout << "Setting " << name << endl;
		if(this == &other) return *this;
		value = other.value;
		leftNode = other.leftNode;
		rightNode = other.rightNode;
		parent = other.parent;
		return *this;
	}
};



class MerkleTree {

private:

	int nextPowerOfTwo(int num) {
		double n = log2(num);
		return (int)pow(2, ceil(n));
	}

public:
	vector<MerkleTreeNode> leafNodes;
	vector<vector<MerkleTreeNode>> treeNodes;
	MerkleTreeNode root;

	bool generatedHash = false;
	string hash = "";

	MerkleTree() {
		cout << "Init" << endl;
	}

	static string computeHash(string input) {
		string output = "";
		output += "12345";
		return output;
	}

	void initialize(vector<string> leaves) {
		// Adjust hash vector to be a power of two
		int targetSize = nextPowerOfTwo(leaves.size()), i = 0;
		while(leaves.size() < targetSize) {
			leaves.push_back(leaves.at(i));
			i++;
		}
		fillTree(leaves);
	}

	// Recursively halves the size of the vector until the vector only has the root
	// vector<MerkleTreeNode*> _fillTree(vector<MerkleTreeNode*> nodes) {

	// 	// for(int i = 0; i < nodes.size(); i ++) {
	// 	// 	cout << &nodes[i] << nodes[i] << " ";
	// 	// }
	// 	// cout << endl;

		

	// 	return _fillTree(newNodes);
	// }

	void fillTree(vector<string> values) {
		leafNodes.clear();
		for(int i = 0; i < values.size(); i++) {
			MerkleTreeNode node(values.at(i));
			node.name = "Initial leaf node";
			leafNodes.push_back(node);
		}

		cout << "Setting tree to leaf nodes" << endl;
		vector<MerkleTreeNode> tree = leafNodes;
		// for(int i = 0; i < leafNodes.size(); i++) {
		// 	tree.push_back(&leafNodes.at(i));
		// }

		// Iteratively construct the tree
		int level = 1;
		while(tree.size() >= 2) {
			vector<MerkleTreeNode> newNodes;

			// Every two nodes will become children to the new node
			for(int i = 0; i < tree.size(); i += 2) {
				string value = computeHash(tree.at(i).value + tree.at(i + 1).value);

				MerkleTreeNode newNode(value, &tree.at(i), &tree.at(i + 1), NULL, "Node at level " + to_string(level));
				newNodes.push_back(newNode);
				tree.at(i).parent = &newNode;
				tree.at(i + 1).parent = &newNode;

			}

			//cout << "b4 " << tree[1] << endl;
			treeNodes.push_back(newNodes);
			tree = treeNodes.back();

			//cout << "af " << tree[0].rightNode << endl;
			//cout << "* " << *(tree[0].rightNode) << endl;
			level++;

		}

		assert(tree.size() == 1);
		root = tree.at(0);
		// root.value = tree[0].value;
		// root.leftNode = tree[0].leftNode;
		// root.rightNode = tree[0].rightNode;
		// root.parent = tree[0].parent;

		hash = root.value;
	}

	void printTree(MerkleTreeNode node, int depth = 0) {
		cout << "    Depth: " << depth << " " << " " << node << endl;
		if(node.leftNode == NULL || node.rightNode == NULL) {
			cout << "FOUND LEAF" << endl;
			cout << node.value << endl;
			//return;
		}


		if(depth > 15) return;

		// if(node.leftNode != NULL) printTree(*node.leftNode, depth + 1);
		// if(node.rightNode != NULL) printTree(*node.rightNode, depth + 1);

		if(node.leftNode != NULL) {
			cout << "Going left " << endl;
			printTree(*node.leftNode, depth + 1);
		}
		if(node.rightNode != NULL) {
			cout << "Going right " << endl;
			printTree(*node.rightNode, depth + 1);
		}
	}

};

// Recursively list the files in a directory
vector<string> getFiles(string directory, string regexStr) {
	vector<string> files;
	for(fs::recursive_directory_iterator i(".."), end; i != end; ++i) {
		if(!is_directory(i->path())) {
			string str = i->path();
			if(regex_match(str, regex(regexStr))) {
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

int main() {
	cout << "Hello world" << endl;
	MerkleTree tree;

	// Get the list of code file names
	vector<string> files = getFiles("..", ".*(\\.cpp|\\.c|\\.h|\\.cc|\\.py|\\.sh)");
	vector<string> hashes (4);
	// vector<string> hashes (files.size());
	// // Compute the hash of the files
	// for(int i = 0; i < files.size(); i++) {
	// 	hashes.at(i) = tree.computeHash(getContents(files[i]));
	// }
	for(int i = 0; i < 4; i++) { // TEMP
		hashes.at(i) = to_string(i + 1);
	}
	

	tree.initialize(hashes);
	cout << "Hash: " << tree.hash << endl;

	cout << "Testing left..." << endl;
	MerkleTreeNode templ = tree.root;
	while(templ.leftNode != NULL) {
		cout << "Root: " << &templ << " left " << templ.leftNode << " right " << templ.rightNode << endl;
		templ = *(templ.leftNode);
	}
	cout << "Found leftmost leaf: " << templ << endl;

	cout << "Testing right..." << endl;
	MerkleTreeNode tempr = tree.root;
	while(tempr.leftNode != NULL) {
		cout << "Root: " << &tempr << " left " << tempr.leftNode << " right " << tempr.rightNode << endl;
		tempr = *(tempr.leftNode);
	}
	cout << "Found rightmost leaf: " << tempr << endl;

	cout << "\nPrinting..." << endl;
	tree.printTree(tree.root);
	return 0;
}