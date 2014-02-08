#!/usr/bin/python
import code
import argparse
from dataPoints import NetflixDataPoint
    
# Arguments
#   titlesPath: path of the movies_title.txt file
# Requirements
#   The file must follow the specification described in the README
# Output
#   A movie info data structure. It is to be used by the parseFiles function when
#   forming datapoints.
# README Specification:
# MOVIES FILE DESCRIPTION
# ================================================================================
#
# Movie information in "movie_titles.txt" is in the following format:
#
# MovieID,YearOfRelease,Title
#
# - MovieID do not correspond to actual Netflix movie ids or IMDB movie ids.
# - YearOfRelease can range from 1890 to 2005 and may correspond to the release of
#   corresponding DVD, not necessarily its theaterical release.
# - Title is the Netflix movie title and may not correspond to 
#   titles used on other sites.  Titles are in English.
def parseMovies(titlesPath):
    movieInfo = {}
    with open(titlesPath,encoding="ISO-8859-1") as titlesFile:
        for movie in titlesFile:
            (ID,year,title) = movie[:-2].split(',',2)
            movieInfo[int(ID)] = (year,title)
    return movieInfo

# Arguments
#   pathList: list of paths to netflix data files.
#   movieInfo: information about movies. Created by the parseMovies function.
#     If no movieInfo was created, it should be an empty dictionary.
# Requirements
#   Every file path must refer to a file with valid netflix data.
# Ouptut
#   list of DataPoints representing the netflix data points in the files.
def parseFiles(pathList, movieInfo):
    pointsList = []
    
    # Iterate over all files
    # This could be done in parallel
    for path in pathList:
        with open(path) as dataFile:
            # The parseFile function is a generator.
            # It parses individual data points, until done with the file.
            parser = parseFile(dataFile,movieInfo)
            for dataPoint in parser:
                pointsList.append(dataPoint)
    return pointsList

# Generator function for the data points in a specific file object.
# parses netflix datafiles, and returns a DataPoint object for each point in the file
# Arguments
#  dataFile: file object for a netflix data file.
#  movieInfo: information about movies. Created by the parseMovies function
#    If no movieInfo was created, it should be an empty dictionary.
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
def parseFile(dataFile,movieInfo):
    # Expect first line to contain (ID):\n, and want to extract ID
    movieID = int(dataFile.readline()[:-2])
    # movieInfo is a map from IDs to information data structures, returned by parseMovies
    currentMovie = movieInfo.get(movieID, None)
    for line in dataFile:
        line = line[:-2]
        yield NetflixDataPoint(line, movieID, currentMovie)

# Called from the command line
if __name__ == "__main__":
    # Parsing command line arguments and automating the help message
    # There are three command line argument types: -h show help message;
    # -m movie_titles.txt_file
    # list of relative file paths (wildcards accepted) with the Netflix data.
    # ArgumentParser takes care of incorrectly formatted arguments, and
    # help message.
    parser = argparse.ArgumentParser(description="Parse netflix data files")
    parser.add_argument("files",
                        metavar="mv_ID.txt",
                        help="path of a netflix dataset file",
                        nargs="+",
                        type=str
    )
    parser.add_argument("--titles","-t",
                        metavar="movie_titles.txt",
                        help="path of the movie title dataset file",
                        nargs=1,
                        type=str
    )
    # pathList is a list of all the file paths passed to the file.
    parseResults = parser.parse_args()
    pathList = parseResults.files
    titlesPath = parseResults.titles

    # pointsList is the list of DataPoints with the Netflix data
    movieInfo = {}
    if titlesPath is not None:
        movieInfo = parseMovies(titlesPath[0])
    pointsList = parseFiles(pathList, movieInfo)

    # Drop user into a shell, with the current environment
    code.interact(local=locals())
