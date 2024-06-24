import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier

knnWindModel = None
knnWeaponModel = None

def loadWindKNN():
    global knnWindModel
    dataWind = pd.read_csv('data/WindPixels.csv')
    XWind = dataWind.drop(columns='label').values
    yWind = dataWind['label'].values
    knnWindModel = KNeighborsClassifier(n_neighbors=1, metric='euclidean')
    knnWindModel.fit(XWind, yWind)
    
def loadWeaponKNN():
    global knnWeaponModel
    dataWeapon = pd.read_csv('data/WeaponPixels.csv')
    XWeapon = dataWeapon.drop(columns='label').values
    yWeapon = dataWeapon['label'].values
    knnWeaponModel = KNeighborsClassifier(n_neighbors=1, metric='euclidean')
    knnWeaponModel.fit(XWeapon, yWeapon)

def knnWind(newPoint):
    global knnWindModel
    newPoint = np.array(newPoint).reshape(1, -1)
    predicted_category = knnWindModel.predict(newPoint)
    return predicted_category[0]

def knnWeapon(newPoint):
    global knnWeaponModel
    newPoint = np.array(newPoint).reshape(1, -1)
    predicted_category = knnWeaponModel.predict(newPoint)
    return predicted_category[0]
