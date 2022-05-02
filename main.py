# MR1007 - Control Computarizado
# ITESM Campus Monterrey
# Dr. Antonio Favela

# A01411195 - Soraya Lizeth Maqueda Gutiérrez
# A00
# A00

import PySimpleGUI as sg # Graphic Interface Library
import numpy as np # Math Library
import pandas as pd # Data Analysis Library
import matplotlib # Grapher Library

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from math import e, trunc

matplotlib.use('TkAgg')

# Global Contro Variables
defaultSize = (20, 1)

numA = 1 # Number of a's coefficients
numB = 1 # Number of b's coefficients
numY = 0 # Number of outputs
numU = 0 # Number of inputs

# Function to draw Graph 
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)

    return figure_canvas_agg

################### ARX Model ###################

# Case Determiner
def case(d, T):
    tPrime = d*T
    
    if tPrime % T == 0:
        # Case 1: tPrime is multiple of T
        return True
    else:
        # Case 2: there's a delay theta
        return False

def an(T, tao):
    return e**(-T /tao)

def bn(T, tao, k):
    return k*(1-(e**(-T/tao)))

# Delay
def d(tPrime, T):
    return trunc(tPrime/T)

# Theta
def t(tPrime, T, d):
    return tPrime-(d*T)

# Theta Prime
def tPrime(t, T, d):
    return t+(d*T)

# Transfer Function
def HGp(cn, mn):
    return cn/mn

def mn(k, t, T, z, d):
    return k*(1-(e**(-T/t)))*(z**(-1-d))

# Difference Equations

# c[n] = a1*c[n-1] + b1*m[n-1-d]
def cn(kMax, T, d, tao):
    cn = []
    a1 = an(T, tao)
    b1 = bn(T, tao, n)

    for n in kMax:
        if cn[n-1]==None:  cn[n-1].append(0) # If a value doesn't exists, we assume that it's 0
        cn.append(a1*cn[n-1] + b1*cn[n-1-d])
    
    return cn

# Equations' Table
headers = { 'k': [], 'y(k)': [], 'u(k)': [] }

table = pd.DataFrame(headers)

# Define the Layout
layout = [
    # Canvas
    [sg.Text('ARX Graphic')],
    [sg.Canvas(key='-CANVAS-')],
    [sg.Button('Close')],
    #Coeffiecients
    [sg.Text('Coefficients')],
    [sg.Text('a')],
    [sg.Input(do_not_clear=True, key='_INA_')],
    [sg.Button('Add a'), sg.Button('Delete a')],
    *[[sg.Text('a' + str(i)), sg.InputText(),] for i in range(numA)],
    [sg.Text('b')],
    [sg.Input(do_not_clear=True, key='_INB_')],
    [sg.Button('+'), sg.Button('-')],
    *[[sg.Text('b' + str(i)), sg.InputText(),] for i in range(numB)],
    # Input Values
    [sg.Text('Enter Values')],
    [sg.Text('Constant (k)', size=defaultSize), sg.InputText(key='-k-')],
    [sg.Text('Delay (d)', size=defaultSize), sg.InputText(key='-d-')],
    [sg.Text("\u03F4'", size=defaultSize), sg.InputText(key='-tPrime-')],
    [sg.Text('Time Interval (T)', size=defaultSize), sg.InputText(key='-T-')],
    [sg.Text('Time Constant (\u03F4)', size=defaultSize), sg.InputText(key='-t-')],
    [sg.Button('Submit')]
]

# Create the window
window = sg.Window(
    'ARX Graphic', # Window Title
    layout, # Window Layout
    location=(600, 600),
    finalize=True,
    element_justification='center',
    font='Helvetica 18'
)

# Graph
fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
t = np.arange(0, 3, .01)
fig.add_subplot(111).plot(t, 2 * np.sin(1 + np.pi * t))

# Add plot to the window
draw_figure(window['-CANVAS-'].TKCanvas, fig)

# Create an event loop
while True:
    event, values = window.read()
    # End program if user closes window or
    # presses the Close button
    if event == 'Close' or event == sg.WIN_CLOSED:
        break

    if event == 'Submit':
        values=['-k-', '-T-', '-tPrime-', '-d-', '-t-']
        an(values['-T-'], values['-t-'])

    if event == 'Add a' or event == 'Delete a':
        numA += -1 if event == 'Delete a' else 1

        windowTemp = sg.Window('ARX Model', location=(600, 600),
        finalize=True, element_justification='center', font='Helvetica 18').Layout(layout)
        window.Close()
        window = windowTemp

window.close()

# References
# https://apmonitor.com/wiki/index.php/Apps/ARXTimeSeries
# https://apmonitor.com/do/index.php/Main/ModelIdentification
# https://www.youtube.com/watch?v=8HdUoWXLNOs