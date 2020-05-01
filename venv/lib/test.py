import tensorflow
import keras
import pandas as pd
import numpy as np
import sklearn
import matplotlib.pyplot as pyplot
from sklearn import linear_model, preprocessing
from sklearn.utils import shuffle
from pandas import DataFrame


data = pd.read_csv("satcat-destorydatevalid.csv")

data_clean = data.drop(['INTLDES', 'PERIOD', 'INCLINATION', 'NORAD_CAT_ID','OBJECT_TYPE','SATNAME','COUNTRY','LAUNCH', 'SITE', 'COMMENT', 'COMMENTCODE', 'FILE', 'RCSVALUE', 'LAUNCH_NUM','LAUNCH_PIECE','CURRENT','OBJECT_NAME','OBJECT_ID','OBJECT_NUMBER'], axis=1)

data_clean.dropna(subset = ['APOGEE'], inplace=True)
data_clean.dropna(subset = ['PERIGEE'], inplace=True)
# data_clean.dropna(subset = ['PERIOD'], inplace=True)
# data_clean.dropna(subset = ['INCLINATION'], inplace=True)

nan_value = float("NaN")
data_clean.replace("", nan_value, inplace=True)
data_clean.dropna(subset = ['RCS_SIZE'], inplace=True)

le = preprocessing.LabelEncoder()
RCS_SIZE = le.fit_transform(list(data_clean["RCS_SIZE"]))
joined = DataFrame(RCS_SIZE, columns=["rcs_size"])

xdata = data_clean
xdata['rcs_size'] = joined
xdata.dropna(subset = ['rcs_size'], inplace=True)
DECAY = xdata['DECAY'].str[:-6].astype(int)
LIFE = DECAY - xdata['LAUNCH_YEAR']
xdata = data_clean.drop(["DECAY", "RCS_SIZE"], 1)

# print(xdata.head(5))
predict = LIFE
x = np.array(xdata)
y = np.array(predict)

x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(x, y, test_size = 0.1)

linear = linear_model.LinearRegression()
linear.fit(x_train, y_train)
accuracy = linear.score(x_test, y_test)
print(accuracy)

print("Coefficient: \n", linear.coef_)
print("Intercept: \n", linear.intercept_)
#
# p = "LAUNCH_YEAR"
# pyplot.scatter(xdata[p], predict)
# pyplot.xlabel(p)
# pyplot.ylabel("decay prediction")
# pyplot.show()