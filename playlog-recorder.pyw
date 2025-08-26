from tkinter import *
from tkinter import ttk
# from tkinter.ttk import *

# adapted from <https://stackoverflow.com/a/14910894>
def center_window(root, width=300, height=200):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # calculate position x and y coordinates
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))

root = Tk()
root.title('Steam Playlog Recorder')
center_window(root, 250, 110)

frm = ttk.Frame(root, padding=10)
frm.grid()

LABEL_SIDE = 'w' or 'e' or None

# TODO: combobox for game name
Label(frm, text='Game:').grid(column=0, row=0, sticky=LABEL_SIDE)
Entry(frm).grid(column=1, row=0)

Label(frm, text='Last played:').grid(column=0, row=1, sticky=LABEL_SIDE)
Entry(frm).grid(column=1, row=1)

Label(frm, text='Play time:').grid(column=0, row=2, sticky=LABEL_SIDE)

sf = Frame(frm)
sf.grid(column=1, row=2, sticky='w')
Entry(sf, width=7).grid(column=0, row=0)
Label(sf, text='hours').grid(column=1, row=0)

ttk.Button(frm, text='Save entry').grid(column=1, row=3, sticky='e')

root.mainloop()
