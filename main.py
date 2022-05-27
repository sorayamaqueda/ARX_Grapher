# MR1007 - Control Computarizado
# ITESM Campus Monterrey
# Dr. Antonio Favela

# A01411195 - Soraya Lizeth Maqueda Gutiérrez
# A00
# A00

# Functionality:
# We need to define a function in Z. Then we need to obtain the Discrete Equivalent of that function (HGp(z))
# From this transformation, we obtain coefficients a1, a2, b1.
# Based on an Excel document, we need to preview how the graph will be.
# The first delivery needs to receive inputs from User, and then be able to graph a first order ARX Model.

from pickle import NONE
from turtle import title

import control.matlab as control
import scipy.signal as signal
import matplotlib.pyplot as plt
import PySimpleGUI as sg  # Graphic Interface Library
import seaborn as sns  # Library for decorations
import pandas as pd  # Data Analysis Library
import numpy as np  # Math Library
import matplotlib  # Grapher Library

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from math import e, trunc

matplotlib.use('TkAgg')

# Global Contro Variables
defaultSize = (15, 1)
showPlot = False

maxCoefficientIndex = 4
numA = 1  # Number of a's coefficients
numB = 0  # Number of b's coefficients
numY = 0  # Number of outputs
numU = 0  # Number of inputs

# Input Values
k = 0  # Gain Constant
T = 0  # Time Interval
tau = 0  # Time Constant
t = 0  # Theta
tPrime = 0  # Theta Prime
inDist = 0  # Input Disturbance
outDist = 0  # Output Disturbance
mk = 0  # Input Signal

# Coefficients (Maximum 4 per coefficient)
# If not given, value must be 0
a = []
b = []

a1 = 0
a2 = 0
a3 = 0
a4 = 0

b1 = 0
b2 = 0
b3 = 0
b4 = 0

# Result lists
cn = []
mn = []
tempM = 0

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
    return e**(-T / tao)


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


# def mn(k, t, T, z, d):
#     return k*(1-(e**(-T/t)))*(z**(-1-d))

# Difference Equations

# c[n] = a1*c[n-1] + b1*m[n-1-d]
def PulseTransferFunction(kMax):
    a1 = values['-a-1']
    b1 = bn(T, tao, n)

    for n in kMax:
        # If a value doesn't exists, we assume that it's 0
        if cn[n-1] == None:
            cn[n-1].append(0)
        cn.append(a1*cn[n-1] + b1*cn[n-1-d])

    return cn


# Equations' Table
headers = {'k': [], 'y(k)': [], 'u(k)': []}

table = pd.DataFrame(headers)
headings = list(headers)
values = table.values.tolist()

# Theme and Styling
sg.theme('DarkBlue')
sg.set_options(font=('Courier New', 12))

# Coefficients
coefficientsFrame = [
    [sg.Frame(layout=[
            [sg.Text('a')],
            *[[sg.Text('a' + str(i)), sg.InputText(key='-a-' + str(i)), ] for i in (n+1 for n in range(4))],
            [sg.Text('b')],
            *[[sg.Text('b' + str(i)), sg.InputText(key='-b-' + str(i)), ] for i in range(4)],
        ], title='Coefficients')]
]

# Table
tableFrame = [
    [sg.Frame(layout=[
        [sg.Table(
            values=values,
            headings=headings,
            auto_size_columns=False,
            col_widths=list(map(lambda x:len(x)+1, headings)))
        ]
    ], title='Table of Values')]
]

# Values
valuesFrame = [
    [sg.Frame(layout=[
        [sg.Text('Constant (k)', size=defaultSize),
                 sg.InputText(key='-k-', size=defaultSize)],
        [sg.Text('Delay (d)', size=defaultSize),
                 sg.InputText(key='-d-', size=defaultSize)],
        [sg.Text("\u03F4'", size=defaultSize), sg.InputText(
            key='-tPrime-', size=defaultSize)],
        [sg.Text('Time Interval (T)', size=defaultSize),
                 sg.InputText(key='-T-', size=defaultSize)]
    ], title='')]
]

