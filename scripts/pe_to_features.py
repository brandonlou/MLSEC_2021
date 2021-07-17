import argparse
import json
import os
import py
import re
import subprocess
import sys
from ember import PEFeatureExtractor


MAX_FILE_SIZE = 2097152 # 2 MiB


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', type=str, help='directory containing raw pe files')
    parser.add_argument('ember_dir', type=str, help='directory to contain ember feature JSONs')
    parser.add_argument('opcode_dir', type=str, help='directory to cotain PE file opcodes')
    return parser.parse_args()


def main():
    args = parse_args()
    input_dir = args.input_dir
    ember_dir = args.ember_dir
    opcode_dir = args.opcode_dir

    # Capture all stderr from lief (a C++ module)
    capture = py.io.StdCaptureFD(out=False, in_=False)

    pe_to_json = dict()
    extractor = PEFeatureExtractor(feature_version=2, print_feature_warning=False)

    # Extract ember features
    for pe_file in os.listdir(input_dir):
        pe_filename = f'{input_dir}/{pe_file}'
        if os.path.getsize(pe_filename) > MAX_FILE_SIZE:
            continue
        with open(pe_filename, 'rb') as in_file:
            sys.stdout.write(f'FILE: {pe_file}\n')
            sys.stderr.write(f'FILE: {pe_file}\n')
            sys.stderr.flush()
            features_dict = extractor.raw_features(in_file.read())
            features_dict['ember_errors'] = []
            pe_to_json[pe_file] = features_dict

    # Append lief/ember warnings to use as features
    out, err = capture.reset()
    filename = ''
    for line in err.splitlines():
        if line[0:5] == 'FILE:':
            filename = line[6:]
        else:
            pe_to_json[filename]['ember_errors'].append(line)

    # Save to JSON file
    for pe_file in pe_to_json:
        with open(f'{ember_dir}/{pe_file}.json', 'wt') as out_file:
            json.dump(pe_to_json[pe_file], out_file, indent=4)

    # Any number of whitespace, one or more hex characters, colon, any number of whitespace, two hex characters
    prog = re.compile(r"\s+[0-9A-Fa-f]+:\s+([0-9A-Fa-f][0-9A-Fa-f])")

    for pe_file in os.listdir(input_dir):
        pe_filename = f'{input_dir}/{pe_file}'
        if os.path.getsize(pe_filename) > MAX_FILE_SIZE:
            continue
        try:
            objdump = subprocess.run(['objdump', '-d', pe_filename], stdout=subprocess.PIPE, check=True, universal_newlines=True).stdout
        except Exception as e:
            print(e)
            continue
        opcode_sequence = []
        # Go through objdump output and extract opcodes using regex.
        for line in objdump.splitlines():
            result = prog.match(line)
            if result is not None:
                opcode = result.group(1)
                opcode_sequence.append(opcode)
        opcode_string = ' '.join(opcode_sequence) # Convert list of opcodes into a string.
        with open(f'{opcode_dir}/{pe_filename}.op', 'wt') as opcode_file:
            opcode_file.write(opcode_string)
        print('Saved {pe_file} opcodes to {opcode_dir}/{pe_filename}.op')

    print('Done.')


if __name__ == '__main__':
    main()

