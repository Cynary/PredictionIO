#!/usr/bin/python
"""
Linear regression: map from feature space to rate.
Use rate to do prediction
"""
from sklearn import linear_model
from baseLearner import BaseLearner
import numpy as np
import code

class LinearRegressionLearner(BaseLearner):
    def __init__(self):
        self.name = "LinearRegressionLearner"

    def learn(self, data):
        _,train,result = zip(*data)
        X = [self.getFeatures(u) for u in train]
        y = [[number/duration] for number,duration in result]
        
        self.model = linear_model.LinearRegression()
        self.model.fit(X,y)

    def predict(self, user, period):
        ID,actions = user
        rate = self.model.decision_function(self.getFeatures(actions))[0]
        return rate*period

def Learner():
    return lambda: LinearRegressionLearner()
