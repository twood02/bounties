import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as tick
from matplotlib.ticker import FuncFormatter
import csv
import random




def main():
   
    data_bar = read_file("sample-bar.txt", ' ')
    data = read_file("sample.txt", ' ')
    l = ["example line", "another example"]
    plot_bar_graph(data_bar, "Number of Registrations Per month", "", "Registrations" )
    plot_line_graph(data, "", "X-axis Label", "Y-axis Label", l)


def read_file(file_name, delim):
    rows =[]
    with open(file_name, 'r') as line:  
        #read the data separated by the delimiter and ignore whitespace follwing the delimiter                                                                                       
        line_reader = csv.reader(line, delimiter=delim, skipinitialspace=True)    
        for line in line_reader:
          rows.append(line)

    # cleaning the data: remove entries that are trailing white space
    for row in rows:
        for cell in row:
            if cell == '':
                row.remove(cell)
            
    return rows

def thousands(x, pos):
    return '%1dK' % (x * 1e-3)

def plot_bar_graph(data, title, x_title, y_title):
    fig = plt.figure(figsize = (10, 5))
    x = []
    y = []
    for row in data:
        x.append(row[0]) # get the labels of the bars
        y.append(int(row[1]))# get the values of the bars


    # creating the bar plot
    ax = plt.subplot(111)
    ax.yaxis.set_major_formatter(thousands)
    #plt.yscale("linear")
    plt.bar(x, y, color ='maroon', width = 0.4)
    plt.xlabel(x_title)
    plt.ylabel(y_title)
    plt.title(title)
    img_title= title.replace(' ', '-') #replace title spaces with dashes 
    plt.savefig(img_title)
    plt.show()
  

def plot_line_graph(data, title, x_title, y_title, line_labels):
    
    markers = ['o', '|', '.', 'x', 's'] # some markers that can be used for lines 

    x = []
    y = [] 
    
    for i in range(1, len(data)):
        x.append(float(data[i][0])) #get the x axis data once since all lines have same x
        
    for i in range(1, len(data[0])-1 ):
        for j in range(1, len(data)): # get the data of line j (column j) at row i 
            y.append(float(data[j][i]))
        plt.plot(x, y, label =line_labels[i-1], marker=markers[i%len(markers)])  #plot the line 
        y = []

    # creating the bar plot
  
    # scaling
    plt.legend(loc="upper right")
    plt.yscale("linear") 
    # Set axes limit
    plt.xlim(0, 1)
    plt.ylim(0, 1)

    #set titles   
    plt.xlabel(x_title)
    plt.ylabel(y_title)
    plt.title(title)
    img_title= title.replace(' ', '-') #replace title spaces with dashes 
    if img_title == '':
        img_title = "line-graph-figure"
    plt.savefig(img_title)
    plt.show()

if __name__ == "__main__":
    main()
