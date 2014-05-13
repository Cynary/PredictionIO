#!/usr/bin/python
"""
Testing framework for methods for LVA.
This tests with the netflix dataset.
This file is for the simple LVA we are trying to do first: predict the number of actions in a time period.

It tests predictors with the following interface:
  .learn(data) -- take data as a list of (customerID, [timeStamps])
  .predict(user,period) -- take a user (customerID, [timeStamps]), and predict the
    number of actions in the future "period" - period should be in seconds.
"""
from dataProcessing import *
import code
import random
import errorFns

inf = float("inf")

def getLearner(train,test,nLearning,Learner):
    trainIDs = random.sample(train.keys(), nLearning)
    learner = Learner()
    learner.learn([(ID,train[ID],test[ID]) for ID in trainIDs])
    return learner

# Prediction error calculation.
predictError = [
    errorFns.magError,
    errorFns.percentError,
    errorFns.squareError,
    errorFns.underError,
    errorFns.overError,
    ]
def getError(train,test,learner,nTesting):
    # Calculate average error
    error = [0]*len(predictError)
    for customerID,(testNumber, testDuration) in random.sample(test.items(), nTesting):
        user = (customerID, train[customerID])
        prediction = learner.predict(user, testDuration)
        for i,errorFn in enumerate(predictError):
            error[i] += errorFn(prediction, testNumber)/nTesting
    return error

import simpleLearner
import hmmLearner
import partitionHmmLearner
import combinationLearner
import linReg
import decision
import decisionReg
# Calculate the average error
if __name__ == "__main__":
    # Parameters for learning, and testing, so that we don't take forever, every time
    nLearning = 100000
    nTesting = 20000
    Learner = decisionReg.Learner()
    
    train, test = getSplitData()
    print("Data acquisition complete.")
    print("Run with %d learning samples, and %d testing samples." % (nLearning, nTesting))

    learner = getLearner(train,test,nLearning,Learner)

    print("Learning is complete, testing")

    error = getError(train,test,learner,nTesting)
    
    print("Average error:", error)
    print("%s\t%d\t%d\t%s" % (learner.name, nLearning, nTesting, '\t'.join([str(i) for i in error])))

    code.interact(local=locals())
