import argparse
import os
import pickle
from ember import PEFeatureExtractor


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('malign', type=str, help='directory containing ember JSONs of malicious PEs')
    parser.add_argument('benign', type=str, help='directory containing ember JSONs of benign PEs')
    parser.add_argument('output', type=str, help='output pickle file')
    return parser.parse_args()


def main():
    args = get_args()
    malign_dir = args.malign
    benign_dir = args.benign
    output_file = args.output

    feature_list = list()
    label_list = list()

    for filename in os.listdir(malign_dir):
        with open(f'{malign_dir}/{filename}', 'rt') as malign_json:
            malign_dict = json.load(malign_json)
        # Extract useful features

    for filename in os.listdir(benign_dir):
        with open(f'{benign_dir}/{filename}' 'rt') as benign_json:
            benign_dict = json.load(benign_json)


    for binary_file in os.listdir(malign_dir):
        with open(f'{malign_dir}/{binary_file}', 'rb') as in_file:
            feature_vector = extractor.feature_vector(in_file.read())
            feature_list.append(feature_vector)
            label_list.append(1)
            print(f'Extracted features from {malign_dir}/{binary_file}')

    for binary_file in os.listdir(benign_dir):
        with open(f'{benign_dir}/{binary_file}', 'rb') as in_file:
            feature_vector = extractor.feature_vector(in_file.read())
            feature_list.append(feature_vector)
            label_list.append(0)
            print(f'Extracted features from {benign_dir}/{binary_file}')

    # Do feature selection? (fisher score, tf-idf score, etc.)

    with open(output_file, 'wb') as out_pkl:
        pickle.dump((feature_list, label_list), out_pkl, protocol=pickle.HIGHEST_PROTOCOL)
    print(f'Saved features to {output_file}')


if __name__ == '__main__':
    main()

