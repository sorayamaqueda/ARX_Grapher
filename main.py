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

from cProfile import label
import control.matlab as control
import scipy.signal as signal
import matplotlib.pyplot as plt
import PySimpleGUI as sg  # Graphic Interface Library
import numpy as np  # Math Library
import matplotlib  # Grapher Library

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from math import e, trunc, sqrt, cos, sin

matplotlib.use('TkAgg')

# Global Design Variables
defaultSize = (15, 1)
showPlot = False

# Global Modeling Variables
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
d = 0 # Delay
m = 0 # Modified Z Transform
zeta = 0
wn = 0
kc = 0 # Controller
tauI = 0 # Integrador
tauD = 0 # Derivator
kMax = 0

# Coefficients (Maximum 4 per coefficient)
# If not given, value must be 0
a = 0
a1 = 0
a2 = 0
a3 = 0
a4 = 0

b = 0
b0 = 0
b1 = 0
b2 = 0
b3 = 0
b4 = 0

beta0 = 0
beta1 = 0
beta2 = 0

# Result lists
cn = []
mn = []
mc = []
err = []
tempM = 0

# Case Control Flags
isARX  = True
isFOM = False
isSOM = False
isAutomatic = False

# Function to draw Graph
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)

    return figure_canvas_agg

def cn_graph(input):
    plt.plot(cn, input, color='blue', marker='o')
    plt.scatter(cn, input)
    plt.title('Response', fontsize=14)
    plt.ylabel('c(k)')
    plt.xlabel('k')
    plt.grid(True)
    plt.show()

    return plt.gcf()

def error_graph(input):
    plt.plot(err, input, color='red', marker='x')
    plt.title('Error')
    plt.ylabel('e(k)')
    plt.xlabel('k')
    plt.grid(True)
    plt.show()

    return plt.gcf()

def mn_graph(input):
    plt.plot(mn, input, color='black', marker='o')
    plt.title('Input')
    plt.ylabel('m(k)')
    plt.xlabel('k')
    plt.grid(True)
    plt.show()

    return plt.gcf()

def mc_graph(input):
    plt.plot(mc, input, color='purple', marker='o')
    plt.title('Controller')
    plt.ylabel('mc(k)')
    plt.xlabel('k')
    plt.grid(True)
    plt.show()

    return plt.gcf()

# Theme and Styling
sg.theme('DarkBlue')
sg.set_options(font=('Courier New', 12))

# Coefficients
coefficientsFrame = [
    [sg.Frame(layout=[
            [sg.Text('a')],
            #                                                                       a1 - a4
            *[[sg.Text('a' + str(i)), sg.InputText(key='-a-' + str(i)), ] for i in (n+1 for n in range(4))],
            [sg.Text('b')],
            #                                                                   b0 - b4
            *[[sg.Text('b' + str(i)), sg.InputText(key='-b-' + str(i)), ] for i in range(4)],
        ], title='')]
]

# Values
valuesFrame = [
    [sg.Frame(layout=[
        [sg.Text('Delay (d)', size=defaultSize),
                 sg.InputText(key='-d-', size=defaultSize)],
        [sg.Text('Time Interval (T)', size=defaultSize),
                 sg.InputText(key='-T-', size=defaultSize)],
        [sg.Text('k Max:'), sg.InputText(key='-kMax-', size=defaultSize)],
    ], title='')]
]

# Constant Values for Models
functionValues = [
    [sg.Frame(layout=[
        [sg.Text('m[k]'), sg.InputText(key='-mk-', size=defaultSize)],
        [sg.Text('Input Disturbance', size=defaultSize),
                 sg.InputText(key='-inputD-', size=defaultSize)],
        [sg.Text('Output Disturbance', size=defaultSize),
                 sg.InputText(key='-outputD-', size=defaultSize)]
    ], title='')]
]

# Menu
models = [
    [sg.Radio('Model ARX', key='-ARX-', group_id='models', enable_events=True, default=True),
    sg.Radio('First Order Model', key='-FOM-', group_id='models', enable_events=True),
    sg.Radio('Second Order Low Damp Model', key='-SOM-', group_id='models', enable_events=True),
    sg.Radio('Automatic', key='-CTRL-', group_id='models', enable_events=True)]
]

# Buttons
buttons = [
    [sg.Button('Plot'), sg.Button('Close')]
]

