import PySimpleGUI as sg # Graphic Interface Library
import numpy as np # Math Library
import pandas as pd # Data Analysis Library
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import oceans

matplotlib.use('TkAgg')

# Function to draw Graph 
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

# Define the Layout
layout = [
    [sg.Text('ARX Graphic')],
    [sg.Canvas(key='-CANVAS-')],
    [sg.Button('OK')]
]

# Create the window
window = sg.Window(
    'ARX Graphic', # Window Title
    layout, # Window Layout
    location=(0, 0),
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
    # presses the OK button
    if event == 'OK' or event == sg.WIN_CLOSED:
        break

window.close()