import argparse
import pickle
from lightgbm import LGBMClassifier
from numpy import array, mean, std
from sklearn.feature_selection import RFE, SelectKBest, f_classif
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, \
                            precision_score, recall_score, roc_auc_score
from sklearn.model_selection import KFold


NUM_FOLDS = 10
BOOSTING = 'gbdt'
OBJECTIVE = 'binary'
LEARNING_RATE = 0.01
NUM_LEAVES = 2048
MAX_DEPTH = 15
# MIN_DATA_IN_LEAF = 50
# FEATURE_FRACTION = 0.5
FEATURES_TO_SELECT = 150


def get_model():
    classifier = LGBMClassifier(boosting_type=BOOSTING, num_leaves=NUM_LEAVES,
                           max_depth=MAX_DEPTH, learning_rate=LEARNING_RATE,
                           objective=OBJECTIVE)
    #rfe = RFE(classifier, n_features_to_select=FEATURES_TO_SELECT, step=1)
    return classifier


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('features', type=str, help='pickled sample features file')
    parser.add_argument('model', type=str, help='output model filename')
    args = parser.parse_args()

    with open(args.features, 'rb') as feature_file:
        data = pickle.load(feature_file)
    X_data = array(data[0])
    y_data = array(data[1])

    # Feature selection using ANOVA F measure
    fs = SelectKBest(score_func=f_classif, k=FEATURES_TO_SELECT)
    X_data = fs.fit_transform(X_data, y_data)

    accuracy = list()
    precision = list()
    recall = list()
    auc = list()
    fp_rate = list()
    f1 = list()

    # Prepare cross-validation procedure
    kfold = KFold(n_splits=NUM_FOLDS, shuffle=True, random_state=1)
    current_fold = 1
    for train, test in kfold.split(X_data, y_data):
        model = get_model()
        model.fit(X_data[train], y_data[train])
        y_pred = model.predict(X_data[test])
        y_test = y_data[test]

        # Calculate metrics
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
    model.fit(X_data, y_data)

    with open(args.model, 'wb') as out_file:
        pickle.dump(model, out_file, protocol=pickle.HIGHEST_PROTOCOL)
    print(f'Saved trained model to {args.model}')


if __name__ == '__main__':
    main()
