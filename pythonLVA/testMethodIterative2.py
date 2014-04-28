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
import simpleLearner
import errorFns

inf = float("inf")

# Parameters for learning, and testing, so that we don't take forever, every time
nLearning = 200
nTesting = 10000
#Learner = hmmLearner.HMMLearner
Learner = partitionHmmLearner.HMMLearner
#Learner = simpleLearner.SimpleLearner

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
    
    valid = (len(trainStamps) >= 5) and (len(testStamps) != 0)
    testDuration = testStamps[0]-trainStamps[-1] if (len(testStamps) != 0 and valid) else 0
    
    return (trainStamps, len(testStamps), testDuration, valid)

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
    
        # mapped will contain a map from customerID to a list of timeStamps
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
    
        # This is a heavy operation, so save the results
        with open("pickleDataFile", "wb") as f:
            pickle.dump(mapped, f)
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
        for customerID,timeStamps in mapped.items():
            trainStamps, testNumber, testDuration, valid = splitFn(timeStamps)
            if valid:
                train[customerID] = trainStamps
                test[customerID] = (testNumber, testDuration)
        del mapped

        # Heavy operation, save the results
        with open("pickleTrainFile", "wb") as f, open("pickleTestFile", "wb") as t:
            pickle.dump(train, f)
            pickle.dump(test, t)
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
                except:
                    print("Error occurred")
