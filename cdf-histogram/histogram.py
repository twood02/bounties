import math
from operator import index
from tkinter.font import names
from pyparsing import line
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

def histogram():
    # Read in the data from the txt file seperated by any amt of space
    hist = pd.read_csv('timings.txt', sep='\s+')
    # Prompt the user for the smallest and largest data point they want to see, as well as the bin size
    print('Enter the min data point you would like to accept, enter D for default')
    min = input()
    if (min == "D"):
        min = hist.min()
    else:
        min = int(min)
    print('Enter the max data point you would like to accept, enter D for default')
    max = input()
    if (max == "D"):
        max = hist.max()
    else:
        max = int(max)
    print('Enter the bin size for the histogram, enter D for default')
    bin_size = input()
    # I had issues actaully calculating the default bin_size if the user chose to do that
    if (bin_size == "D"):
        count = hist.size
        print(count)
        bin_size = math.sqrt(count)
        
    else:
        bin_size = int(bin_size)
    # Make the plot with the dataframe and binsize
    histGraph = sns.histplot(data = hist,binwidth=bin_size)
    # Label the graph
    histGraph.set(xlabel='Timings')
    if (type(min) == int and type(max == int)):
        plt.xlim(min,max)
    # Display the graph
    plt.show()

histogram()