# Define the Layout
layout = [
    # Canvas
    [sg.Text('Discrete Control Model Grapher')],
    [sg.Canvas(key='-CANVAS-')],
    # Coefficients
    [sg.Frame('Coefficients', coefficientsFrame, pad=(0, (14, 5)), key='Hide')],
    # Input Values
    [sg.Frame('Values', valuesFrame, pad=(0, 5)), sg.Frame(
        '', functionValues, pad=(0, (14, 5)), key='Hide')],
    # Event Buttons and Menu
    [sg.Frame('Menu', models)], [sg.Frame('', buttons)]
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

# Create an event loop
while True:
    event, values = window.read()
    # End program if user closes window or presses the Close button
    if event == 'Close' or event == sg.WIN_CLOSED:
        break

    # Enable plot visibility
    if event == 'Plot':
        showPlot = True

        # We store any values that the user has given depending on the mode 
        if isARX:
            T = float(values['-T-'])
            inDist = float(values['-inputD-'])
            outDist = float(values['-outputD-'])
            d = int(values['-d-'])
            mk = int(values['-mk-'])
            a1 = float(values['-a-1'])
            a2 = float(values['-a-2'])
            a3 = float(values['-a-3'])
            a4 = float(values['-a-3'])
            b0 = float(values['-b-0'])
            b1 = float(values['-b-1'])
            b2 = float(values['-b-2'])
            b3 = float(values['-b-3'])
            #b4 = float(values['-b-4'])
            kMax = int(values['-kMax-'])
        elif isFOM == True:
            tPrime = float(values['-tPrime-'])
            T = float(values['-T-'])
            tau = float(values['-tau-'])
            m = 1 - (t/T)
            d = trunc(tPrime / T)
            t = tPrime - (d*T)
            mk = int(values['-mk-'])
            kMax = int(values['-kMax-'])
            a1 = e**(-T / tau)
            a2 = 0
            a3 = 0
            a4 = 0
            b0 = 0
            b1 = k*(1 - e**(-m*T/tau))
            b2 = k*(e**(-m*T/tau) - e**(-T/tau))
            b3 = 0
            b4 = 0
        elif isSOM == True:
            k = int(values['-k-'])
            tPrime = float(values['-tPrime-'])
            wn = float(values['-naturalFreq-'])
            zeta = float(values['-zeta-'])
            mk = int(values['-mk-'])
            a = wn * zeta
            try: 
                b = wn * sqrt(1 - zeta**2) 
            except ZeroDivisionError: 
                b = 0
            try:
                d = trunc(tPrime / T)
            except ZeroDivisionError:
                d = 0
            a1 = (2*e**(2*a*T))*cos(b*T)
            a2 = e**(-2*a*T)
            a3 = 0
            a4 = 0
            b0 = 0
            b1 = k * (1 - (e**(-a*T))*cos(b*T)- (a/b)*e**(-a*T)*sin(b*T))
            b2 = k * ((e**(-a*T)) + (a/b)*e**(-a*T)*sin(b*T) - (e**(-a*T))*cos(b*T))
            kMax = int(values['-kMax-'])
        elif isAutomatic:
            tauD = float(values['-tauD-'])
            tauI = float(values['-tauI-'])
            kc = float(values['-kC-'])
            T = float(values['-T-'])
            mk = int(values['-mk-'])
            beta0 = kc*(1 + (T/tauI) + (tauD/T))
            beta1 = kc*(-1 - (2*tauD/T))
            beta2 = kc*(tauD/T)
            kMax = int(values['-kMax-'])
            a1 = float(values['-a-1'])
            b0 = float(values['-b-0'])
            b1 = float(values['-b-1'])

        tempM = mk
        v = 0
        for i in range(kMax):
            mn.append(float(mk))

        # All values before mk are 0 for cn
        cn.extend([0]*mk)
        delay = int(d)
        k = 0
        lim = kMax - d - 4
        #while k < lim:
        for k in range(lim):
            cn.append((a1*cn[k + 1]) + (a2*cn[k + 2]) + (a3*cn[k + 3]) + (a4*cn[k + 4]) + (b0*mn[k + delay]) + (b1*mn[k + 1 + delay]) + (b2*mn[k + 2 + delay]) + (b3*mn[k + 3 + delay]) + (b4*mn[k + 4 + delay]))
            k+=1

        if isAutomatic:
            errLim = 0
            for k in range(kMax - 1):
                err.append(mn[k] - cn[k])

            for k in range(lim):
                mc.append(mn[k+1] + (beta0*err[k]) + (beta1*err[k+1]) + (beta2*err[k+2]))

        if not isAutomatic:
            plt.plot(cn, list(np.arange(1, len(cn) + 1)), color='blue', marker='o', label='c(k)')
            plt.scatter(cn, list(np.arange(1, len(cn) + 1)))
            plt.plot(mn, list(np.arange(1, len(mn) + 1)), color='black', marker='o', label='m(k)')
            plt.ylabel('k')
            plt.title('Manual Control')
            plt.legend()
            plt.show()
            fig = plt.gcf()
            draw_figure(window['-CANVAS-'].TKCanvas, fig)        
        else:
            plt.plot(cn, list(np.arange(1, len(cn) + 1)), color='blue', marker='o', label='c(k)')
            plt.scatter(cn, list(np.arange(1, len(cn) + 1)))
            plt.plot(err, list(np.arange(1, len(err) + 1)), color='red', marker='x', label='e(k)')
            plt.plot(mn, list(np.arange(1, len(mn) + 1)), color='black', marker='o', label='m(k)')
            plt.plot(mc, list(np.arange(1, len(mc) + 1)), color='purple', marker='o', label='mc(k)')
            plt.ylabel('k')
            plt.title('Automatic Control')
            plt.legend()
            plt.show()
            fig = plt.gcf()
            draw_figure(window['-CANVAS-'].TKCanvas, fig)
    
    if values['-ARX-']:
        isARX = True
        isFOM = False
        isAutomatic = False
        isSOM = False

        # Coefficients
        coefficientsFrame = [
            [sg.Frame(layout=[
                [sg.Text('a')],
                *[[sg.Text('a' + str(i)), sg.InputText(key='-a-' + str(i)), ] for i in (n+1 for n in range(4))],
                [sg.Text('b')],
                *[[sg.Text('b' + str(i)), sg.InputText(key='-b-' + str(i)), ] for i in range(4)],
            ], title='')]
        ]

        # Values
        valuesFrame = [
            [sg.Frame(layout=[
                [sg.Text('Delay (d)', size=defaultSize), sg.InputText(key='-d-', size=defaultSize)],
                [sg.Text('Time Interval (T)', size=defaultSize), sg.InputText(key='-T-', size=defaultSize)],
                [sg.Text('k Max:'), sg.InputText(key='-kMax-', size=defaultSize)],
                [sg.Text('Constant (k)', size=defaultSize), sg.InputText(key='-k-', size=defaultSize)]
            ], title='')]
        ]

        # Constant Values for Models
        functionValues = [
            [sg.Frame(layout=[
                [sg.Text('m[k]'), sg.InputText(key='-mk-', size=defaultSize)],
                [sg.Text('Input Disturbance', size=defaultSize), sg.InputText(key='-inputD-', size=defaultSize)],
                [sg.Text('Output Disturbance', size=defaultSize), sg.InputText(key='-outputD-', size=defaultSize)]
            ], title='')]
        ]

        # Menu
        models = [
            [sg.Radio('Model ARX', key='-ARX-', group_id='models', enable_events=True, default=True),
            sg.Radio('First Order Model', key='-FOM-', group_id='models', enable_events=True),
            sg.Radio('Second Order Low Damp Model', key='-SOM-', group_id='models', enable_events=True),
            sg.Radio('Automatic', key='-CTRL-', group_id='models', enable_events=True)]
        ]

        # Buttons
        buttons = [
            [sg.Button('Plot'), sg.Button('Close')]
        ]

        # Define the Layout
        layout = [
            # Canvas
            [sg.Text('Discrete Control Model Grapher')],
            [sg.Canvas(key='-CANVAS-')],
            # Coefficients
            [sg.Frame('Coefficients', coefficientsFrame, pad=(0, (14, 5)), key='Hide')],
            # Input Values
            [sg.Frame('Values', valuesFrame, pad=(0, 5)), sg.Frame(
            '', functionValues, pad=(0, (14, 5)), key='Hide')],
            # Event Buttons and Menu
            [sg.Frame('Menu', models)], [sg.Frame('', buttons)]
        ]

    if values['-SOM-']:
        isARX = False
        isFOM = False
        isAutomatic = False
        isSOM = True

        # Coefficients
        coefficientsFrame = [
        [sg.Frame(layout=[
                [sg.Text('a')],
                [sg.Text('a1 = 2*e^(-a*T)*cos(b*T)')],
                [sg.Text('a2 = -e^(-2*a*T)')],
                [sg.Text('b')],
                [sg.Text('b1 = k*[1-e^(-a*T)*cos(b*T) - (a/b)*e^(-a*T)*sin(b*T)]')],
                [sg.Text('b2 = k*[e^(-2*a*T) + (a/b)*e^(-a*T)*cos(b*T)]')]
            ], title='')]
        ]

        # Values
        valuesFrame = [
            [sg.Frame(layout=[
                [sg.Text('Constant (k)', size=defaultSize),
                sg.InputText(key='-k-', size=defaultSize)],
                [sg.Text("\u03F4'", size=defaultSize), sg.InputText(
                key='-tPrime-', size=defaultSize)],
                [sg.Text('Time Interval (T)', size=defaultSize),
                sg.InputText(key='-T-', size=defaultSize)],
                [sg.Text('k Max:'), sg.InputText(key='-kMax-', size=defaultSize)],
                [sg.Text('Zeta', size=defaultSize), 
                sg.InputText(key='-zeta-', size=defaultSize)],
                [sg.Text('Wn', size=defaultSize),
                sg.InputText(key='-naturalFreq-', size=defaultSize)],
                [sg.Text('m[k]'), sg.InputText(key='-mk-', size=defaultSize)]
            ], title='')]
        ]

        # Menu
        models = [
            [sg.Radio('Model ARX', key='-ARX-', group_id='models', enable_events=True),
            sg.Radio('First Order Model', key='-FOM-', group_id='models', enable_events=True),
            sg.Radio('Second Order Low Damp Model', key='-SOM-', group_id='models', enable_events=True, default=True),
            sg.Radio('Automatic', key='-CTRL-', group_id='models', enable_events=True)]
        ]

        # Buttons
        buttons = [
            [sg.Button('Plot'), sg.Button('Close')]
        ]

        # Define the Layout
        layout = [
            # Canvas
            [sg.Text('Discrete Control Model Grapher')],
            [sg.Canvas(key='-CANVAS-')],
            # Input Values
            [sg.Frame('Values', valuesFrame, pad=(0, 5))],
            # Event Buttons and Menu
            [sg.Frame('Menu', models)], [sg.Frame('', buttons)]
        ]

        windowTemp = sg.Window(
            'Discrete Model Grapher',
            location=(0, 0),
            finalize=True,
            element_justification='center',
            font='Helvetica 18'
        ).Layout(layout).Finalize()
        window.Close()
        window = windowTemp

    if values['-FOM-']:
        isARX = False
        isFOM = True
        isAutomatic = False
        isSOM = False

        coefficientsFrame = [
            [sg.Frame(layout=[
                [sg.Text('a')],
                [sg.Text('a1 = e^(-T/𝜏)')],
                [sg.Text('b')],
                [sg.Text('b1 = k*[1 - e^(-m*T/' + '𝜏' + ')]')],
                [sg.Text('b2 = k*[e^(-m*T/𝜏) - a1]')]
            ], title='')]
        ]

        # Values
        valuesFrame = [
            [sg.Frame(layout=[
                [sg.Text('Constant (k)', size=defaultSize),
                sg.InputText(key='-k-', size=defaultSize)],
                [sg.Text("\u03F4'", size=defaultSize), sg.InputText(
                key='-tPrime-', size=defaultSize)],
                [sg.Text('Time Interval (T)', size=defaultSize),
                sg.InputText(key='-T-', size=defaultSize)],
                [sg.Text('k Max:'), sg.InputText(key='-kMax-', size=defaultSize)],
                [sg.Text('Time Constant (𝜏)', size=defaultSize), sg.InputText(key='-tau-', size=defaultSize)],
                [sg.Text('m[k]'), sg.InputText(key='-mk-', size=defaultSize)]
            ], title='')]
        ]

        # Menu
        models = [
            [sg.Radio('Model ARX', key='-ARX-', group_id='models', enable_events=True),
            sg.Radio('First Order Model', key='-FOM-', group_id='models', enable_events=True, default=True),
            sg.Radio('Second Order Low Damp Model', key='-SOM-', group_id='models', enable_events=True),
            sg.Radio('Automatic', key='-CTRL-', group_id='models', enable_events=True)]
        ]

        # Buttons
        buttons = [
            [sg.Button('Plot'), sg.Button('Close')]
        ]

        # Define the Layout
        layout = [
            # Canvas
            [sg.Text('Discrete Control Model Grapher')],
            [sg.Canvas(key='-CANVAS-')],
            # Coefficients and table
            [sg.Frame('Coefficients', coefficientsFrame, pad=(0, (14, 5)), key='Hide')],
            # Input Values
            [sg.Frame('Inputs', valuesFrame, pad=(0, 5))],
            # Event Buttons and Menu
            [sg.Frame('Menu', models)], [sg.Frame('', buttons)]
        ]

        windowTemp = sg.Window(
            'Discrete Model Grapher',
            location=(0, 0),
            finalize=True,
            element_justification='center',
            font='Helvetica 18'
        ).Layout(layout).Finalize()
        window.Close()
        window = windowTemp

    if values['-CTRL-']:
        isARX = False
        isFOM = False
        isAutomatic = True
        isSOM = False

        coefficientsFrame = [
            [sg.Frame(layout=[
                [sg.Text('β')],
                [sg.Text('β0 = Kc*[1 + (T/𝜏i) + (𝜏d/T)]')],
                [sg.Text('β1 = Kc*[-1 - (2*𝜏d/T)]')],
                [sg.Text('β2 = Kc*[𝜏d/T]')],
                [sg.Text('a')],
                *[[sg.Text('a' + str(i)), sg.InputText(key='-a-' + str(i)), ] for i in (n+1 for n in range(1))],
                [sg.Text('b')],
                *[[sg.Text('b' + str(i)), sg.InputText(key='-b-' + str(i)), ] for i in range(2)],
            ], title='')]
        ]

        valuesFrame = [
            [sg.Frame(layout=[
                [sg.Text('Controller (kc)', size=defaultSize),
                sg.InputText(key='-kC-', size=defaultSize)],
                [sg.Text('Time Interval (T)', size=defaultSize),
                sg.InputText(key='-T-', size=defaultSize)],
                [sg.Text('k Max:'), sg.InputText(key='-kMax-', size=defaultSize)]
            ], title='')]
        ]

        # Constant Values for Models
        functionValues = [
            [sg.Frame(layout=[
                [sg.Text('Integrator (𝜏):', size=defaultSize),
                sg.InputText(key='-tauI-', size=defaultSize)],
                [sg.Text('Derivator (𝜏):', size=defaultSize),
                sg.InputText(key='-tauD-', size=defaultSize)],
                [sg.Text('m[k]'), sg.InputText(key='-mk-', size=defaultSize)],
            ], title='')]
        ]

        # Menu
        models = [
            [sg.Radio('Model ARX', key='-ARX-', group_id='models', enable_events=True),
            sg.Radio('First Order Model', key='-FOM-', group_id='models', enable_events=True),
            sg.Radio('Second Order Low Damp Model', key='-SOM-', group_id='models', enable_events=True),
            sg.Radio('Automatic', key='-CTRL-', group_id='models', enable_events=True, default=True)]
        ]

        # Buttons
        buttons = [
            [sg.Button('Plot'), sg.Button('Close')]
        ]

        # Define the Layout
        layout = [
            # Canvas
            [sg.Text('Discrete Control Model Grapher')],
            [sg.Canvas(key='-CANVAS-')],
            # Coefficients and table
            [sg.Frame('Coefficients', coefficientsFrame, pad=(0, (14, 5)), key='Hide')],
            # Input Values
            [sg.Frame('Values', valuesFrame, pad=(0, 5)), sg.Frame(
                '', functionValues, pad=(0, (14, 5)), key='Hide')],
            # Event Buttons and Menu
            [sg.Frame('Menu', models)], [sg.Frame('', buttons)]
        ]

        windowTemp = sg.Window(
            'Discrete Model Grapher',
            location=(0, 0),
            finalize=True,
            element_justification='center',
            font='Helvetica 18'
        ).Layout(layout).Finalize()
        window.Close()
        window = windowTemp

window.close()

# References
# https://apmonitor.com/wiki/index.php/Apps/ARXTimeSeries
# https://apmonitor.com/do/index.php/Main/ModelIdentification
# https://www.youtube.com/watch?v=8HdUoWXLNOs
