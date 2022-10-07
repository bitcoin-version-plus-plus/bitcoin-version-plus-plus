#ifndef BITCOIN_HANDSHAKE_PROOF_CPP
#define BITCOIN_HANDSHAKE_PROOF_CPP

// This code is created by the Cybersecurity Lab, University of Colorado, Colorado Springs, 2022

#include <iostream>
#include <filesystem>
#include <fstream>
#include <vector>
#include <string>
#include <regex>
#include <inttypes.h>
#include <random.h>
#include <util/strencodings.h>
#include <logging.h>
#include <hash.h>
#include <handshake_proof_merkle.cpp>
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wsubobject-linkage"

class HandshakeProof {
    private:
        bool initialized = false;
        HandshakeProofTreeT<32, sha256_compress> merkleTree;
        std::string merkleHash = "";

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

        // Given a number (e.g. 10) compute the next power of two (e.g. 16)
        int nextPowerOfTwo(int num) {
            double n = log2(num);
            return (int)pow(2, ceil(n));
        }

    public:

        std::string generateProof(std::string ID) {
            if(!initialized) initialize();
            // Update the ID
            if(ID == "::") {
                std::vector<uint8_t> newID(4);
                GetRandBytes(newID.data(), 4);
                ID = HexStr(newID);
                LogPrint(BCLog::HANDSHAKE_PROOF, "\nChanged ID from \"::\" to \"%s\"", ID);
            }
            LogPrint(BCLog::HANDSHAKE_PROOF, "\nGenerating handshake proof for \"%s\"", ID);
            updateHashAtIndex(merkleTree, 0, sha256(ID));
            return ID + "@" + merkleTree.root().to_string();
        }

        bool verifyProof(std::string combined) {
            std::string ID, hash;
            std::regex rgx("([^@]+)@(.+)");
            std::smatch matches;
            if(std::regex_search(combined, matches, rgx)) {
                ID = matches[1].str();
                hash = matches[2].str();
            } else {
                // Invalid format, verification failed
                LogPrint(BCLog::HANDSHAKE_PROOF, "\nHandshake proof \"%s\" was in the wrong format", combined);
                return false;
            }
            LogPrint(BCLog::HANDSHAKE_PROOF, "\nVerifying handshake proof for \"%s\"", ID);

            updateHashAtIndex(merkleTree, 0, sha256(ID));
            std::string proof = merkleTree.root().to_string();
            LogPrint(BCLog::HANDSHAKE_PROOF, "\n\"%s\" == \"%s\"", proof, hash);
            return proof == hash;
        }

        // Update the hash at an index within the merkleTree
        void updateHashAtIndex(HandshakeProofTree &merkleTree, int index, std::string hashString) {
            HandshakeProofTreeT<32, sha256_compress>::HandshakeProofNode* ID = merkleTree.walk_to(index, true, [](HandshakeProofTreeT<32, sha256_compress>::HandshakeProofNode* n, bool go_right) {
                n->dirty = true;
                return true;
            });
            HandshakeProofTree::Hash newHash(hashString);
            ID->hash = newHash;
            merkleTree.compute_root();
        }

        std::string getHash() const {
            return merkleHash;
        }

        void initialize() {
            if(initialized) return;
            LogPrint(BCLog::HANDSHAKE_PROOF, "\nHandshake prover is being initialized...");
            std::string currentPath(std::filesystem::current_path());
            LogPrint(BCLog::HANDSHAKE_PROOF, "\nCurrent path = %s", currentPath);

            // Get the list of code file names
            std::string directory = "./src";
            std::string regexToIncludeStr = ".*(\\.cpp|\\.c|\\.h|\\.cc|\\.py|\\.sh)";
            std::string regexToIgnoreStr = ".*(/build-aux/|/config/|-config.h|/minisketch/|/obj/|/qt/|/univalue/gen/|/zqm/).*";
            // Get the list of code file names
            std::vector<std::string> files = getFiles(directory, regexToIncludeStr, regexToIgnoreStr);
            std::vector<std::string> hashes ((int)files.size());
            // Compute the hash of the files
            for(int i = 0; i < (int)files.size(); i++) {
                hashes.at(i) = sha256(getContents(files[i]));
            }
            // Set the initial ID
            hashes.insert(hashes.begin(), "0000000000000000000000000000000000000000000000000000000000000000");
            // Adjust the size to make it a full binary merkleTree
            int targetSize = nextPowerOfTwo((int)hashes.size()), i = 0;
            while((int)hashes.size() < targetSize) {
                hashes.push_back(hashes.at(i));
                i++;
            }

            // Cybersecurity Lab: Testing a mini merkleTree
            // std::vector<std::string> hashes (16);
            // for(int i = 0; i < 16; i++) {
            //  hashes.at(i) = sha256(to_string(i + 1));
            // }

            // Convert the hashes to Merkle node objects
            std::vector<HandshakeProofTree::Hash> leaves ((int)hashes.size());
            for(int i = 0; i < (int)hashes.size(); i++) {
                HandshakeProofTree::Hash hash(hashes.at(i));
                leaves.at(i) = hash;
            }

            // Create the merkleTree
            merkleTree.insert(leaves);

            // Update the ID
            updateHashAtIndex(merkleTree, 0, "0000000000000000000000000000000000000000000000000000000000000000");

            merkleHash = merkleTree.root().to_string();
            initialized = true;
        }

        // Read the contents of a file at a given file path
        static std::string getContents(std::string filePath) {
            std::string contents = "";
            std::ifstream f(filePath);
            while(f) {
                std::string line;
                getline(f, line);
                contents += line + '\n';
            }
            return contents;
        }

        // Computes the SHA-256 hash of a string
        static std::string sha256(const std::string str)
        {
            uint256 hash;
            CHash256().Write(MakeUCharSpan(str)).Finalize(hash);
            return hash.ToString();
        }
};

#pragma GCC diagnostic pop
#endif // BITCOIN_HANDSHAKE_PROOF_CPP