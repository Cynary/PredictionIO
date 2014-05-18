#!/usr/bin/python
"""
Basic Learner: does not do any learning, but has helper functions.
Helps to extract features from data.
"""

from itertools import islice
import numpy as np

def Learner():
    return lambda: BaseLearner()

class BaseLearner():
    def __init__(self):
        self.name = "Learner"

    def inputParser(self,data):
        data = sorted(data)
        prevTime = data[0][0]
        output = []
        for t in islice(data,1,len(data)):
            output.append([t[0]-prevTime])
            prevTime = t[0]
        return np.array(output)

    def average(self, data):
        runningAverage = np.zeros(len(data[0]))
        totalElms = float(len(data))
        for elm in data:
            elm = [float(i) for i in elm]
            runningAverage += np.array(elm)/totalElms
        return runningAverage

    def variance(self, data):
        average = self.average(data)
        return self.average([(np.array([float(i) for i in d])-average)**2 for d in data])

    def getFeatures(self,userAction):
        differences = self.inputParser(userAction)
        features = self.average(userAction)
        features = np.append(features, self.variance(userAction))
        features = np.append(features, self.average(differences))
        features = np.append(features, self.variance(differences))
        
        timeStamps,ratings,movieYears = [sorted(piece) for piece in zip(*userAction)]
        otherFeatures = [
            len(timeStamps),
            timeStamps[0],
            timeStamps[-1],
            movieYears[0],
            movieYears[-1],
            ratings[0],
            ratings[-1],
        ]
        features = np.append(features, otherFeatures)
        return features

    def learn(self, data):
        pass
        
    def predict(self, user, period):
        pass
