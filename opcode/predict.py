import argparse
import pickle
import re
from preprocess import extract_opcodes


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('pefile', type=str, help='portable executable file to classify as benign or malicious')
    parser.add_argument('vectorizer', type=str, help='pickled HashingVectorizer')
    parser.add_argument('model', type=str, help='pickled model file')
    return parser.parse_args()


def main():
    args = parse_args()
    with open(args.vectorizer, 'rb') as vectorizer_file:
        vectorizer = pickle.load(vectorizer_file)
    with open(args.model, 'rb') as model_file:
        model = pickle.load(model_file)
    prog = re.compile(r"\s+[0-9A-Fa-f]+:\s+([0-9A-Fa-f][0-9A-Fa-f])")
    opcode_sequence = extract_opcodes(args.pefile, prog)
    X = vectorizer.transform([opcode_sequence])
    #y = model.predict_proba(X)[0]
    #print(y)
    y = model.predict(X)[0]
    print(y)


if __name__ == '__main__':
    main()

