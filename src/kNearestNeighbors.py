import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder

knnWindModel = None
knnWeaponModel = None

def loadWindKNN():
    global knnWind
    dataWind = pd.read_csv('data/WindPixels.csv')
    XWind  = dataWind.drop(columns='label').values
    yWind  = dataWind['label'].values
    knnWindModel = KNeighborsClassifier(n_neighbors=1, metric='euclidean')
    knnWindModel.fit(XWind, yWind)

    
def loadWeaponKNN():
    global knnWeapon
    dataWeapon = pd.read_csv('data/WindPixels.csv')
    XWeapon  = dataWeapon.drop(columns='label').values
    yWeapon  = dataWeapon['label'].values
    knnWeaponModel = KNeighborsClassifier(n_neighbors=1, metric='euclidean')
    knnWeaponModel.fit(XWeapon, yWeapon)


def knnWind(newPoint):
    global knnWind
    newPoint = np.array(newPoint)
    newPoint = newPoint.reshape(1, -1)
    predicted_category = knnWindModel.predict(newPoint)
    
    return predicted_category[0]

def knnWeapon(newPoint):
    global knnWeapon
    return "shot"