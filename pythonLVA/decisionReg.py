#!/usr/bin/python
"""
Decision Tree: map from feature space to rate.
Use rate to do prediction
"""
from sklearn import tree
from baseLearner import BaseLearner
import numpy as np
import code

class DecisionTreeRegressionLearner(BaseLearner):
    def __init__(self):
        self.name = "DecisionTreeRegressionLearner"

    def learn(self, data):
        _,train,result = zip(*data)
        X = [self.getFeatures(u) for u in train]
        y = [number/duration for number,duration in result]
        
        self.model = tree.DecisionTreeRegressor(max_depth=6,min_samples_leaf=100)
        self.model.fit(X,y)
        with open("graphReg.dot","w") as dot_data:
            tree.export_graphviz(self.model, out_file=dot_data, feature_names=[
                "Average timestamp",
                "Average rating",
                "Average year of movie",
                "Timestamp variance",
                "Rating variance",
                "Year of movie variance",
                "Average time spacing",
                "Variance in time spacing",
                "Number of actions",
                "Earliest timestamp",
                "Most recent timestamp",
                "Earliest year of movie",
                "Most recent year of movie",
                "Worst rating",
                "Best rating",
            ])
        
    def predict(self, user, period):
        ID,actions = user
        rate = self.model.predict(self.getFeatures(actions))[0]
        return rate*period

def Learner():
    return lambda: DecisionTreeRegressionLearner()
