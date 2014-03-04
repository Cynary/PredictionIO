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
import parserNF
import code
import os
import time
import datetime
from hmmLearn import HMMLearner

inf = float("inf")

# Prediction error calculation.
# At the moment, it is the percent error
def predictError(predicted,actual):
    return abs(predicted/actual-1.)

# Arguments
#   year,month,day
# Output
#   timestamp at midnight of that day, month, and year.
def getTimeStamp(year,month,day):
    # Getting the timestamp
    # http://stackoverflow.com/questions/9223905/python-timestamp-from-day-month-year
    dt = datetime.datetime(year=year, month=month, day=day)
    return time.mktime(dt.timetuple())
    
# Returns a list with all the data file paths
def getDataPathList():
    directory = "/home/rgomes/projects/predictionio/download/training_set"
    return [os.path.join(directory, f) for f in os.listdir(directory)]

def getMoviesPath():
    return "/home/rgomes/projects/predictionio/download/movie_titles.txt"

# MapReduce style function.
# Gets NetflixDataPoints, and returns tuples
#   (customerID,timeStamp)
# timeStamp - timestamp of when the rating was performed.
# Arguments
#   dataPoint: NetflixDataPoint to process
# Ouptut
#   MapReduce style output (customerID,timeStamp),
#   to later be reduced (processed).
def mapFn(dataPoint):
    # Point date
    customerID,year,month,day = dataPoint
    timestamp = getTimeStamp(year,month,day)
    return (customerID,timestamp)

# Gets the data from a user as [timeStamps]
# Returns a split of that data into training and testing sets.
# The amount of data on each split will depend on fracTrain.
# Returns: ([trainingStamps], [testingStamps], testDuration, valid)
# valid indicates whether we should use this data point or not (we should only use
# datapoints with 2 or more datapoints in the trainSet)
def splitFn(timeStamps, fracTrain=0.5):
    endTrain = max(int(fracTrain*len(timeStamps)), 5)
    trainStamps = timeStamps[:endTrain]
    testStamps = timeStamps[endTrain:]
    
    valid = len(trainStamps) >= 5
    testDuration = testStamps[0]-trainStamps[-1] if (len(testStamps) and valid) != 0 else 0
    
    return (trainStamps, len(testStamps), testDuration, valid)

# Calculate the total error
if __name__ == "__main__":
    # # Parse the points
    # movieInfo = parserNF.parseMovies(getMoviesPath())

    # # mapped will contain a map from customerID to a list of timeStamps
    # mapped = {}
    # i = 0
    # for path in getDataPathList():
    #     if i%10 == 0:
    #         print("Processed", i, "files.")
    #     i = i+1
    #     with open(path) as dataFile:
    #         # The parseFile function is a generator.
    #         # It parses individual data points, until done with the file.
    #         parser = parserNF.parseFile(dataFile,movieInfo)
    #         for dataPoint in parser:
    #             key,value = mapFn(dataPoint)
    #             if key in mapped:
    #                 mapped[key].append(value)
    #             else:
    #                 mapped[key] = [value]

    # # This always takes forever, this is the last time
    import pickle
    # with open("pickleDataFile", "wb") as f:
    #     pickle.dump(mapped, f)

    # SO MUCH WIN!!!
    # with open("pickleDataFile", "rb") as f:
    #     mapped = pickle.load(f)
    
    # # Get the train/test splits.
    # train = {}
    # test = {}
    # for customerID,timeStamps in mapped.items():
    #     trainStamps, testNumber, testDuration, valid = splitFn(timeStamps)
    #     if valid:
    #         train[customerID] = trainStamps
    #         test[customerID] = (testNumber, testDuration)
    # del mapped

    # with open("pickleTrainFile", "wb") as f, open("pickleTestFile", "wb") as t:
    #     pickle.dump(train, f)
    #     pickle.dump(test, t)

    # EVEN MORE WIN!!
    with open("pickleTrainFile", "rb") as f, open("pickleTestFile", "rb") as t:
        train = pickle.load(f)
        test = pickle.load(t)

    print("Reading, and mapping is complete. Learning now.")
    
    learner = HMMLearner()
    learner.learn(train.items())

    print("Learning is complete now.")

    # Calculate total error
    totalError = 0
    nusers = len(train)
    print("Number of users: ", nusers) # 480189
    for customerID,(testNumber, testDuration) in test.items():
        user = (customerID, train[customerID])
        prediction = learner.predict(user, testDuration)
        totalError += predictError(prediction, testNumber)

    print("Average percentage error: ", totalError/nusers) # 28456820.787530653
    print("Average number of actions: ", nactions/nusers) # 209.25199660966828
    
    code.interact(local=locals())
