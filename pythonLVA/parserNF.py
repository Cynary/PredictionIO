#!/usr/bin/python
import code
import argparse

# DataPoint is the parent class for all datapoints.
class DataPoint:
    pass

# NetflixDataPoint refers to specific data points
class NetflixDataPoint(DataPoint):
    # Creates the DataPoint object.
    # Arguments
    #   dataString: "CustomerID,Rating,YYYY-MM-DD".
    #   movieID: ID of the movie.
    # Requirements
    #   dataString needs to be correctly formatted, and movieID is an integer.
    # Effects
    #   Parses the dataString, and creates the object.
    def __init__(self, dataString, movieID):
        pass

    
    
# Arguments
#   pathList: list of paths to netflix data files.
# Requirements
#   Every file path must refer to a file with valid netflix data.
# Ouptut
#   list of DataPoints representing the netflix data points in the files.
def parseFiles(pathList):
    pointsList = []
    
    # Iterate over all files
    for path in pathList:
        with open(path) as dataFile:
            # The parseFile function is a generator.
            # It parses individual data points, until done with the file.
            parser = parseFile(dataFile)
            for dataPoint in parser:
                pointsList.append(dataPoint)
    return pointsList

# Generator function for the data points in a specific file object.
# parses netflix datafiles, and returns a DataPoint object for each point in the file
# Arguments
#  dataFile: file object for a netflix data file.
# Requirements
#  dataFile must be a valid netflix data file. Does not check for inconsistencies, or
#  formatting.
# Ouput
#  generator, iterates over individual datapoints in the file.
# valid netflix formatting (taken from the README):
# TRAINING DATASET FILE DESCRIPTION
# ================================================================================
#
# The file "training_set.tar" is a tar of a directory containing 17770 files, one
# per movie.  The first line of each file contains the movie id followed by a
# colon.  Each subsequent line in the file corresponds to a rating from a customer
# and its date in the following format:
#
# CustomerID,Rating,Date
#
# - MovieIDs range from 1 to 17770 sequentially.
# - CustomerIDs range from 1 to 2649429, with gaps. There are 480189 users.
# - Ratings are on a five star (integral) scale from 1 to 5.
# - Dates have the format YYYY-MM-DD.
def parseFile(dataFile):
    # Expect first line to contain (ID):\n, and want to extract ID
    movieID = int(dataFile.readline()[:-2])
    for line in iter(lambda: dataFile.readline()[:-2], ''):
        yield NetflixDataPoint(line, movieID)

if __name__ == "__main__":
    # Need to add arguments for movies, and qualifying files.
    
    # Parsing command line arguments and automating the help message
    # There are two command line argument types: -h show help message;
    # list of relative file paths (wildcards accepted) with the Netflix data.
    # ArgumentParser takes care of incorrectly formatted arguments, and
    # help message.
    parser = argparse.ArgumentParser(description="Parse netflix data files")
    parser.add_argument("files",
                        metavar="mv_*.txt",
                        help="path of a netflix dataset file",
                        nargs="+",
                        type=str
    )
    # pathList is a list of all the file paths passed to the file.
    pathList = parser.parse_args().files

    # pointsList is the list of DataPoints with the Netflix data
    pointsList = parseFiles(pathList)

    # Drop user into a shell, with the current environment
    code.interact(local=locals())
