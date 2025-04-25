#include <iostream>
#include <unordered_map>
#include <vector>
#include <string>
#include <fstream>
#include <string>
#include <sstream>
using namespace std;

class DFA {
private:
    struct Node {
        unordered_map<char, Node*> children;
        bool isFinal = false;
    };

    Node* root;

public:
    DFA() {
        root = new Node();
    }

    // Insert a word into the DFA
    void insert(const string& word) {
        Node* curr = root;
        for (char ch : word) {
            if (curr->children.find(ch) == curr->children.end()) {
                curr->children[ch] = new Node();
            }
            curr = curr->children[ch];
        }
        curr->isFinal = true;
    }

    // Check if input string is accepted by the DFA
    bool accepts(const string& input) {
        Node* curr = root;
        for (char ch : input) {
            if (ispunct(ch))
                continue;
            if (curr->children.find(ch) == curr->children.end()) {
                return false;
            }
            curr = curr->children[ch];
        }
        return curr->isFinal;
    }

    ~DFA() {
        freeNode(root);
    }

private:
    void freeNode(Node* node) {
        for (auto& pair : node->children) {
            freeNode(pair.second);
        }
        delete node;
    }
};

int main() {
    // Open the text file named "input.txt"
    ifstream f("input.txt");

    // Check if the file is successfully opened
    if (!f.is_open()) {
        cerr << "Error opening the file!";
        return 1;
    }

    // String variable to store the read data
    string s;
    vector <string> tokens;
    string intermediate;
    // Read each line of the file and print it to the
    // standard output stream till the whole file is
  	// completely read
    while (getline(f, s)) {
        //cout << s << '\n';
        stringstream check1(s);
        while (getline(check1, intermediate, ' '))
            tokens.push_back(intermediate);
    }
        
    // Close the file
    f.close();

    vector<string> acceptedWords = {
        "Malaysia", "Thailand", "Singapore", "Vietnam", "Indonesia", "Brunei",
        "Philippines", "Malaya", "North Borneo", "British Empire", "Peninsular Malaysia",
        "East Malaysia", "Malaysian Borneo", "Sarawak", "Tanjung Piai", "Straits Settlements",
        "Malayan Union", "Federation of Malaya", "Kuala Lumpur", "Putrajaya", "Southeast Asia",
        "continental Eurasia", "tropics", "Malay kingdoms", "British protectorates",
        "Association of Southeast Asian Nations", "East Asia Summit",
        "Organisation of Islamic Cooperation", "Asia-Pacific Economic Cooperation",
        "Commonwealth of Nations", "Non-Aligned Movement"
    };

    DFA dfa;
    for (const string& word : acceptedWords) {
        dfa.insert(word);
    }

    // string test;
    // cout << "Enter input to test: ";
    // getline(cin, test);
    // Printing the token vector
    for(int i = 0; i < tokens.size(); i++) {
        if (dfa.accepts(tokens[i])) {
            cout << tokens[i] << " Accepted by DFA" << endl;
        } else {
            cout << tokens[i] <<" Rejected by DFA" << endl;
        }
    }
    
    return 0;
}
