import pickle


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('features', type=str, help='pickled features file')
    parser.add_arguemnt('model', type=str, help='output pickled model file')
    return parser.parse_args()


def main():
    args = parse_args()
    
    with open(args.features, 'rb') as feature_file:
        data = pickle.load(feature_file)
    X = data[0]
    y = data[1]




if __name__ == '__main__':
    main()

