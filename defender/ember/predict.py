import argparse
import pickle
from ember import PEFeatureExtractor
from numpy import reshape


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('pefile', type=str, help='portable exectuable file')
    parser.add_argument('model', type=str, help='pickled model file')
    args = parser.parse_args()

    extractor = PEFeatureExtractor(feature_version=2, print_feature_warning=False)

    with open(args.pefile, 'rb') as pe_file:
        features = extractor.feature_vector(pe_file.read())
    features = reshape(features, (1, -1))

    with open(args.model, 'rb') as model_file:
        model = pickle.load(model_file)

    yhat = model.predict(features)[0]
    print(f'Prediction: {yhat}')


if __name__ == '__main__':
    main()
