import pandas as pd
import pickle

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

import configuration as c

df_comb = pd.read_csv(c.PATH_TO_DATASET1) # Disease combination
df_norm = pd.read_csv(c.PATH_TO_DATASET2) # Individual Disease
df_comb.drop('Unnamed: 0', axis = 1, inplace = True)
df_norm.drop('Unnamed: 0', axis = 1, inplace = True)

X = df_comb.iloc[:, 1:]
Y = df_comb.iloc[:, 0:1]

lr = LogisticRegression()
model = lr.fit(X, Y)
pickle.dump(model, open(c.MODEL_PATH,'wb'))

scores = cross_val_score(lr, X, Y, cv=5)
pickle.dump(scores, open(c.MODEL_SCORES_PATH,'wb'))

X = df_norm.iloc[:, 1:]
Y = df_norm.iloc[:, 0:1]

# List of symptoms
dataset_symptoms = list(X.columns)
pickle.dump(dataset_symptoms, open(c.SYMPTOMS_PATH,'wb'))