#!/usr/bin/env python3
###################################################################
#
#   CSSE1001/7030 - Assignment 1
#
#   Student Username: s4392687
#
#   Student Name: Maxwell Bo
#
###################################################################

#####################################
# Support given below - DO NOT CHANGE
#####################################

from assign1_support import *

#####################################
# End of support 
#####################################

# Add your code here

import math
from itertools import count


def interact():
    ''' 
    Provides an interface for the user to input commands.
    The interface will request a data source file.
    If the source file is valid, the user can use commands to display formatted
    statistical information from the data set.
    
    interact() --> None

    Preconditions: 
    input must either "summary" or "sets *args"
    "sets" arguments must be space seperated integers 
    input must not be 'q', or else the interface loop will terminate
    '''

    print("Welcome to the Statistic Summariser\n")
    fileTargetStr = input("Please enter the data source file: \n")
    data = load_data(fileTargetStr)

    while True:
        rawInput = input("Command: ")
        commandList = rawInput.lower().split()
        arguments = commandList[1:]

        if commandList[0] == "summary":
            display_set_summaries(data_summary(data))

        elif commandList[0] == "sets":
            try:
                display_set_summaries(data_summary([data[int(x)] for x in
                                                    arguments]))
            except Exception:
                print("Unknown command: " + rawInput + '\n')

        elif commandList[0] == "q":
            break

        else:
            print("Unknown command: " + rawInput + '\n')


def load_data(filename):
    '''
    Loads data from a target file, and returns a list of 
    (str, [float, ..., float]) tuples, with a tuple corresponding
    to each line of the target file.

    load_data(str) --> list --> [(str, [float, ..., float]), (...), (str, [float, ..., float])]

    Preconditions:
    filename must be a file within the working directory of the script
    filename must include the file extension
    filename must point to a file where its contents are in a
    "str, float, ..., float \n" format
    '''
    
    with open(filename, 'r') as file:
        datastream = [line.split(', ') for line in file]
        return [(splitlines[0], [float(i) for i in splitlines[1:]])
            for splitlines in datastream]
    


def get_ranges(data):
    ''' 
    Returns a tuple containing the minimum and maximum values of a list 

    get_ranges(list) --> tuple --> (value, value)

    Preconditions: 
    data must be a sortable list of only numeric type objects
    '''

    data.sort()
    return (data[0], data[-1])


def get_mean(data):
    ''' 
    Returns the mean of all values in a list

    get_mean(list) --> float

    Preconditions: 
    data must be a list of only numeric type objects
    '''
    return sum(data) / len(data)


def get_median(data):
    ''' 
    Returns the median of all values in a list

    get_median(list) --> float

    Preconditions:
    data must be a sortable list of only numeric type objects
    '''

    data.sort()
    length = len(data)
    if length % 2 == 0:
        #When even
        return (data[(length // 2) - 1] + data[length // 2]) / 2.0
    else:
        #When odd
        return data[(length - 1) // 2]


def get_std_dev(data):
    ''' 
    Returns the standard deviation of all values in a list

    get_std_dev(list) --> float

    Preconditions:
    data must be a list of only numeric type objects
    '''

    sumtotal = 0
    for i in data:
        sumtotal += (i - get_mean(data)) ** 2
    return math.sqrt((1 / len(data)) * sumtotal)


def data_summary(data):
    '''
    Returns the statistical information of a dataset

    data_summary(list) --> list --> [(str, int, float, float, float, float, float), ..., (str, int, float, float, float, float, float)]

    Preconditions: 
    data must be a list of structure [(str, [float, ..., float]), ..., (str, [float, ..., float])]
    '''
    return [(
        subset[0], len(subset[1]), get_mean(subset[1]), get_median(subset[1]),
        get_ranges(subset[1])[0], get_ranges(subset[1])[1],
        get_std_dev(subset[1])) for subset in data]


def display_set_summaries(data):
    '''
    Prints a nicely formatted statistical information of a dataset, which may consist of >= 0 data subsets.

    display_set_summaries(list) --> None

    Preconditions:
    data must be a list of format [(str, int, float, float, float, float, float), *,]
    '''

    labels = [" ", "Count:", "Mean:", "Median:", "Minimum:", "Maximum:",
              "Std Dev:"]
    print("\nSet Summaries\n")
    for i in zip(labels, *data):
        for j in i:
            if type(j) is float:
                display_with_padding("{0:.2f}".format(j))
            else:
                display_with_padding(j)
        print('')
    print('')

    ##################################################
    # !!!!!! Do not change (or add to) the code below !!!!!
    # 
    # This code will run the interact function if
    # you use Run -> Run Module  (F5)
    # Because of this we have supplied a "stub" definition
    # for interact above so that you won't get an undefined
    # error when you are writing and testing your other functions.
    # When you are ready please change the definition of interact above.
    ###################################################


if __name__ == '__main__':
    interact()
