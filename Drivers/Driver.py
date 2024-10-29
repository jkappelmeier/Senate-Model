import sys
sys.path.append('../')
import Senate.Geographies.National as National
import Senate.SenateModel as SenateModel
import Senate.LoadData as LoadData
import datetime
import Config as C
import csv



# Create National object
nat = National.National('National', 0, C.incSigma)

# Add State objects
nat.addChildren(LoadData.states)

# Assign to Model
sen = SenateModel.SenateModel('Senate Model', nat, LoadData.cor)


# Add polls
sen.addPolls(LoadData.polls)



# Run simulation
[incAvg, chalAvg, winRate, lossRate, tippingPoint, simStateVote] = sen.runSimulation(10000)

print('')
print('Senate Seats:')
print('    Democrats - Average: ' + str(round(incAvg, 2)) + ' Senate Seats | Chance of winning: ' + str(round(winRate * 100, 2)) + '%')
print('    Republicans - Average: ' + str(round(chalAvg, 2)) + ' Senate Seats | Chance of winning: ' + str(round(lossRate * 100, 2)) + '%')
print('    Chance of Senate Tie: ' + str(round((1 - winRate - lossRate) * 100, 2)) + '%')
print('')
for i in range(len(sen.stateGeographies)):
    print(str(sen.stateGeographies[i].name) + ' (' +str(round(tippingPoint[i]*100,2))+'% Tipping Point Chance):')
    if sen.allGeographies[i + 1].est > 0.5:
        print('    ' + str(sen.stateGeographies[i].demName) + ' - Estimate: ' + str(round(sen.allGeographies[i+1].est * 100, 2)) + '% | Chance of winning: ' + str(round(sen.allGeographies[i+1].probWin * 100, 2)) + '%')
        print('    ' + str(sen.stateGeographies[i].gopName) + ' - Estimate: ' + str(round((1 - sen.allGeographies[i+1].est) * 100, 2)) + '% | Chance of winning: ' + str(round((1 - sen.allGeographies[i+1].probWin) * 100, 2)) + '%')
    else:
        print('    ' + str(sen.stateGeographies[i].gopName) + ' - Estimate: ' + str(round((1 - sen.allGeographies[i+1].est) * 100, 2)) + '% | Chance of winning: ' + str(round((1 - sen.allGeographies[i+1].probWin) * 100, 2)) + '%')
        print('    ' + str(sen.stateGeographies[i].demName) + ' - Estimate: ' + str(round(sen.allGeographies[i+1].est * 100, 2)) + '% | Chance of winning: ' + str(round(sen.allGeographies[i+1].probWin * 100, 2)) + '%')
    print('')

with open('simulations.csv', 'w', newline = '') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',')
    for row in simStateVote:
        spamwriter.writerow(row)
