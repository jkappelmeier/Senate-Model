import Core.Model as Model
import Config as C
import numpy as np

# Implements the Model superclass for the senate election
class SenateModel(Model.Model):

    # Constructor for this class
    #
    # Inputs:
    #   name - name of this object
    #   geography - Head of geography class tree
    #   cor - correlation matrix to be used (must match lengths of all children of geography)
    #   currentDate - current date to run Model
    # Output:
    #   Instance of this class
    def __init__(self, name, geography, cor, currentDate = C.currentDate):

        # Call superclass
        Model.Model.__init__(self, name, geography, cor, currentDate)


    # Simulate the eleciton nSamples times
    #
    # Input:
    #   nRuns - Number of times to simulate election
    # Output:
    #   incAvg - Average electoral vote of incumbent
    #   chalAvg - Average electoral vote of challenger
    #   winRate - Percent of times incumbent wins
    #   lossRate - Percent of times incumbent loses
    #   simStateVoteList - List of all the state results generated
    def runSimulation(self, nRuns):
        self.estimateVote()

        # Collect data
        stateEst = np.array(np.transpose(self.finalEst))[0]

        nWins = 0
        nLoses = 0
        nStatesInc = []
        nStatesChal = []
        simStateVoteList = []
        tippingPoint = np.zeros(len(stateEst))
        for i in range(nRuns):
            simVote = np.random.multivariate_normal(stateEst, self.finalCov)
            statesWon = [1 if a_ > 0.5 else 0 for a_ in simVote]
            statesWon = sum(statesWon) + 28
            statesLost = 100 - statesWon
            nStatesInc.append(statesWon)
            nStatesChal.append(statesLost)

            if statesWon > statesLost:
                nWins = nWins + 1
            elif statesLost > statesWon:
                nLoses = nLoses + 1
            simStateVoteList.append(simVote)

            # Find Tipping Point State
            sortedIndices = np.argsort(simVote)
            states = 38
            count = 0
            while states < 51:
                states = states + 1
                count = count + 1
            tippingPoint[sortedIndices[count-1]] = tippingPoint[sortedIndices[count-1]] + 1

            if i % 100 == 0:
                print(str(i) + ' / ' + str(nRuns) + ' Runs completed')

        winRate = nWins /  nRuns
        lossRate = nLoses / nRuns
        incAvg = sum(nStatesInc) / nRuns
        chalAvg = sum(nStatesChal) / nRuns
        tippingPoint = tippingPoint / np.sum(tippingPoint)

        return [incAvg, chalAvg, winRate, lossRate, tippingPoint, simStateVoteList]
