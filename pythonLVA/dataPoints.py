#!/usr/bin/python
"""
This file contains the specifications and implementation of data point classes for
the LVA project.
"""

# DataPoint is the parent class for all datapoints.
class DataPoint:
    pass

def NetflixDataPoint(dataString, movieID, currentMovie):
    movieYear,movieTitle = currentMovie
    
    customerID,rating,date = dataString.split(',')
    year,month,day = date.split('-')
    customerID = int(customerID)
    year = int(year)
    month = int(month)
    day = int(day)
    rating = int(rating)

    return (customerID,year,month,day,rating,movieYear)

# NetflixDataPoint refers to specific data points
# class NetflixDataPoint(DataPoint):
#     # Creates the DataPoint object.
#     # Arguments
#     #   dataString: "CustomerID,Rating,YYYY-MM-DD".
#     #   movieID: ID of the movie.
#     #   currentMovie: information data structure, returned by parseMovies
#     # Requirements
#     #   dataString needs to be correctly formatted, and movieID is an integer.
#     # Effects
#     #   Parses the dataString, and creates the object.
#     def __init__(self, dataString, movieID, currentMovie):
#         customerID,rating,date = dataString.split(',')
#         year,month,day = date.split('-')
#         self.customerID = int(customerID)
#         # self.rating = int(rating)
#         self.year = int(year)
#         self.month = int(month)
#         self.day = int(day)
#         # self.movieID = movieID
#         # self.movieInfo = currentMovie

#     def __repr__(self):
#         return str((self.customerID,self.rating,
#                     (self.year,self.month,self.day),
#                     self.movieID,
#                     self.movieInfo))

#     __str__ = __repr__

# Called from the command line
if __name__ == "__main__":
    # Drop user into a shell, with the data point classes
    code.interact(local=locals())
