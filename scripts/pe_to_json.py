import argparse
import json
import os
import py
import sys
from ember import PEFeatureExtractor


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', type=str, help='directory containing raw pe files')
    parser.add_argument('output_dir', type=str, help='directory to contain feature JSONs')
    return parser.parse_args()


def main():
    args = parse_args()
    input_dir = args.input_dir
    output_dir = args.output_dir

    # Capture all stderr from lief (C++ module)
    capture = py.io.StdCaptureFD(out=False, in_=False)
   
    pe_to_json = dict() 
    extractor = PEFeatureExtractor(feature_version=2, print_feature_warning=False)
   
    # Extract ember features 
    for pe_file in os.listdir(input_dir):
        pe_filename = f'{input_dir}/{pe_file}'
        if os.path.getsize(pe_filename) > 2097152: # 2 MiB
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
        with open(f'{output_dir}/{pe_file}.json', 'wt') as out_file:
            json.dump(pe_to_json[pe_file], out_file, indent=4)


if __name__ == '__main__':
    main()