functionValues = [
    [sg.Frame(layout=[
        [sg.Text('Time Constant (\u03F4)', size=defaultSize),
                 sg.InputText(key='-tau-', size=defaultSize)],
        [sg.Text('m[k]'), sg.InputText(key='-mk-', size=defaultSize)],
        [sg.Text('Input Disturbance', size=defaultSize),
                 sg.InputText(key='-inputD-', size=defaultSize)],
        [sg.Text('Output Disturbance', size=defaultSize),
                 sg.InputText(key='-outputD-', size=defaultSize)]
    ], title='')]
]

# Define the Layout
layout = [
    # Canvas
    [sg.Text('Discrete Control Model Grapher')],
    [sg.Canvas(key='-CANVAS-')],
    [sg.Frame('Inputs', tableFrame, pad=(0, 5)), sg.Frame(
        '', coefficientsFrame, pad=(0, (14, 5)), key='Hide')],
    # Input Values
    [sg.Frame('Values', valuesFrame, pad=(0, 5)), sg.Frame(
        '', functionValues, pad=(0, (14, 5)), key='Hide')],
    # Window Buttons
    [sg.Button('Submit'), sg.Button('Show Plot'), sg.Button('Close')]
]

# Create the window
window = sg.Window(
    'Discrete Control Model',  # Window Title
    location=(0, 0),
    finalize=True,
    element_justification='center',
    font='Helvetica 18',
    size=(800, 800)
).Layout(layout).Finalize()  # Window Layout

# # Graph
fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)

# Define Transfer Function
num = np.array([2])
den = np.array([3, 1])

H = signal.TransferFunction(num, den)
t, y = signal.step(H)

plt.plot(t, y)
plt.title('Step Response')
plt.xlabel('t')
plt.ylabel('y')
plt.grid()

# fig.add_subplot(111).plot(plt.show())

# Add plot to the window
# draw_figure(window['-CANVAS-'].TKCanvas, fig)

