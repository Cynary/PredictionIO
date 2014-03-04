"""
This file contains error calculating functions
"""

def percentError(predicted,actual):
    return abs(predicted/actual-1.)

def squareError(predicted,actual):
    return (predicted-actual)**2
