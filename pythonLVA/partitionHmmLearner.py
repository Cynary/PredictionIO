from hmmLearner import HMMLearner
from sklearn import hmm
from sklearn.cluster import KMeans
import numpy as np
import time

# This file contains a Hidden Markov Model learner
# We are structuring the Markov Model in the following way:
#   An agent generates actions at random intervals.
#   These intervals are the output of each state, sampled from a gaussian.

# Extension: actions have descriptions, how to add it to this model?

def Learner(clusters=2):
    return lambda: PartitionHMMLearner(clusters)

class PartitionHMMLearner(HMMLearner):
    def __init__(self, clusters = 2):
        self.clusters = clusters
        self.models = None
        self.name = "HMM+Cluster(%d)" % self.clusters

    def learn(self,data):
        _,train,result = zip(*data)
        y = [[number/duration] for number,duration in result]
        
        k = KMeans(init='k-means++', n_clusters=self.clusters, n_init=40)
        k.fit(y)

        groups = [[] for i in range(self.clusters)]
        for u,y in zip(train,y):
            groups[k.predict(y)[0]].append(self.inputParser(u))
        self.models = [self.getModel(group) for group in groups]

    def predict(self, user, period):
        if self.models is None:
            return None

        userID,actions = user
        data = self.inputParser(actions)

        # Find best fit model
        model = None
        score = float("-inf")
        for m in self.models:
            newScore = m.score(data)
            if newScore > score:
                score = newScore
                model = m
        
        originalStart = model.startprob_
        model.startprob_ = model.predict_proba(data)[-1]

        n = 1
        while sum(model.sample(n)[0]) <= period:
            n = n+1
        predicted = n-1
        model.startprob_ = originalStart
        
        return predicted
