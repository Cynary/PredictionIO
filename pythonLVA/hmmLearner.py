from baseLearner import BaseLearner
from sklearn import hmm
import numpy as np
import time

# This file contains a Hidden Markov Model learner
# We are structuring the Markov Model in the following way:
#   An agent generates actions at random intervals.
#   These intervals are the output of each state, sampled from a gaussian.

# Extension: actions have descriptions, how to add it to this model?

def Learner():
    return lambda: HMMLearner()

class HMMLearner(BaseLearner):
    def __init__(self):
        self.name = "HMM"

    def learn(self,data):
        _,train,_ = zip(*data)
        self.model = self.getModel([self.inputParser(u) for u in train])

    def predict(self, user, period):
        userID,timeStamps = user
        data = self.inputParser(timeStamps)
        originalStart = self.model.startprob_
        self.model.startprob_ = self.model.predict_proba(data)[-1]

        n = 1
        while sum(self.model.sample(n)[0]) <= period:
            n = n+1
        predicted = n-1
        self.model.startprob_ = originalStart
        
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
        while time.time()-start < timeout and n < 7:
            # Start with a fair start prob/transition matrix
            startprob = np.array([1./n for i in range(n)])
            transmat = np.array(np.array([startprob for i in range(n)]))
            model = hmm.GaussianHMM(n, "full", startprob, transmat, n_iter=100)
            try:
                model.fit(data)
                score = sum([1./len(data)*model.score(d) for d in data])
            except:
                return prevModel
            print(n,score)
            if score < prevScore: # Local maxima found
                return prevModel
            else:
                prevModel = model
                prevScore = score
            n = n+1
        return prevModel
