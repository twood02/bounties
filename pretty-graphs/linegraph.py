# All the imports for graphing and dataframes
from operator import index
from tkinter.font import names
from pyparsing import line
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd


def lineplot():
    plt.clf()
    sns.set_theme()
    # Read in the text file and seperate by any amt of space
    data = pd.read_csv('sample.txt', sep='\s+')
    # Drop all null columns
    data = data.dropna(axis=1)
    # Rename the columns to account for # in the text file 
    # This is done so that each header correlates to its data 
    data = data.rename({'#': 'x','x':'y1','y1':'y2'}, axis=1) 
    # Set the iterator/index equal to the x values
    data = data.set_index('x') 


    # Set the ticks for each lines to '+' and 'o'
    markers = {'y1':"P","y2":"o"}
    # Set the plot using the reformatted data and using the markers
    graph = sns.lineplot(
        data=data,
        markers= markers
        
    )
    # Label the axes 
    graph.set(xlabel='x axis label', ylabel='y axis label')
    # Set the graph bounds
    plt.xlim(0,1)
    plt.ylim(0,1)
    # Configure the legend
    plt.legend( loc='lower right', labels=['Example line', 'Another example'])
    # Bring up the actual graph
    plt.show()

lineplot()


