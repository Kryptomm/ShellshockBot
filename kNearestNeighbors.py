from math import sqrt
from random import random, randint
import time
from threading import Thread

def hammingDistanceModified(vec1, vec2, numVec1, numVec2):
    points = 0
    for i in range(len(vec1)):
        if vec1[i] == 1 and vec2[i] == 1: points += 1
    if numVec1 > numVec2: return 1-(points/numVec1)
    else: return 1-(points/numVec2)

class neighborStore:
    def __init__(self, k):
        self.neighbors = [] #[[Distance, Category]]
        self.k = k

    def push(self, value, category):
        if len(self.neighbors) < self.k: self.neighbors.append([value, category])
        else:
            values = [_[0] for _ in self.neighbors]
            maximal = max(values)
            if value < maximal:
                index = values.index(maximal)
                self.neighbors[index] = [value, category]

    def mostSeenCategory(self):
        cats = [_[1] for _ in self.neighbors]
        return max(set(cats), key = cats.count)

    def lowestValue(self):
        cats = [_[0] for _ in self.neighbors]
        return min(cats)

#data = [   [[x1,x2,...,xn], "cat1"], [[x1,x2,...,xn], "cat2"]    ]
def singleThreadfindCategory(newPoint, data, ones, fixedK=1):
    ns = neighborStore(fixedK)

    for d in data:
        distance = hammingDistanceModified(newPoint, d[0], ones,d[2])
        ns.push(distance, d[1])
    return ns.mostSeenCategory()

def multiThreadHelper(newPoint, data, targetArray, ones):
    ns = neighborStore(1)
    for d in data:
        distance = hammingDistanceModified(newPoint, d[0], ones, d[2])
        ns.push(distance, d[1])
    targetArray.extend(ns.neighbors)

def multiThreadfindCategory(newPoint, data, numThreads, ones, fixedK=1):
    chunked_list = list()
    chunk_size = int(len(data)/numThreads)
    for i in range(0, len(data), chunk_size):
        chunked_list.append(data[i:i+chunk_size])
    
    threads = []
    results = []
    for i in range(0, len(chunked_list)):
        t = Thread(target=multiThreadHelper, args=(newPoint, chunked_list[i], results, ones))
        threads.append(t)
    for t in threads: t.start()
    for t in threads: t.join()
    ns = neighborStore(fixedK)
    for r in results:
        ns.push(r[0],r[1])
    return ns.mostSeenCategory()