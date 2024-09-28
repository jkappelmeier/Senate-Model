import numpy as np
import csv
import sys
import Config as C
sys.path.insert(1, '../Model')
import Core.Poll as Poll
import Senate.Geographies.State as State

# Load in State Data
states = []
with open('../Data/StateFundamentals.csv') as csvfile:
    data = csv.reader(csvfile, delimiter = ',')
    rowCount = 0
    for row in data:
        if rowCount > 0:
            est = float(row[1])

            state = State.State(str(row[0]), est, float(row[2]), demName = str(row[3]), gopName = str(row[4]))
            states.append(state)

        rowCount = rowCount + 1

# Load in polls
polls = []
with open('../Data/Polls.csv') as csvfile:
    data = csv.reader(csvfile, delimiter = ',')
    rowCount = 0
    for row in data:
        if rowCount > 0:
            geography = str(row[0])
            date = str(row[1])
            result = [float(row[2][:-1]), float(row[3][:-1])]
            pollster = str(row[4])
            sampleSize = int(row[5])
            poll = Poll.Poll(geography, date, result, pollster, sampleSize)
            polls.append(poll)
        rowCount = rowCount + 1


# Load in correlation matrix
cor = np.zeros([34, 34])
with open('../Data/StateCorrelation.csv') as csvfile:
    data = csv.reader(csvfile, delimiter = ',')
    rowCount = 0
    for row in data:
        if rowCount > 0:
            cor[rowCount - 1, :] = row[1:]
        rowCount = rowCount + 1
