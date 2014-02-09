#!/usr/bin/python
"""
Test the "dumb" solution to LVA:
Look at the rate of rating (rates/time), and predict number of ratings in the future
by taking the expected value: rate*time.
If called from the command line, it takes the data files, and a date (YYYY-MM-DD 
format), and for every user, it takes the ratings before YYYY-MM-DD to figure out the
rate, and uses the ratings including and after the date to see how close the
prediction is to the actual case.
"""

import parserNF
import code
import os
import time
import datetime

inf = float("inf")

year,month,day = -inf,-inf,-inf

# Prediction error calculation.
# At the moment, it is the square
def predictError(predicted,actual):
    return (predicted-actual)**2

# Compare year/month/day dates.
# Returns true if the first date is smaller than the second
# def cmpDate((fYear,fMonth,fDay), (sYear,sMonth,sDay)):
#     return fYear < sYear and fMonth < sMonth and fDay < sDay
# No longer used

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
#   to later be reduced.
def mapFn(dataPoint):
    # Point date
    customerID,year,month,day = dataPoint
    timestamp = getTimeStamp(year,month,day)
    return (customerID,timestamp)

# MapReduce style function.
# Gets list of timestamps of ratings from mapFn
# Calculates the prediction, and returns the error for this user
# (square of difference)
# Arguments
#   values: list of timestamps from mapFn
# Ouptut
#   error for this customer
def reduceFn(key, values):
    global year,month,day
    res = {'train': 0, 'test': 0}

    # Start and end timestamps (used to calculate period duration for training and
    # prediction)
    startTimeStamp = inf
    endTimeStamp = -inf

    # "cut" timestamp of the date when testing data starts.
    cutTimeStamp = getTimeStamp(year,month,day)
    
    for timeStamp in values:
        # If the timestamp is before the "cut", then this is train, otherwise test.
        before = timeStamp < cutTimeStamp
        res['train' if before else 'test'] += 1
        
        # Update start and end timestamps.
        if startTimeStamp > timeStamp:
            startTimeStamp = timeStamp
        if endTimeStamp < timeStamp:
            endTimeStamp = timeStamp

    # No training data, just return 0
    if cutTimeStamp <= startTimeStamp:
        return 0
        
    # Calculate training and test durations
    trainDuration = max(0,cutTimeStamp - startTimeStamp)
    testDuration = max(0,endTimeStamp - cutTimeStamp)

    # Calculate the rate, and use it to make a prediction.
    # Note: assuming python3, so this is float division
    rate = res['train']/trainDuration
    prediction = rate * testDuration

    error = predictError(prediction,res['test'])
    return error

# Calculate the total error
if __name__ == "__main__":
    year,month,day = 2005,1,1
    # Parse the points
    movieInfo = parserNF.parseMovies(getMoviesPath())
    #pointsList = parserNF.parseFiles(getDataPathList(), movieInfo)

    # mapped will contain a map from customerID to timestamp
    mapped = {}
    for path in getDataPathList():
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

    code.interact(local=locals())

    # for point in pointsList:
    #     # Get customerID,timestamp
    #     key,value = mapFn(point)
    #     if key in mapped:
    #         mapped[key].append(value)
    #     else:
    #         mapped[key] = [value]

    # Calculate total error
    totalError = 0
    for key,values in mapped.items():
        error = reduceFn(key,values)
        totalError += error
        if totalError == inf or error == inf:
            code.interact(local=locals())

    print(totalError)