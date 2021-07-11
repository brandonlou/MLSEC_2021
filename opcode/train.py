import argparse
import pickle
from numpy import array, mean
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score, make_scorer
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from lightgbm import LGBMClassifier


NUM_FOLDS = 10
NUM_LEAVES = 32
MAX_DEPTH = 12
LEARNING_RATE = 0.25
NUM_TREES = 75
THRESHOLD = 0.5 #0.998


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('features', type=str, help='pickled features file')
    parser.add_argument('model', type=str, help='output pickled model file')
    return parser.parse_args()


def get_model():
    model = LGBMClassifier(boosting_type='gbdt', num_leaves=NUM_LEAVES, max_depth=MAX_DEPTH, learning_rate=LEARNING_RATE, n_estimators=NUM_TREES, objective='binary', reg_alpha=0.1, random_state=1, n_jobs=-1)
    return model


def optimize_model(X, y):
    score = make_scorer(roc_auc_score, max_fpr=5e-3)
    param_grid = {
        'boosting_type': ['gbdt'],
        'objective': ['binary'],
        'num_iterations': [500, 1000],
        'learning_rate': [0.005, 0.05, 0.1, 0.25, 0.5],
        'num_leaves': [16, 32, 64, 128, 256, 512, 1024, 2048],
        'feature_fraction': [0.5, 0.8, 1.0],
        'bagging_fraction': [0.5, 0.8, 1.0]
    }
    model = LGBMClassifier(n_jobs=-1, silent=True)
    grid = GridSearchCV(estimator=model, cv=NUM_FOLDS, param_grid=param_grid, scoring=score, n_jobs=1, verbose=3)
    grid.fit(X, y)
    return grid.best_params_


def main():
    args = parse_args()
    
    with open(args.features, 'rb') as feature_file:
        data = pickle.load(feature_file)
    X = data[0]
    y = array(data[1])

    #best_params = optimize_model(X, y)
    #print(best_params)
    #exit()

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

        # Calculate metrics.
        accuracy.append(accuracy_score(y_test, y_pred))
        precision.append(precision_score(y_test, y_pred))
        recall.append(recall_score(y_test, y_pred))
        auc.append(roc_auc_score(y_test, y_pred))
        f1.append(f1_score(y_test, y_pred))
        tn, fp, _, _ = confusion_matrix(y_test, y_pred).ravel()
        fp_rate.append(fp / (fp + tn))        

        print(f'Fold {current_fold} complete')
        current_fold += 1

    print(f'Accuracy: {round(mean(accuracy), 4):.4f}')
    print(f'Precision: {round(mean(precision), 4):.4f}')
    print(f'Recall: {round(mean(recall), 4):.4f}')
    print(f'AUC: {round(mean(auc), 4):.4f}')
    print(f'FP Rate: {round(mean(fp_rate), 4):.4f}')
    print(f'F1 Score: {round(mean(f1), 4):.4f}')

    # Create a single model fitted from all available data.
    model = get_model()
    model.fit(X, y)
    with open(args.model, 'wb') as out_file:
        pickle.dump(model, out_file, protocol=pickle.HIGHEST_PROTOCOL)
    print(f'Saved trained model to {args.model}')


if __name__ == '__main__':
    main()

