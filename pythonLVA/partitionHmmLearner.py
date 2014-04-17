from itertools import islice
from sklearn import hmm
from sklearn.cluster import KMeans
import numpy as np
import time

# This file contains a Hidden Markov Model learner
# We are structuring the Markov Model in the following way:
#   An agent generates actions at random intervals.
#   These intervals are the output of each state, sampled from a gaussian.

# Extension: actions have descriptions, how to add it to this model?

class HMMLearner:
    def __init__(self, clusters = 2):
        self.clusters = clusters
        self.models = None
        self.name = "HMM+Cluster(%d)" % self.clusters

    # Data is input as lists of timestamps, and we want lists of intervals between
    # actions.
    # This function takes a list of (action, time) items, and outputs a list of
    # intervals
    # data: list of (time) -> list of (interval)
    # This will actually be a list of single element lists, so that they can be used
    # to train the HMM of scikit-learn
    # Note: you should call this function for a single agent's data
    def inputParser(self,data):
        data = sorted(data)
        prevTime = data[0][0]
        output = []
        for t in islice(data,1,len(data)):
            output.append([t[0]-prevTime])
            prevTime = t[0]
        return np.array(output)

    def learn(self,data):
        k = KMeans(init='k-means++', n_clusters=self.clusters, n_init=10)
        k.fit([[float(len(u))] for ID,u in data])
        print(k.cluster_centers_)
        groups = [[] for i in range(self.clusters)]
        for ID,u in data:
            groups[k.predict(float(len(u)))[0]].append(self.inputParser(u))
        self.models = [self.getModel(group) for group in groups]

    def predict(self, user, period):
        if self.models is None:
            return None

        userID,timeStamps = user
        data = self.inputParser(timeStamps)

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

    # This function returns an HMM trained on the input data. Data should be a list of
    # intervals between actions.
    # It tries multiple models, until it runs out of time, or finds a local minima in
    # the score.
    # It simply iterates on the number of states.
    def getModel(self,data, timeout=600):
        start = time.time()
        prevModel = None
        prevScore = float("-inf")
        n = 1
        while time.time()-start < timeout and n < 7: # n > 6 often crashes with few data points :(
            # Start with a fair start prob/transition matrix
            startprob = np.array([1./n for i in range(n)])
            transmat = np.array(np.array([startprob for i in range(n)]))
            model = hmm.GaussianHMM(n, "full", startprob, transmat, n_iter=100)
            try:
                model.fit(data)
                score = sum([1./len(data)*model.score(d) for d in data])
            except ValueError:
                return prevModel
            print(n,score)
            if score < prevScore: # Local maxima found
                return prevModel
            else:
                prevModel = model
                prevScore = score
            n = n+1
        return prevModel
