import Core.Geography as Geography
import Config as C

# This class represents the data for a state
class State(Geography.Geography):

    # Constructor for this class:
    #
    # Inputs:
    #   name - name for this object
    #   fundEst - fundamentals estimate of vote
    #   fundSigma - uncertainty in fundEst
    # Optional Inputs:
    #   pollingBiasSigma - final uncertainty in the bias for national polls
    #   pollingProcessNoise - variance gained every day from when a poll was
    #                         taken
    #   demName - name of Democratic candidate
    #   gopName - name of Republican candidate
    def __init__(self, name, fundEst, fundSigma, pollingBiasSigma = C.pollingBiasSigmaState, pollingProcessNoise = C.pollingProcessNoiseState, demName = '', gopName = ''):

        # Call superclass
        Geography.Geography.__init__(self, name)

        self.fundEst = fundEst
        self.fundSigma = fundSigma
        self.pollingBiasSigma = pollingBiasSigma
        self.pollingProcessNoise = pollingProcessNoise
        self.demName = demName
        self.gopName = gopName
