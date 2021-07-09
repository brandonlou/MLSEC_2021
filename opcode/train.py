import argparse
import pickle
from numpy import array, mean
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold


NUM_FOLDS = 10
NUM_ESTIMATORS = 60
MAX_DEPTH = 30
THRESHOLD = 0.87


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('features', type=str, help='pickled features file')
    parser.add_argument('model', type=str, help='output pickled model file')
    return parser.parse_args()


def get_model():
    model = RandomForestClassifier(n_estimators=NUM_ESTIMATORS, criterion='entropy', max_depth=MAX_DEPTH, n_jobs=-1, random_state=1)
    return model


def main():
    args = parse_args()
    
    with open(args.features, 'rb') as feature_file:
        data = pickle.load(feature_file)
    X = data[0]
    y = array(data[1])

    accuracy = []
    precision = []
    recall = []
    auc = []
    fp_rate = []
    f1 = []

    kfold = StratifiedKFold(n_splits=NUM_FOLDS, shuffle=True, random_state=1)
    current_fold = 1
    for train, test in kfold.split(X, y):
        model = get_model()
        model.fit(X[train], y[train])
        y_proba = model.predict_proba(X[test])[:,1]
        y_pred = [int(p >= THRESHOLD) for p in y_proba]
        y_test = y[test]

        accuracy.append(accuracy_score(y_test, y_pred))
        precision.append(precision_score(y_test, y_pred))
        recall.append(recall_score(y_test, y_pred))
        auc.append(roc_auc_score(y_test, y_pred))
        f1.append(f1_score(y_test, y_pred))
        tn, fp, _, _ = confusion_matrix(y_test, y_pred).ravel()
        fp_rate.append(fp / (fp + tn))        

        print(f'Fold {current_fold} complete')
        current_fold += 1

    print(f'Accuracy: {round(mean(accuracy), 3):.3f}')
    print(f'Precision: {round(mean(precision), 3):.3f}')
    print(f'Recall: {round(mean(recall), 3):.3f}')
    print(f'AUC: {round(mean(auc), 3):.3f}')
    print(f'FP Rate: {round(mean(fp_rate), 3):.3f}')
    print(f'F1 Score: {round(mean(f1), 3):.3f}')

    # Create a single model fitted from all available data.
    model = get_model()
    model.fit(X, y)
    with open(args.model, 'wb') as out_file:
        pickle.dump(model, out_file, protocol=pickle.HIGHEST_PROTOCOL)
    print(f'Saved trained model to {args.model}')


if __name__ == '__main__':
    main()

