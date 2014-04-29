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
from testMethod import *

# Calculate the average error
if __name__ == "__main__":
    nLearners = [500,1000,1500,2000,2500,3000]
    Learner = partitionHmmLearner.HMMLearner
    
    train, test = getSplitData()
    print("Data acquisition complete, reading now.")

    for nLearning in nLearners:
        j = 0
        with open("output", "a") as f:
            # Repeat 5 times for each n
            while j < 5:
                try:
                    print("Run #%d with %d learning samples, and %d testing samples." % (j+1, nLearning, nTesting))
                    learner = getLearner(train,test,nLearning,Learner)
                    print("Learning is complete, testing")
                    error = getError(train,test,learner,nTesting)
                    print("Average error:", error)
                    print("%s\t%d\t%d\t%s" % (learner.name, nLearning, nTesting, '\t'.join([str(i) for i in error])), file=f)
                    j = j+1
                except KeyboardInterrupt:
                    raise
                # except Exception as e:
                #     print("Error occurred",str(e))
