// This code is created by the Cybersecurity Lab, University of Colorado, Colorado Springs, 2022

#ifndef BITCOIN_HANDSHAKE_PROOF_CPP
#define BITCOIN_HANDSHAKE_PROOF_CPP

#include <iostream>
#include <filesystem>
#include <fstream>
#include <vector>
#include <string>
#include <regex>
#include <inttypes.h>
#include <logging.h>
#include <hash.h>
#include <handshake_proof_merkle.cpp>
//#include <span.h>
//#include <node/context.h>
//#include <sync.h>
//#include <net.h>
//#include "openssl/sha.h"


class HandshakeProof {
    private:
        bool initialized = false;
        merkle_proof::Tree tree;
        std::string merkle_hash = "";

        // Computes the SHA-256 hash of a string
        std::string sha256(const std::string str)
        {
            uint256 hash;
            CHash256().Write(MakeUCharSpan(str)).Finalize(hash);
            return hash.ToString();
        }

        // The function used to sort the vector of file names
        static bool pathCompareFunction (std::string a, std::string b) {
            return a < b;
        }

        // Recursively list the files in a directory
        std::vector<std::string> getFiles(std::string directory, std::string regexToIncludeStr, std::string regexToIgnoreStr) {
            std::vector<std::string> files;
            for(std::filesystem::recursive_directory_iterator i(directory), end; i != end; ++i) {
                if(!is_directory(i->path())) {
                    std::string str = i->path();
                    if(std::regex_match(str, std::regex(regexToIncludeStr)) && !std::regex_match(str, std::regex(regexToIgnoreStr))) {
                        files.push_back(str);
                    }
                }
            }
            std::sort(files.begin(),files.end(), pathCompareFunction);
            return files;
        }

        // Read the contents of a file at a given file path
        std::string getContents(std::string filePath) {
            std::string contents = "";
            std::ifstream f(filePath);
            while(f) {
                std::string line;
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

    public:

        std::vector<std::string> const supportedVersions = {
            "/Satoshi:23.0.0/"
        };

        //RecursiveMutex cs_handshakeProof;

        // HandshakeProof(int temp) {
        //     LogPrint(BCLog::HANDSHAKE_PROOF, "\nINITIALIZED THE HANDSHAKE PROVER");
        // }

        bool isVersionSupported(std::string version) const {
            for(int i = 0; i < (int)supportedVersions.size(); i++) {
                LogPrint(BCLog::HANDSHAKE_PROOF, "\nCHECKING VERSION %s == %s --> %s", version, supportedVersions.at(i), version == supportedVersions.at(i));
                if(version == supportedVersions.at(i)) return true;
            }
            return false;
        }

        std::string generateProof(std::string ID) {
            if(!initialized) initialize();
            // Update the ID
            LogPrint(BCLog::HANDSHAKE_PROOF, "\nGENERATING PROOF FOR %s", ID);
            updateHashAtIndex(tree, 0, sha256(ID));
            return tree.root().to_string();
        }

        bool verifyProof(std::string hash, std::string ID) {
            LogPrint(BCLog::HANDSHAKE_PROOF, "\nVERIFYING PROOF FOR %s", ID);
            return generateProof(ID) == hash;
            
            // if(tree.root().to_string() == "fbdef921f44b67c5104404a2b1d496cedc5001a7bd321fb31bda1a7ac4cef571") {
            //     cout << "Correct version" << endl;
            // } else {
            //     cout << "Incorrect version: " << tree.root().to_string() << endl;
            // }
        }

        // Update the hash at an index within the tree
        void updateHashAtIndex(merkle_proof::Tree &tree, int index, std::string hash_string) {
            merkle_proof::TreeT<32, merkle_proof::sha256_compress>::Node* ID = tree.walk_to(index, true, [](merkle_proof::TreeT<32, merkle_proof::sha256_compress>::Node* n, bool go_right) {
                n->dirty = true;
                return true;
            });
            merkle_proof::Tree::Hash newHash(hash_string);
            ID->hash = newHash;
            tree.compute_root();
        }

        std::string getHash() const {
            return merkle_hash;
        }

        void initialize() {
            if(initialized) return;
            LogPrint(BCLog::HANDSHAKE_PROOF, "\nINITIALIZING HANDSHAKE PROVER");

            // Get the list of code file names
            std::string directory = "../src";
            std::string regexToIncludeStr = ".*(\\.cpp|\\.c|\\.h|\\.cc|\\.py|\\.sh)";
            std::string regexToIgnoreStr = ".*(/build-aux/|/config/|-config.h|/minisketch/|/obj/|/qt/|/univalue/gen/|/zqm/).*";

            // Get the list of code file names
            std::vector<std::string> files = getFiles("../src", regexToIncludeStr, regexToIgnoreStr);
            std::vector<std::string> hashes ((int)files.size());
            // Compute the hash of the files
            for(int i = 0; i < (int)files.size(); i++) {
                hashes.at(i) = sha256(getContents(files[i]));
            }
            // Set the initial ID
            hashes.insert(hashes.begin(), "0000000000000000000000000000000000000000000000000000000000000000");
            // Adjust the size to make it a full binary tree
            int targetSize = nextPowerOfTwo((int)hashes.size()), i = 0;
            while((int)hashes.size() < targetSize) {
                hashes.push_back(hashes.at(i));
                i++;
            }

            // Cybersecurity Lab: Testing a mini tree
            // std::vector<std::string> hashes (16);
            // for(int i = 0; i < 16; i++) {
            //  hashes.at(i) = sha256(to_string(i + 1));
            // }

            // Convert the hashes to Merkle node objects
            std::vector<merkle_proof::Tree::Hash> leaves ((int)hashes.size());
            for(int i = 0; i < (int)hashes.size(); i++) {
                merkle_proof::Tree::Hash hash(hashes.at(i));
                leaves.at(i) = hash;
            }

            // Create the tree
            tree.insert(leaves);

            // Update the ID
            updateHashAtIndex(tree, 0, "0000000000000000000000000000000000000000000000000000000000000000");

            merkle_hash = tree.root().to_string();

            // auto root = tree.root();
            // auto path = tree.path(0);
            // assert(path->verify(root));
            initialized = true;
        }
};


#endif // BITCOIN_HANDSHAKE_PROOF_CPP