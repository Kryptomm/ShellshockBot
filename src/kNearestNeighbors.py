from math import sqrt
from threading import Thread

def hammingDistanceModified(newPointVec, dataVec):
    points = 0
    for i in range(len(newPointVec)):
        if newPointVec[i] != dataVec[i] : points += 1
    return points

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
def singleThreadfindCategory(newPoint, data, fixedK=1):
    ns = neighborStore(fixedK)

    for d in data:
        distance = hammingDistanceModified(newPoint, d[0])
        ns.push(distance, d[1])
    return ns.mostSeenCategory()

def multiThreadHelper(newPoint, data, targetArray):
    ns = neighborStore(1)
    for d in data:
        distance = hammingDistanceModified(newPoint, d[0])
        ns.push(distance, d[1])
    targetArray.extend(ns.neighbors)

def multiThreadfindCategory(newPoint, data, numThreads, fixedK=1):
    chunked_list = list()
    chunk_size = int(len(data)/numThreads)
    for i in range(0, len(data), chunk_size):
        chunked_list.append(data[i:i+chunk_size])
    
    threads = []
    results = []
    for i in range(0, len(chunked_list)):
        t = Thread(target=multiThreadHelper, args=(newPoint, chunked_list[i], results))
        threads.append(t)
    for t in threads: t.start()
    for t in threads: t.join()
    ns = neighborStore(fixedK)
    for r in results:
        ns.push(r[0],r[1])
        print(r)
    return ns.mostSeenCategory()