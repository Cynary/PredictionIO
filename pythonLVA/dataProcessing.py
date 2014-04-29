import parserNF
import pickle
import os
import time
import datetime

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
# Gets NetflixDataPoints, and returns tuples with action descriptors:
#   (customerID,(timeStamp,rating,movieYear))
# timeStamp - timestamp of when the rating was performed.
# rating - what the rating was
# movieYear - year of the movie being rated
# Arguments
#   dataPoint: NetflixDataPoint to process
# Ouptut
#   MapReduce style output (customerID,(timeStamp,rating,movieYear)),
#   to later be reduced (processed).
def mapFn(dataPoint):
    # Point date
    customerID,year,month,day,rating,movieYear = [int(i) if i != 'NULL' else 1990 for i in dataPoint]
    timestamp = getTimeStamp(year,month,day)
    return (customerID,(timestamp,rating,movieYear))

# Gets the data from a user as a list of (timeStamp,rating,movieYear)
# Returns a split of that data into training and testing sets.
# The amount of data on each split will depend on fracTrain.
# Returns: ([trainData], number of testing actions, testDuration, valid)
# valid indicates whether we should use this data point or not (we should only use
# datapoints with 2 or more datapoints in the trainSet)
def splitFn(actions, fracTrain=0.5):
    endTrain = max(int(fracTrain*len(actions)), 5)
    actions = sorted(actions)
    train = actions[:endTrain]
    test = actions[endTrain:]
    
    valid = (len(train) >= 5) and (len(test) != 0)
    # Note: these durations are accurate to within a day, so we add a day.
    # Otherwise, the following bug happened: a lot of ratings in one day, and testDuration was 0.
    oneDay = 24*60*60 # seconds
    testDuration = oneDay+test[0][0]-train[-1][0] if (len(test) != 0 and valid) else 0
    
    return (train, len(test), testDuration, valid)

def getData():
    # Check if the result already exists, and if it does, return
    print("Processing NetFlix data set")
    try:
        # SO MUCH WIN!!!
        with open("pickleDataFile", "rb") as f:
            mapped = pickle.load(f)
    except FileNotFoundError:
        # Parse the points
        movieInfo = parserNF.parseMovies(getMoviesPath())
    
        # mapped will contain a map from customerID to a list of timeStamps, and ratings
        mapped = {}
        i = 0
        for path in getDataPathList():
            if i%100 == 0:
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
    print("Splitting NetFlix dataset")
    try:
        # EVEN MORE WIN!!
        with open("pickleTrainFile", "rb") as f, open("pickleTestFile", "rb") as t:
            train = pickle.load(f)
            test = pickle.load(t)
    except FileNotFoundError:
        mapped = getData()
        # Get the train/test splits.
        train = {}
        test = {}
        for customerID,actions in mapped.items():
            trainActions, testResult, testDuration, valid = splitFn(actions)
            if valid:
                train[customerID] = trainActions
                test[customerID] = (testResult, testDuration)
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
