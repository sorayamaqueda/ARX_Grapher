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
defaultSize = (10, 1)

numA = 0 # Number of a's coefficients
numB = 0 # Number of b's coefficients
numY = 0 # Number of outputs
numU = 0 # Number of inputs

# Input Values
k = 0 # Gain Constant
T = 0 # Time Interval
tau = 0 # Time Constant
t = 0 # Theta
tPrime = 0 # Theta Prime
inDist = 0 # Input Disturbance
outDist = 0 # Output Disturbance
mk = 0 # Input Signal

# Coefficients (Maximum 4 per coefficient)
# If not given, value must be 0
a1 = 0
a2 = 0
a3 = 0
a4 = 0

b1 = 0
b2 = 0
b3 = 0
b4 = 0

# Function to draw Graph 
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)

    return figure_canvas_agg

################### Plant Control Discrete Model ###################

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
        # If a value doesn't exists, 
        # we assume that it's 0
        if cn[n-1]==None:  cn[n-1].append(0)
        cn.append(a1*cn[n-1] + b1*cn[n-1-d])
    
    return cn

# Equations' Table
headers = { 'k': [], 'y(k)': [], 'u(k)': [] }

table = pd.DataFrame(headers)

# Define the Layout
layout = [
    # Canvas
    [sg.Text('Discrete Control Model Grapher')],
    [sg.Canvas(key='-CANVAS-')],
    #Coeffiecients
    [sg.Text('Coefficients')],
    [sg.Text('a')],
    *[[sg.Text('a' + str(i)), sg.InputText(),] for i in range(numA)],
    [sg.Button('Add a'), sg.Button('Delete a')],
    [sg.Text('b')],
    *[[sg.Text('b' + str(i)), sg.InputText(),] for i in range(numB)],
    [sg.Button('Add b'), sg.Button('Delete b')],
    # Input Values
    [sg.Text('Enter Values')],
    [sg.Text('Constant (k)', size=defaultSize), sg.InputText(key='-k-', size=defaultSize), sg.Text('Delay (d)', size=defaultSize), sg.InputText(key='-d-', size=defaultSize)],
    [sg.Text("\u03F4'", size=defaultSize), sg.InputText(key='-tPrime-', size=defaultSize), sg.Text('Time Interval (T)', size=defaultSize), sg.InputText(key='-T-', size=defaultSize)],
    [sg.Text('Time Constant (\u03F4)', size=defaultSize), sg.InputText(key='-tau-', size=defaultSize), sg.Text('m[k]'), sg.InputText(key='-mk-', size=defaultSize)],
    [sg.Text('Input Disturbance', size=defaultSize), sg.InputText(key='-inputD-', size=defaultSize), sg.Text('Output Disturbance', size=defaultSize), sg.InputText(key='-outputD-', size=defaultSize)],
    # Window Buttons
    [sg.Button('Submit'), sg.Button('Close')]
]

