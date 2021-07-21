import argparse
import base64
import pickle
import py
import re
import subprocess
from ember import PEFeatureExtractor


THRESHOLD = 0.5
PE_STRINGS = ('This program cannot be run in DOS mode', 'This is a PE executable', '.text', '.data', '.rdata', '.reloc', '.rsrc', '.dll', 'Windows', 'windows', 'Microsoft', 'microsoft')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('pefile', type=str, help='portable executable file to classify as benign or malicious')
    parser.add_argument('vectorizer', type=str, help='pickled HashingVectorizer')
    parser.add_argument('model', type=str, help='pickled model file')
    return parser.parse_args()


def contains_string(in_string):
    for pe_string in PE_STRINGS:
        if pe_string in in_string:
            print(f'String found: {pe_string}')
            return True
    return False


def main():
    args = parse_args()
    with open(args.pefile, 'rb') as pe_file:
        pe_bytes = pe_file.read()
    with open(args.vectorizer, 'rb') as vectorizer_file:
        vectorizer = pickle.load(vectorizer_file)
    with open(args.model, 'rb') as model_file:
        model = pickle.load(model_file)
    
    # Brute force all single byte XOR keys
    for key in range(1, 256):
        print(f'Trying XOR key {key}...')
        out_bytes = b''
        for byte in pe_bytes:
            out_bytes += bytes([byte ^ key])
        out_str = str(out_bytes)
        if contains_string(out_str):
            print(f'Malicious: Detected XOR encryption')
            return

    # Match at least 1000 base-64 characters followed by 0 to 3 padding characters
    prog = re.compile(r"([\w+/]{1000,}={0,3})")
    match = prog.match(str(pe_bytes))
    if match is not None:
        b64_str = match.group()[1]
        b64_decoded = base64.b64decode(b64_str)
        if contains_string(b64_decoded):
            print(f'Malicious: Detected base64 encryption')
            return

    # Extract opcodes.
    opcode_matcher = re.compile(r"\s*[0-9A-Fa-f]+:\s+([0-9A-Fa-f][0-9A-Fa-f])\s")
    try:
        objdump = subprocess.run(['objdump', '-d', args.pefile], stdout=subprocess.PIPE, check=True, universal_newlines=True).stdout
    except Exception as e:
        print(e)
        return
    opcode_sequence = []
    for line in objdump.splitlines():
        result = opcode_matcher.match(line)
        if result is not None:
            opcode = result.group(1)
            opcode_sequence.append(opcode)
    if not opcode_sequence:
        print('No opcodes found. File is benign')
        return
    opcode_string = ' '.join(opcode_sequence)

    # Extract ember features.
    extractor = PEFeatureExtractor(feature_version=2, print_feature_warning=False)
    capture = py.io.StdCaptureFD(out=False, in_=False)
    features_dict = extractor.raw_features(pe_bytes)
    out, err = capture.reset()
    features_dict['ember_errors'] = []
    for line in err.splitlines():
        features_dict['ember_errors'].append(line)

    # Vectorize opcodes and features here
    X = vectorizer.transform([opcode_string])

    # Use model here
    y = model.predict_proba(X)[0][1]
    if y > THRESHOLD:
        print(f'Malicious (P={y})')
    else:
        print(f'Benign (P={y})')


if __name__ == '__main__':
    main()

