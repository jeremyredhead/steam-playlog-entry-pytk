#==LOGIC SECTION==
import os
import datetime
import textwrap
from collections import namedtuple

# Constants
DATE_FORMATS = ['%Y %b. %d, %I:%M %p', '%Y %B %d, %I:%M %p']
PREF_DATE_FMT = DATE_FORMATS[0]
PLAYLOG_SUFFIX = '-playlog.txt'
NAMELINE_PREFIX = 'NAME:'

def parse_date(s):
    parse = datetime.datetime.strptime
    for fmt in DATE_FORMATS:
        try:
            return parse(s, fmt)
        except:
            pass
    return None

Game = namedtuple('Game', ['file', 'name'])
def list_games(path=None):
    games = [f for f in os.listdir(path) if f.endswith(PLAYLOG_SUFFIX)]
    games = [Game(f, f.removesuffix(PLAYLOG_SUFFIX).replace('-', ' ')) for f in games]
    for i, game in enumerate(games):
        with open(game.file) as f:
            first_line = f.readline()
            if first_line.startswith(NAMELINE_PREFIX):
                name = first_line.removeprefix(NAMELINE_PREFIX).strip()
                games[i] = game._replace(name=name)
    return games

def assemble_entry(last_played, play_time):
    # FIXME: ensure consistent results in date locale-wise
    date = datetime.datetime.now().strftime(PREF_DATE_FMT)
    entry = f"""\
    {date}:
    \tlast played: {last_played}
    \tplay time: {play_time} hours
    """
    return textwrap.dedent(entry)


#==UI SECTION==
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

class AddPlaylogEntry:
    # 'w' (left), 'e' (right), or None (centered)
    LABEL_SIDE = 'e'

    def __init__(self, root):
        frm = ttk.Frame(root, padding=10)
        frm.grid()

        LABEL_SIDE = self.LABEL_SIDE
        Label(frm, text='Game:').grid(column=0, row=0, sticky=LABEL_SIDE)
        self.game_select = ttk.Combobox(frm)
        self.game_select.grid(column=1, row=0)
        # TODO: fetch values from files on disk
        # XXX: how to correlate game name to filename? what if multiple files for one game?
        self.game_select['values'] = ['Spelunky 2', 'Among Us', 'UFO 50']

        Label(frm, text='Last played:').grid(column=0, row=1, sticky=LABEL_SIDE)
        self.last_played = ttk.Combobox(frm)
        self.last_played.grid(column=1, row=1)
        # TODO: fetch value (singular) from last entry of selected game's playlog
        # XXX: what if no entry/file? try to render an Entry instead in that case?
        self.last_played['values'] = ['Jul 13']

        Label(frm, text='Play time:').grid(column=0, row=2, sticky=LABEL_SIDE)

        sf = Frame(frm)
        sf.grid(column=1, row=2, sticky='w')
        self.play_time = Entry(sf, width=7)
        self.play_time.grid(column=0, row=0)
        Label(sf, text='hours').grid(column=1, row=0)

        ttk.Button(frm, text='Save entry').grid(column=1, row=3, sticky='e')

        frm.rowconfigure(0, pad=2)
        frm.rowconfigure(1, pad=2)

root = Tk()
root.title('Steam Playlog Recorder')
center_window(root, 250, 110)
AddPlaylogEntry(root)

import sys
if 'idlelib' in sys.modules:
    root.update()
    root.attributes('-topmost', True)
else:
    root.mainloop()
