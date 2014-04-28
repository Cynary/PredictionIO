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
import pickle
import random
import hmmLearner
import partitionHmmLearner
import partitionHmmLearner2
import simpleLearner
import errorFns
import combinationLearner

inf = float("inf")

# Parameters for learning, and testing, so that we don't take forever, every time
nLearning = 200
nTesting = 10000
#Learner = hmmLearner.HMMLearner
#Learner = partitionHmmLearner.HMMLearner
#Learner = simpleLearner.SimpleLearner
#Learner = combinationLearner.CombinationLearner
Learner = partitionHmmLearner2.HMMLearner

# Prediction error calculation.
predictError = [
    errorFns.magError,
    errorFns.percentError,
    errorFns.squareError,
    ]

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
    directory = "../download/training_set"
    return [os.path.join(directory, f) for f in os.listdir(directory)]

def getMoviesPath():
    return "../download/movie_titles.txt"

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
    customerID,year,month,day,rating,movieYear = dataPoint
    timestamp = getTimeStamp(year,month,day)
    return (customerID,(timestamp,rating,movieYear))

# Gets the data from a user as [timeStamps]
# Returns a split of that data into training and testing sets.
# The amount of data on each split will depend on fracTrain.
# Returns: ([trainingStamps], [testingStamps], testDuration, valid)
# valid indicates whether we should use this data point or not (we should only use
# datapoints with 2 or more datapoints in the trainSet)
def splitFn(actions, fracTrain=0.5):
    endTrain = max(int(fracTrain*len(actions)), 5)
    train = actions[:endTrain]
    test = actions[endTrain:]
    
    valid = (len(train) >= 5) and (len(test) != 0)
    testDuration = test[0][0]-train[-1][0] if (len(test) != 0 and valid) else 0
    
    return (train, len(test), testDuration, valid)

def getData():
    # Check if the result already exists, and if it does, return
    try:
        # SO MUCH WIN!!!
        with open("pickleDataFile", "rb") as f:
            mapped = pickle.load(f)
    except FileNotFoundError:
        print("Processing NetFlix data set")
        # Parse the points
        movieInfo = parserNF.parseMovies(getMoviesPath())
    
        # mapped will contain a map from customerID to a list of timeStamps, and ratings
        mapped = {}
        i = 0
        for path in getDataPathList():
            if i%10 == 0:
                print("Processed", i, "files.")
            i = i+1
            with open(path) as dataFile:
                # The parseFile function is a generator.
                # It parses individual data points, until done with the file.
                parser = parserNF.parseFile(dataFile,movieInfo)
                for dataPoint in parser:
                    key,value = mapFn(dataPoint)
                    if key in mapped:
                        mapped[key].append(value)
                    else:
                        mapped[key] = [value]
    
        for customerID in list(mapped.keys()):
            if len(mapped[customerID]) < 5:
                del mapped[customerID]

        # This is a heavy operation, so save the results
        with open("pickleDataFile", "wb") as f:
            p = pickle.Pickler(f)
            p.fast = True
            p.dump(mapped)
    print("Done Processing")
    return mapped

def getSplitData():
    try:
        # EVEN MORE WIN!!
        with open("pickleTrainFile", "rb") as f, open("pickleTestFile", "rb") as t:
            train = pickle.load(f)
            test = pickle.load(t)
    except FileNotFoundError:
        print("Splitting NetFlix dataset")
        mapped = getData()
        # Get the train/test splits.
        train = {}
        test = {}
        for customerID,actions in mapped.items():
            trainActions, testNumber, testDuration, valid = splitFn(actions)
            if valid:
                train[customerID] = trainActions
                test[customerID] = (testNumber, testDuration)
        del mapped

        # Heavy operation, save the results
        with open("pickleTrainFile", "wb") as f, open("pickleTestFile", "wb") as t:
            pTrain = pickle.Pickler(f)
            pTest = pickle.Pickler(t)
            pTrain.fast = True
            pTest.fast = True
            pTrain.dump(train)
            pTest.dump(test)
    print("Done Splitting")
    return (train, test)

# Calculate the average error
if __name__ == "__main__":
    train, test = getSplitData()

    print("Data acquisition complete, reading now.")

    nLearners = [500,1000,1500,2000,2500,3000]
    for nLearning in nLearners:
        j = 0
        with open("output", "a") as f:
            # Repeat 5 times for each n
            while j < 5:
                try:
                    print("Run #%d with %d learning samples, and %d testing samples." % (j+1, nLearning, nTesting))
                    learner = Learner()
                    learner.learn(random.sample(train.items(), nLearning))
                    
                    print("Learning is complete, testing")
                    
                    # Calculate average error
                    error = [0]*len(predictError)
                    print("Testing for", nTesting, "data points.")
                    for customerID,(testNumber, testDuration) in random.sample(test.items(), nTesting):
                        user = (customerID, train[customerID])
                        prediction = learner.predict(user, testDuration)
                        for i,errorFn in enumerate(predictError):
                            error[i] += errorFn(prediction, testNumber)/nTesting
                            
                    print("Average error:", error)

                    print("%s\t%d\t%d\t%s" % (learner.name, nLearning, nTesting, '\t'.join([str(i) for i in error])), file=f)
                    j = j+1
                except KeyboardInterrupt:
                    raise
                # except Exception as e:
                #     print("Error occurred",str(e))