# Create the window
window = sg.Window(
    'Discrete Control Model', # Window Title
    location=(0, 0),
    finalize=True,
    element_justification='center',
    font='Helvetica 18',
    size=(800, 800)
).Layout(layout).Finalize() # Window Layout

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
        # Store submitted values in global variables
        k = values['-k-']
        T = values['-T-']
        tPrime = values['-tPrime-']
        inDist = values['-inputD-']
        outDist = values['-outputD-']
        tau = values['-tau-']
        mk = values['-mk-']

        if numA > 0: print('Get other indexes and if empty fill in with 0')
        if numB > 0: print('Get other indexe values and if empty fill in with 0')


    # If a new coefficient a is added
    if event == 'Add a' or event == 'Delete a':
        if event == 'Delete a': numA += -1  
        else: numA += 1

        # Avoid reusing layout
        layout = [
            # Canvas
            [sg.Text('Discrete Control Model Grapher')],
            [sg.Canvas(key='-CANVAS-')],
            #Coeffiecients
            [sg.Text('Coefficients')],
            [sg.Text('a')],
            *[[sg.Text('a' + str(i)), sg.InputText(),] for i in range(numA)],
            [sg.Button('Add a'), sg.Button('Delete a')],
            [sg.Text('b')],
            *[[sg.Text('b' + str(i)), sg.InputText(),] for i in range(numB)],
            [sg.Button('Add b'), sg.Button('Delete b')],
            # Input Values
            [sg.Text('Enter Values')],
            [sg.Text('Constant (k)', size=defaultSize), sg.InputText(key='-k-', size=defaultSize), sg.Text('Delay (d)', size=defaultSize), sg.InputText(key='-d-', size=defaultSize)],
            [sg.Text("\u03F4'", size=defaultSize), sg.InputText(key='-tPrime-', size=defaultSize), sg.Text('Time Interval (T)', size=defaultSize), sg.InputText(key='-T-', size=defaultSize)],
            [sg.Text('Time Constant (\u03F4)', size=defaultSize), sg.InputText(key='-t-', size=defaultSize), sg.Text('m[k]'), sg.InputText(key='-mk-', size=defaultSize)],
            [sg.Text('Input Disturbance', size=defaultSize), sg.InputText(key='-inputD-', size=defaultSize), sg.Text('Output Disturbance', size=defaultSize), sg.InputText(key='-outputD-', size=defaultSize)],
            # Window Buttons
            [sg.Button('Submit'), sg.Button('Close')]
        ]

        fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
        t = np.arange(0, 3, .01)
        fig.add_subplot(111).plot(t, 2 * np.sin(1 + np.pi * t))

        draw_figure(window['-CANVAS-'].TKCanvas, fig)

        windowTemp = sg.Window('Discrete Model Grapher', location=(0, 0),
        finalize=True, element_justification='center', font='Helvetica 18').Layout(layout).Finalize()
        window.Close()
        window = windowTemp

    # If another coefficient b is added
    if event == 'Add b' or event == 'Delete b':
        if event == 'Delete b': numB += -1  
        else: numB += 1

        # Avoid reusing layout
        layout = [
            # Canvas
            [sg.Text('Discrete Control Model Grapher')],
            [sg.Canvas(key='-CANVAS-')],
            #Coeffiecients
            [sg.Text('Coefficients')],
            [sg.Text('a')],
            *[[sg.Text('a' + str(i)), sg.InputText(),] for i in range(numA)],
            [sg.Button('Add a'), sg.Button('Delete a')],
            [sg.Text('b')],
            *[[sg.Text('b' + str(i)), sg.InputText(),] for i in range(numB)],
            [sg.Button('Add b'), sg.Button('Delete b')],
            # Input Values
            [sg.Text('Enter Values')],
            [sg.Text('Constant (k)', size=defaultSize), sg.InputText(key='-k-', size=defaultSize), sg.Text('Delay (d)', size=defaultSize), sg.InputText(key='-d-', size=defaultSize)],
            [sg.Text("\u03F4'", size=defaultSize), sg.InputText(key='-tPrime-', size=defaultSize), sg.Text('Time Interval (T)', size=defaultSize), sg.InputText(key='-T-', size=defaultSize)],
            [sg.Text('Time Constant (\u03F4)', size=defaultSize), sg.InputText(key='-t-', size=defaultSize), sg.Text('m[k]'), sg.InputText(key='-mk-', size=defaultSize)],
            [sg.Text('Input Disturbance', size=defaultSize), sg.InputText(key='-inputD-', size=defaultSize), sg.Text('Output Disturbance', size=defaultSize), sg.InputText(key='-outputD-', size=defaultSize)],
            # Window Buttons
            [sg.Button('Submit'), sg.Button('Close')]
        ]

        fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
        t = np.arange(0, 3, .01)
        fig.add_subplot(111).plot(t, 2 * np.sin(1 + np.pi * t))

        draw_figure(window['-CANVAS-'].TKCanvas, fig)

        windowTemp = sg.Window('Discrete Model Grapher', location=(0, 0),
        finalize=True, element_justification='center', font='Helvetica 18').Layout(layout).Finalize()
        window.Close()
        window = windowTemp

window.close()

# References
# https://apmonitor.com/wiki/index.php/Apps/ARXTimeSeries
# https://apmonitor.com/do/index.php/Main/ModelIdentification
# https://www.youtube.com/watch?v=8HdUoWXLNOs