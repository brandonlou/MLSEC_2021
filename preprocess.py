import ember
import os
import sys


def main():
    if len(sys.argv) != 4:
        print(f'Usage: python3 {sys.argv[0]} <input dir> <output dir> <m/b>')
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    if sys.argv[3] == 'm': # Malicious
        verdict = 1
    elif sys.argv[3] == 'b': # Benign
        verdict = 0
    else:
        print(f'Usage: python3 {sys.argv[0]} <input dir> <output dir> <m/b>')
        sys.exit(1)

    #for filename in os.listdir(input_dir):
    ember.create_vectorized_features(input_dir)
    ember.create_metadata(input_dir)
        # Get Ember features
        # Get other features


if __name__ == '__main__':
    main()

