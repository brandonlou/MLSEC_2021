import argparse
import os
import pickle
import subprocess
import sys
import re
from sklearn.feature_extraction.text import HashingVectorizer


STOP_WORDS = []
LINES_TO_SKIP = 7
HASH_BITS = 12


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('malign', type=str, help='directory containing malign pe files')
    parser.add_argument('benign', type=str, help='directory containing benign pe files')
    parser.add_argument('output', type=str, help='filename of pickled features')
    return parser.parse_args()


# Extracts opcodes from a single PE file.
def extract_opcodes(filename: str, prog) -> str:
    if os.path.getsize(filename) > 2097152: # 2 MiB
        return None
    try:
        objdump = subprocess.run(['objdump', '-d', filename], stdout=subprocess.PIPE, check=True, universal_newlines=True).stdout
    except:
        return None

    opcode_sequence = []
    first_section = False

    for line in objdump.splitlines():
        # Only want to read one code section for now
        if line[0:11] == 'Disassembly':
            if first_section:
                break
            else:
                first_section = True
                continue
        result = prog.match(line)
        if result is not None:
            opcode = result.group(1)
            opcode_sequence.append(opcode)
    return ' '.join(opcode_sequence)


def main():
    args = parse_args()
    malign_dir = args.malign
    benign_dir = args.benign
    output_filename = args.output

    # Any number of whitespace, one or more hex characters, colon, any number of whitespace, two hex characters    
    prog = re.compile(r"\s+[0-9A-Fa-f]+:\s+([0-9A-Fa-f][0-9A-Fa-f])")

    corpus = []
    y = []
    
    for pe_file in os.listdir(malign_dir):
        opcode_sequence = extract_opcodes(f'{malign_dir}/{pe_file}', prog)
        if opcode_sequence is not None:
            corpus.append(opcode_sequence)
            y.append(1)
    
    for pe_file in os.listdir(benign_dir):
        opcode_sequence = extract_opcodes(f'{benign_dir}/{pe_file}', prog)
        if opcode_sequence is not None:
            corpus.append(opcode_sequence)
            y.append(0)
    
    vectorizer = HashingVectorizer(input='content', lowercase=False, stop_words=STOP_WORDS, ngram_range=(2, 2), analyzer='word', n_features=2**HASH_BITS)
    X = vectorizer.fit_transform(corpus)

    with open(output_filename, 'wb') as output_file:
        pickle.dump((X, y), output_file, protocol=pickle.HIGHEST_PROTOCOL)
    print(f'Saved features to {output_filename}')


if __name__ == '__main__':
    main()

