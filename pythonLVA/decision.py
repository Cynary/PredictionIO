#!/usr/bin/python
"""
Decision Tree: map from feature space to rate.
Use rate to do prediction
"""
from sklearn import tree
from baseLearner import BaseLearner
import numpy as np
import code

class DecisionTreeLearner(BaseLearner):
    def __init__(self):
        self.name = "DecisionTreeLearner"

    def learn(self, data):
        _,train,result = zip(*data)
        X = [self.getFeatures(u) for u in train]
        y = [number/duration for number,duration in result]
        
        self.model = tree.DecisionTreeClassifier()
        self.model.fit(X,y)

    def predict(self, user, period):
        ID,actions = user
        rate = self.model.predict(self.getFeatures(actions))[0]
        return rate*period

def Learner():
    return lambda: DecisionTreeLearner()
