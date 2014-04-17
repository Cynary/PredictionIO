#!/usr/bin/python
"""
"Dumb" solution to LVA:
Look at the rate of rating (rates/time), and predict number of ratings in the future
by taking the expected value: rate*time.
"""

import parserNF
import code
import os
import time
import datetime

class SimpleLearner():
    def __init__(self):
        self.name = "SimpleLearner"

    def learn(self, data):
        pass

    def predict(self, user, period):
        # Some background here: data comes in timestamps, but these span days.
        # So we will add a whole day to the data to account for that.
        oneDay = 24*60*60 # 24h*60m*60s
        data = sorted(user[1])
        learnPeriod = data[-1][0]-data[0][0] + oneDay
        nactions = len(data)
        rate = nactions/learnPeriod # #actions/s
        return period*rate # #actions
