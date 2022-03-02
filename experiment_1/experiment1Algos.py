import libs.algorithms as algo
import goodTuring as gt
from classes.Encoding import Encoding
import geneticAlgorithm.utils as utils
import geneticAlgorithm.constants as constants
import csv

#Defining pieces necessary for fsc
TOTAL = 427929800129788411
p = 1 / TOTAL

def isTrap_uniform_low(encodedTrap, trap, fitnessFunc, sigVal=13.29):
    """given a trap and a significant value, determines whether the trap is coherent enough to be considered designed based on the unifrom distribution and low significant value"""
    global p
    connectionTuple = algo.connectionsPerPiece(trap)
    return algo.functional_specified_complexity(connectionTuple, p) >= sigVal

def isTrap_uniform_high(encodedTrap, trap, fitnessFunc, sigVal=18): # Need to fix this value according to alpha value!
    """given a trap and a significant value, determines whether the trap is coherent enough to be considered designed based on the unifrom distribution and low significant value"""
    global p
    connectionTuple = algo.connectionsPerPiece(trap)
    return algo.functional_specified_complexity(connectionTuple, p) >= sigVal

def isTrap_real_low(encodedTrap, trap, fitnessFunc, sigVal=13.29):
    """given a trap and a significant value, determines whether the trap is coherent enough to be considered designed based on the real distribution"""
    p = gt.getSmoothedProb(encodedTrap, fitnessFunc)
    connectionTuple = algo.connectionsPerPiece(trap)
    return algo.functional_specified_complexity(connectionTuple, p) >= sigVal

def isTrap_real_high(encodedTrap, trap, fitnessFunc, sigVal=18): # Need to fix this value according to alpha value!
    """given a trap and a significant value, determines whether the trap is coherent enough to be considered designed based on the real distribution"""
    p = gt.getSmoothedProb(encodedTrap, fitnessFunc)
    connectionTuple = algo.connectionsPerPiece(trap)
    return algo.functional_specified_complexity(connectionTuple, p) >= sigVal



   

def scExperiment(fitnessFunc, num_files):
    countTotal = 0

    for i in range(num_files):
        input_suff = "_new_enc_{}".format(i + 1)
        output_suff = "_new_enc_{}_scResults".format(i + 1)
        inputPath = constants.getExperimentPath(func=fitnessFunc, suff=input_suff)
        outputPath = constants.getExperimentPath(func=fitnessFunc, suff=output_suff)

        with open(inputPath, 'r' ,newline='') as incsv:
            with open(outputPath, 'w' ,newline='') as outcsv:
                writer = csv.writer(outcsv)

                for row in csv.reader(incsv):
                    if row[0] == "Trial":
                        writer.writerow(row + ["isTrap_uniform_low", "isTrap_uniform_high", "isTrap_real_low", "isTrap_real_high" ])
                    else:
                        countTotal += 1
                        if countTotal % 2 == 0:
                            continue
                        encodedTrap = utils.convertStringToEncoding(row[1])
                        decodedTrap = encoder.decode(encodedTrap)
                        trap = utils.createTrap(decodedTrap)
                        isTrap_uniform_low = isTrap_uniform_low(encodedTrap, trap, fitnessFunc)
                        isTrap_uniform_high = isTrap_uniform_high(encodedTrap, trap, fitnessFunc)
                        isTrap_real_low = isTrap_real_low(encodedTrap, trap, fitnessFunc)
                        isTrap_real_high = isTrap_real_high(encodedTrap, trap, fitnessFunc)
                        writer.writerow(row+[isTrap_uniform_low, isTrap_uniform_high, isTrap_real_low, isTrap_real_high ])
                outcsv.close()
    
    print("test total count:", countTotal)