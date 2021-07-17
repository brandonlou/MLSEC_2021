import argparse
import os
import pickle
import subprocess
import sys
import re
from sklearn.feature_extraction.text import HashingVectorizer


#STOP_WORDS = ['0f', '72', '73', '74', '75', '76', '77', '78', '79', '7a', '7b', '7c', '7d', '7e', '7f', '9a', 'c3', 'c2', 'ca', 'cb', 'e0', 'e1', 'e2', 'e3', 'e8', 'ff']
STOP_WORDS = []
HASH_BITS = 12


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('malign', type=str, help='directory containing malicious PE opcode files')
    parser.add_argument('benign', type=str, help='directory containing benign PE opcode files')
    parser.add_argument('-f', '--features', type=str, help='output filename containing pickled features')
    parser.add_argument('-v', '--vectorizer', type=str, help='output filename containing vectorizer used')
    return parser.parse_args()


def main():
    args = parse_args()
    malign_dir = args.malign
    benign_dir = args.benign
    features_filename = args.features
    vectorizer_filename = args.vectorizer

    corpus = []
    y = []

    print('Processing opcode files...')   
 
    for root, _, files in os.walk(malign_dir):
        for f in files:
            filename = f'{root}/{f}'
            with open(filename, 'rt') as in_file:
                opcode_sequence = in_file.read()
            corpus.append(opcode_sequence)
            y.append(1)

    for root, _, files in os.walk(benign_dir):
        for f in files:
            filename = f'{root}/{f}'
            with open(filename, 'rt') as in_file:
                opcode_sequence = in_file.read()
            corpus.append(opcode_sequence)
            y.append(0)
    
    print('Vectorizing opcodes...')
    vectorizer = HashingVectorizer(input='content', lowercase=False, stop_words=STOP_WORDS, ngram_range=(2, 2), analyzer='word', n_features=2**HASH_BITS)
    X = vectorizer.fit_transform(corpus)

    if features_filename is not None:
        with open(features_filename, 'wb') as features_file:
            pickle.dump((X, y), features_file, protocol=pickle.HIGHEST_PROTOCOL)
        print(f'Saved features to {features_filename}')

    if vectorizer_filename is not None:
        with open(vectorizer_filename, 'wb') as vectorizer_file:
            pickle.dump(vectorizer, vectorizer_file, protocol=pickle.HIGHEST_PROTOCOL)
        print(f'Saved vectorizer to {vectorizer_filename}')

    print('Done')


if __name__ == '__main__':
    main()

