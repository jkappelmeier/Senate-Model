import datetime
import numpy as np
# This provides all constants/config values used by model
# Note that data comes from elections from 1996 - 2020


### Race Specific Strings

incParty = 'D' # Incumbent Party

currentDate = datetime.date.today() # Current Date
electionDate = datetime.date(2024,11,5) # Election Date
startDate =  datetime.date(2024,1,1) # Campaign Start Date


### National-Level Fundamental Consants

incAvg = 0.486 # Average incumbent 2-party vote share
incSigma = 0.031 # Standard deviation in incumbent 2-party vote share


### National-Level Polling Constants

pollingSigmaSF = 0.07108 # Average polling error at N = 1000
pollingProcessNoiseNat = 1.22e-5 # Polling process noise per day for national polls
pollingBiasSigmaNat = np.sqrt(9.73e-4) # National Polling Bias Noise


### State-Level Polling Constants

pollingProcessNoiseState = 1.04e-5
pollingBiasSigmaState = np.sqrt(8.25e-4)