# Create an event loop
while True:
    event, values = window.read()
    # End program if user closes window or presses the Close button
    if event == 'Close' or event == sg.WIN_CLOSED:
        break

    # Enable plot visibility
    if event == 'Show Plot':
        showPlot = True
        print('Generating graph...')
        num = np.array([12])
        den = np.array([3, 1])

        H = signal.TransferFunction(num, den)

        t, m = signal.step(H)
        plt.plot(t, m)
        plt.xlabel('t')
        plt.ylabel('m[k]')
        plt.grid()
        fig.add_subplot(111).plot(plt.show())

    # Store input values
    if event == 'Submit':
        
        # Coefficients
        coefficientsFrame = [
            [sg.Frame(layout=[
                    [sg.Text('a')],
                    *[[sg.Text('a' + str(i)), sg.InputText(key='-a-' + str(i)), ]for i in range(numA)],
                    [sg.Button('Add a'), sg.Button('Delete a')],
                    [sg.Text('b')],
                    *[[sg.Text('b' + str(i)), sg.InputText(key='-b-' + str(i)), ] for i in range(numB)],
                    [sg.Button('Add b'), sg.Button('Delete b')],
                ], title='Coefficients')
            ]
        ]

        # Table
        tableFrame = [
            [sg.Frame(layout=[
                [sg.Table(
                    values=values,
                    headings=headings,
                    auto_size_columns=False,
                    col_widths=list(map(lambda x:len(x)+1, headings)))
                ]
            ], title='Table of Values')]
        ]

        # Values
        valuesFrame = [
            [sg.Frame(layout=[
                [sg.Text('Constant (k)', size=defaultSize), sg.InputText(key='-k-', size=defaultSize)],
                [sg.Text('Delay (d)', size=defaultSize), sg.InputText(key='-d-', size=defaultSize)],
                [sg.Text("\u03F4'", size=defaultSize), sg.InputText(key='-tPrime-', size=defaultSize)],
                [sg.Text('Time Interval (T)', size=defaultSize), sg.InputText(key='-T-', size=defaultSize)]
            ], title='')]
        ]

        functionValues = [
            [sg.Frame(layout=[
                [sg.Text('Time Constant (\u03F4)', size=defaultSize), sg.InputText(key='-tau-', size=defaultSize)],
                [sg.Text('m[k]'), sg.InputText(key='-mk-', size=defaultSize)],
                [sg.Text('Input Disturbance', size=defaultSize), sg.InputText(key='-inputD-', size=defaultSize)],
                [sg.Text('Output Disturbance', size=defaultSize), sg.InputText(key='-outputD-', size=defaultSize)]
            ], title='')]
        ]

        # Avoid reusing layout
        layout = [
            # Canvas
            [sg.Text('Discrete Control Model Grapher')],
            [sg.Canvas(key='-CANVAS-')],
            [sg.Frame('Inputs', tableFrame, pad=(0, 5)), sg.Frame(
                '', coefficientsFrame, pad=(0, (14, 5)), key='Hide')],
            # Input Values
            [sg.Frame('Values', valuesFrame, pad=(0, 5)), sg.Frame(
                '', functionValues, pad=(0, (14, 5)), key='Hide')],
            # Window Buttons
            [sg.Button('Submit'), sg.Button('Show Plot'), sg.Button('Close')]
        ]

        windowTemp = sg.Window(
            'Discrete Model Grapher',
            location=(0, 0),
            finalize=True,
            element_justification='center',
            font='Helvetica 18').Layout(layout).Finalize()
        window.Close()
        window = windowTemp

        # Store submitted values in global variables
        k = values['-k-']
        T = values['-T-']
        tPrime = values['-tPrime-']
        inDist = values['-inputD-']
        outDist = values['-outputD-']
        tau = values['-tau-']
        mk = values['-mk-']

        tempM = mk
        mn.append(tempM)

        fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)

        # Define Transfer Function
        num = np.array([2])
        den = np.array([3, 1])
        # num = np.array([1.2])
        # den = np.array([-0.5, -0.8])

        H = signal.TransferFunction(num, den)
        t, y = signal.step(H)

        plt.plot(t, y)
        plt.title('Step Response')
        plt.xlabel('t')
        plt.ylabel('y')
        plt.grid()

        fig.add_subplot(111).plot(plt.show())

        draw_figure(window['-CANVAS-'].TKCanvas, fig)

        if a[1] != None: a1 = a[1]
        if a[2] != None: a2 = a[2]
        if a[3] != None: a3 = a[3]
        if a[4] != None: a4 = a[4]

        if b[1] != None: b1 = b[1]
        if b[2] != None: b2 = b[2]
        if b[3] != None: b3 = b[3]
        if b[4] != None: b4 = b[4]

        for i in range(4):
            cn[i] = (a1*c[i + 1]) + (a2*c[i + 2]) + \
                     (b1*m[i + 1 + d]) + (b2*m[i + 2 + d])

        plt.plot(cn, t)
        plt.grid()

        fig.add_subplot(111).plot(plt.show())

    if values['-mk-'] == None:
        print('Updating mn...')
        print('\ntempM')
        mn.append(tempM)
    
    for i in range(numA):
        ai = values['-a-' + str(i)]
        if ai != None:
            a.append(ai)
        else:
            a.append(0)

    for i in range(numB):
        bi = values['-b-' + str(i)]
        if bi != None:
            b.append(values['-b-' + str(i)])
        else:
            b.append(0)

window.close()

# References
# https://apmonitor.com/wiki/index.php/Apps/ARXTimeSeries
# https://apmonitor.com/do/index.php/Main/ModelIdentification
# https://www.youtube.com/watch?v=8HdUoWXLNOs
