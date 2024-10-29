import datetime
import numpy as np
import Config as C
from scipy.stats import norm
import Core.logitConversions as logitConversions

# This model contains the properties and methods for the overall model
class Model:

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
        self.name = name
        self.geographyHead = geography
        self.correlation = cor
        self.geographyHead.model = self
        self.allGeographies = self.getAllGeographies(self.geographyHead)
        self.stateGeographies = []

        self.currentDate = currentDate
        t0 = (C.electionDate - C.startDate).days
        tFinal = (C.electionDate - self.currentDate).days
        self.time = np.arange(t0, tFinal-1, -1)

        # State Vector Fundamentals
        self.xFund = []
        self.xCovarianceFund = []
        self.xTurnoutEst = []

        # Polling Vector
        self.zPolls = []
        self.rPolls = []
        self.availFlags = []

        # State Vector Polling Estimates
        self.xPolling = []
        self.xCovariancePolling = []

        # Polling Vector
        self.zPolls = []
        self.rPolls = []
        self.availFlags = []

        # Final Estimate
        self.stateEst = []
        self.covariance = []

        self.initializeModel()


    # Initialize the fundamentals of the model with information from the
    # geographies
    def initializeModel(self):

        ### Initialize Fundamentals:

        # Set up mapping between state vector and full geography vector
        [stateChildren, parentToStateIndices] = self.getChildren(self.geographyHead)
        self.stateGeographies = stateChildren
        self.parentToStateIndices = parentToStateIndices

        stateFundEst = []
        stateFundSigma = []
        for i in range(len(stateChildren)):
            stateFundEst.append(stateChildren[i].fundEst)
            stateFundSigma.append(stateChildren[i].fundSigma)

        # Adjust to estimate of national vote
        stateFundEst = np.array(stateFundEst)

        self.xFund = np.array(stateFundEst)
        rho = self.correlation
        stateFundSigma = np.array(stateFundSigma)
        self.xCovarianceFund = np.multiply(np.transpose(np.matrix(stateFundSigma)) * np.matrix(stateFundSigma), np.matrix(rho)) + self.geographyHead.fundSigma**2 * np.ones((len(self.xFund),len(self.xFund)))


        self.zPolls = np.zeros([len(self.time),len(self.stateGeographies)])
        self.rPolls = np.ones([len(self.time),len(self.stateGeographies)])*1000000
        self.availFlags = np.zeros([len(self.time),len(self.stateGeographies)],dtype=bool)

        self.xPolling = np.zeros([len(self.time),len(self.xFund)])
        self.xCovariancePolling = np.zeros([len(self.time),len(self.xFund),len(self.xFund)])

        self.stateEst = np.zeros(len(self.xFund))
        self.covariance = np.zeros([len(self.stateEst),len(self.stateEst)])


    # Add polls to the model
    #
    # Input:
    #   polls - List of polls to add to model
    def addPolls(self, polls):

        self.geographyHead.addPolls(polls)

        ### Initialize Polling measurements:
        for i in range(len(self.stateGeographies)):
            for j in range(len(self.time)):
                for k in range(len(self.stateGeographies[i].polls)):
                    if self.time[j] == (C.electionDate - self.stateGeographies[i].polls[k].date).days:
                        if self.availFlags[j, i] == 0:
                            self.availFlags[j, i] = 1
                            self.zPolls[j, i] = self.stateGeographies[i].polls[k].result
                            self.rPolls[j, i] = self.stateGeographies[i].polls[k].sigma**2
                        else:
                            self.zPolls[j, i] = (self.zPolls[j, i] * self.stateGeographies[i].polls[k].sigma**2 + self.stateGeographies[i].polls[k].result * self.rPolls[j, i]) / (self.rPolls[j, i] + self.stateGeographies[i].polls[k].sigma**2)
                            self.rPolls[j, i] = (1 - self.rPolls[j, i] / (self.rPolls[j, i] + self.stateGeographies[i].polls[k].sigma**2)) * self.rPolls[j, i]


    # Run the polling average for all geography areas concurently with covariance
    def runPollingAvg(self):


        N = len(self.xFund)

        # Set up process noise and bias
        rho = self.correlation
        p0 = 100000 * self.xCovarianceFund
        x0 = np.zeros(len(self.xFund))
        qVec = np.zeros(N)
        biasVec = np.zeros(N)
        for i in range(N):
            qVec[i] = np.sqrt(self.stateGeographies[i].pollingProcessNoise)
            biasVec[i] = self.stateGeographies[i].pollingBiasSigma
        qVec = np.matrix(qVec)
        biasVec = np.matrix(biasVec)
        Q = np.multiply(np.transpose(qVec)*qVec, rho) + np.ones((N,N)) * self.geographyHead.pollingProcessNoise
        bias = np.multiply(np.transpose(biasVec)*biasVec, rho) + np.ones((N,N)) * self.geographyHead.pollingBiasSigma**2
        # Set up measurement noise
        R = np.zeros([len(self.time), N, N])
        for i in range(len(self.time)):
            for j in range(N):
                R[i,j,j] = self.rPolls[i,j]

        # Set up sensitivity matrix
        H = np.identity(N)

        # Run Kalman Filter
        xK = np.transpose(np.matrix(x0))
        pK = p0
        for i in range(len(self.time)):
            if np.sum(self.availFlags[i, :]) > 0:
                zK = self.zPolls[i, :]
                zK = zK[self.availFlags[i, :]]
                zK = np.transpose(np.matrix(zK))
                hK = H[self.availFlags[i,:],:]
                hK = np.matrix(hK)

                rK = R[i, :, :]
                rK = rK[self.availFlags[i,:], :]
                rK = rK[:, self.availFlags[i, :]]
                rK = np.matrix(rK)

                fundEst = np.transpose(np.matrix(self.xFund))
                y = zK - hK * (xK + fundEst)
                S = hK * pK * np.transpose(hK) + rK
                K = pK * np.transpose(hK) * np.linalg.inv(S)

                xK = xK + K * y
                #pK = (np.identity(N) - K * hK) * pK
                pK = (np.identity(N) - K * hK) * pK * np.transpose(np.identity(N) - K * hK) + K * rK * np.transpose(K)

            pK = pK + Q

            self.xPolling[i, :] = np.array(np.transpose(xK))
            self.xCovariancePolling[i, :, :] = np.array(pK + bias + self.time[i]*Q)



    # Estimate the vote for all states of the model.
    #
    def estimateVote(self):

        # Run all polling averages
        self.runPollingAvg()

        N = len(self.xFund)
        m = len(self.allGeographies)

        # Combine Fundamentals and Polling for States
        xState = np.transpose(np.matrix(self.xFund-self.xFund))
        pState = self.xCovarianceFund
        zState = np.transpose(np.matrix(self.xPolling[-1,:]))
        rState = np.matrix(self.xCovariancePolling[-1,:,:])

        # Set up sensitivity matrix
        H = np.identity(N)

        fundEst = np.transpose(np.matrix(self.xFund))

        yState = zState
        S = pState + rState
        K = pState * np.linalg.inv(S)

        xEst = xState + K * yState
        pEst = (np.identity(len(xState)) - K) * pState * np.transpose(np.identity(len(xState)) - K) + K * np.matrix(rState) * np.transpose(K)


        self.stateEst = xEst
        self.covariance = pEst

        xEst = H * (self.stateEst + fundEst)
        pEst = H * pEst * np.transpose(H)

        self.finalEst = xEst
        self.finalCov = pEst

        # Assign estimates
        for i in range(len(self.stateGeographies)):
            self.stateGeographies[i].est = xEst[i, 0]
            self.stateGeographies[i].sigma = np.sqrt(pEst[i,i])
            winRate = norm.cdf((self.stateGeographies[i].est - 0.5) / self.stateGeographies[i].sigma)
            self.stateGeographies[i].probWin = winRate


    # Please implement this method to simulate the election nRuns times.
    #
    # Inputs:
    #   nRuns - number of times to run election
    def runSimulation(self, nRuns):
        self.estimateVote()
        return []


    # Get all children (and children of children recursively)
    #
    # Input:
    #   geography - Head of geography object to search
    # Output:
    #   children - List of children geographies
    #   parentToStateIndices - List of relations between parent geographies and indices of children in the final state vector
    def getAllGeographies(self, geography, children = []):
        geography.model = self
        children.append(geography)
        if len(geography.children) > 0:
            for i in range(len(geography.children)):
                children = self.getAllGeographies(geography.children[i], children)
        return children


    # Get all children (and children of children recursively) as well as relation between and parents to the list of children
    #
    # Input:
    #   geography - Head of geography object to search
    # Output:
    #   children - List of children geographies
    #   parentToStateIndices - List of relations between parent geographies and indices of children in the final state vector
    def getChildren(self, geography, children = [], parentToStateIndices = []):
        geography.model = self
        if len(geography.children) == 0:
            children.append(geography)
        else:
            initLen = len(children)
            for i in range(len(geography.children)):
                [children, parentToStateIndices] = self.getChildren(geography.children[i], children, parentToStateIndices)
            finalLen = len(children)
            parentToStateIndices.append([geography, np.arange(initLen, finalLen, 1)])
        return [children, parentToStateIndices]
