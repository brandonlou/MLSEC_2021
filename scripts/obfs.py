import ahocorasick
import argparse
import base64
import pickle
import os

class ObfuscationDetector:
    def __init__(self, automaton_filename=''):
        if automaton_filename:
            with open(automaton_filename, 'rb') as automaton_pkl:
                self.A = pickle.load(automaton_pkl)
        else:
            self.A = ahocorasick.Automaton()
            word_list = ('This program', 'Rich', '.text', '.data', '.rdata', '.reloc', '.rsrc', '.dll', 'System')
            # XOR encode the word list
            for key in range(1, 256):
                for word in word_list:
                    encoded = bytes([ord(char) ^ key for char in word])
                    self.A.add_word(encoded, (key, encoded))
            # Base 64 encode the word list
            for word in word_list:
                bytez = word.encode('utf-8')
                encoded64 = base64.b64encode(bytez)
                encoded32 = base64.b32encode(bytez)
                encoded16 = base64.b16encode(bytez)
                self.A.add_word(encoded64, (364, encoded64))
                self.A.add_word(encoded32, (332, encoded32))
                self.A.add_word(encoded16, (316, encoded16))
            self.A.make_automaton()

    def save(self, pkl_filename):
        with open(pkl_filename, 'wb') as automaton_pkl:
            pickle.dump(self.A, automaton_pkl)

    def analyze_file(self, pe_filename):
        with open(pe_filename, 'rb') as in_file:
            pe_file_contents = in_file.read()
        found_strings = dict()
        for end_index, (key, original_value) in self.A.iter(pe_file_contents):
            if found_strings.get(key) is None:
                found_strings[key] = {original_value}
            else:
                found_strings[key].add(original_value)
            if key < 256:
                decoded = [chr(b ^ key) for b in original_value]
                print(f"Found: {''.join(decoded)} (key = {key})")
            elif key == 316:
                decoded = str(base64.b16decode(original_value), 'utf-8')
                print(f'Found: {decoded} (base16)')
            elif key == 332:
                decoded = str(base64.b32decode(original_value), 'utf-8')
                print(f'Found: {decoded} (base32)')
            elif key == 364:
                decoded = str(base64.b64decode(original_value), 'utf-8')
                print(f'Found: {decoded} (base64)')
        for key in found_strings.keys():
            if len(found_strings[key]) >= 2:
                print('Malicious!')
                return True
        print('Benign')
        return False


def main():
    obfs = ObfuscationDetector()
    for filename in os.listdir('MLSEC_2019_samples_and_variants'):
        malicious = obfs.analyze_file(f'MLSEC_2019_samples_and_variants/{filename}')
        if malicious:
            print(filename)
 
if __name__ == '__main__':
    main()

