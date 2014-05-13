"""
This file contains error calculating functions
"""

import math

def percentError(predicted,actual):
    return abs(predicted/actual-1.)

def squareError(predicted,actual):
    return (predicted-actual)**2

# Check if they're in the same order of magnitude
def magError(predicted,actual):
    predOrder = math.log(predicted) if predicted > 0 else -1
    actualOrder = math.log(actual) if predicted > 0 else -1
    return abs(predOrder-actualOrder)

def underError(predicted,actual):
    return percentError(predicted,actual) if predicted<actual else 0

def overError(predicted,actual):
    return percentError(predicted,actual) if predicted>actual else 0
