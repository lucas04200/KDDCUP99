from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.neighbors import LocalOutlierFactor
from sklearn.metrics import RocCurveDisplay,PrecisionRecallDisplay
from sklearn.metrics import balanced_accuracy_score,confusion_matrix,roc_auc_score,f1_score,average_precision_score, precision_recall_curve, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler,RobustScaler
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from imblearn.under_sampling import TomekLinks
from sklearn.linear_model import LogisticRegression
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import label_binarize
from imblearn.combine import SMOTETomek
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline
from sklearn.utils import resample
import pickle
import matplotlib.pyplot as plt
import numpy as np 
import pandas as pd

# Tomek resampling
def Tomek(X,Y):
    tl = TomekLinks()
    X_tomek, y_Tomek = tl.fit_resample(X, Y)
    return X_tomek, y_Tomek

# Scoring pour l'apprentissage supervise 
def scoring(Ytest, Prob):
    # Calcul du seuil optimal basé sur F1 score
    precision, recall, thresholds = precision_recall_curve(Ytest, Prob)
    f1_scores = 2 * (precision * recall) / (precision + recall)
    best_idx = np.argmax(f1_scores)
    best_f1 = f1_scores[best_idx]
    best_threshold = thresholds[best_idx] if len(thresholds) > 0 else 0.5 # seuil à 0.5 de base si on ne trouve pas de meilleur seuil 
    avg_precision = average_precision_score(Ytest, Prob)    
    return best_f1, avg_precision, best_threshold

# scoring pour IsolationForest et LOF 
def scoring_non_supervised(Ytest, Prob):
    precision, recall, thresholds = precision_recall_curve(Ytest, -Prob)  # Inversion des scores
    f1_scores = 2 * (precision * recall) / (precision + recall)
    best_idx = np.argmax(f1_scores)
    best_f1 = f1_scores[best_idx]
    best_threshold = thresholds[best_idx] if len(thresholds) > 0 else 0.5 
    avg_precision = average_precision_score(Ytest, -Prob)  # Inverse des scores pour la précision moyenne
    
    return best_f1, avg_precision, best_threshold

# Dictionnaire de nos modèles
models = {
    'Logistic Regression': LogisticRegression(random_state=1),
    'RandomForestClassifier': RandomForestClassifier(n_estimators=10, random_state=1),  # Limite à 10 arbres
    'Logistic Regression SMOTE': LogisticRegression(random_state=1),
    'RandomForestClassifier SMOTE': RandomForestClassifier(n_estimators=10, random_state=1),
    'Logistic Regression Tomek': LogisticRegression(random_state=1),
    'RandomForestClassifier Tomek': RandomForestClassifier(n_estimators=10, random_state=1),
    'Logistic Regression Balanced': LogisticRegression(class_weight='balanced', random_state=1),
    'RandomForestClassifier Balanced': RandomForestClassifier(n_estimators=10, class_weight='balanced', random_state=1),
    'Isolation Forest': IsolationForest(contamination='auto', n_estimators=1000, random_state=1),  # Limite le nombre d'estimateurs
    'Local Outlier Factor': LocalOutlierFactor(novelty=True, contamination='auto', n_neighbors=200)
}

# Automatisation
def pipeline(Xtrain, Xtest, Ytrain, Ytest):
    best_model = None
    best_score = -np.inf
    probas = {}

    for name, model in models.items():
        X_train_resampled, Y_train_resampled = Tomek(Xtrain, Ytrain) if 'Tomek' in name else (Xtrain, Ytrain)
        
        # Boucle pour LOF et IsolationForest
        if isinstance(model, (LocalOutlierFactor, IsolationForest)):
            model.fit(X_train_resampled)
            Prob = -model.decision_function(Xtest)  # Anomaly (inverse si nécessaire)
            best_f1, avg_precision, best_thresh = scoring_non_supervised(Ytest, Prob)
        else:
            # Fit et proba des models 
            model.fit(X_train_resampled, Y_train_resampled)
            Prob = model.predict_proba(Xtest)[:, 1]
            best_f1, avg_precision, best_thresh = scoring(Ytest, Prob)
        
        Pred = (Prob > best_thresh).astype(int)  # Prédiction binaire basée sur le seuil
        probas[name] = Prob
        
        # Comparaison boucle
        if avg_precision > best_score:
            best_score = avg_precision
            best_model = name
        
        print(f"Model : {name} : Average Precision = {avg_precision}, Threshold = {best_thresh}")
        
        # Calcul et affichage de la matrice de confusion
        cm = confusion_matrix(Ytest, Pred)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=[0, 1])
        disp.plot(cmap=plt.cm.Blues)
        plt.title(f"Confusion Matrix for {name}")
        plt.show()
    
    # Affichage du meilleur modèle
    print(f"\nMeilleur modèle: {best_model} avec un score de {best_score}")
    
    # Affichage des courbes de précision-rappel
    fig, ax = plt.subplots(figsize=(10, 8))
    for name, prob in probas.items():
        PrecisionRecallDisplay.from_predictions(Ytest, prob, name=name, ax=ax)
    plt.show()


# RobustScaler
def RobScaler(X):
    scaler = RobustScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns, index=X.index)
    return X_scaled

# OneHotEncoder
def Encoder(X_train):
    X_encoded = pd.get_dummies(X_train, columns=['protocol_type', 'service', 'flag'])
    return X_encoded