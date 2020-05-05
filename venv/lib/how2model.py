import tensorflow
import keras
import pandas as pd
import numpy as np
import sklearn
import matplotlib.pyplot as pyplot
from sklearn import linear_model, preprocessing
from sklearn.utils import shuffle
from pandas import DataFrame
import pickle

data = pd.read_csv("leo_new_data.csv")

data2 = data[["APOGEE", "PERIGEE", "INCLINATION", "DECAY", "PERIOD", "RCS_SIZE"]]

data_clean = pd.DataFrame(data2)

data_clean.dropna(subset = ['APOGEE'], inplace=True)
data_clean.dropna(subset = ['PERIGEE'], inplace=True)
data_clean.dropna(subset = ['PERIOD'], inplace=True)
data_clean.dropna(subset = ['INCLINATION'], inplace=True)
data_clean.dropna(subset = ['DECAY'], inplace=True)

nan_value = float("NaN")
data_clean.replace("", nan_value, inplace=True)
data_clean.dropna(subset = ['RCS_SIZE'], inplace=True)

data_clean.reset_index(drop=True, inplace=True)

le = preprocessing.LabelEncoder()
RCS_SIZE = le.fit_transform(list(data_clean["RCS_SIZE"]))
joined = DataFrame(RCS_SIZE, columns=["rcs_size"])


xdata = data_clean.drop(['RCS_SIZE'], 1)

xdata['rcs_size'] = joined
print(xdata)
xdata.dropna(subset = ['rcs_size'], inplace=True)
print(xdata)
DECAY = xdata['DECAY'].str.replace("-","").astype(int)
xdata = xdata.drop(["DECAY"], 1)

print(xdata)

predict = DECAY
x = np.array(xdata)
y = np.array(predict)

x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(x, y, test_size = 0.1)

linear = linear_model.LinearRegression()
linear.fit(x_train, y_train)
accuracy = linear.score(x_test, y_test)
print(accuracy)

# with open("how2model.pickle", "wb") as f:
#     pickle.dump(linear, f)
#
# pickle_in = open("how2model.pickle", "rb")
# linear = pickle.load(pickle_in)
