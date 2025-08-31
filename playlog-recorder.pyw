#==LOGIC SECTION==
import os
import datetime
import textwrap
import collections

# Constants
DATE_FORMATS = ['%Y %b. %d, %I:%M %p', '%Y %B %d, %I:%M %p']
PREF_DATE_FMT = DATE_FORMATS[0]

def parse_date(s):
    parse = datetime.datetime.strptime
    for fmt in DATE_FORMATS:
        try:
            return parse(s, fmt)
        except:
            pass
    return None

Playlog = collections.namedtuple('Playlog', ['file', 'game'])

class PlaylogList(collections.UserList):
    """List of Playlogs. Duh."""

    FILENAME_SUFFIX = '-playlog.txt'
    NAMELINE_PREFIX = 'NAME:'
    PLAYLOGS_FOLDER = os.path.join(os.path.expanduser('~'), 'Documents', 'playlogs')

    # TODO: allow configuring prefix/suffix(s) via keyword arguments
    # -- may require inheriting from list instead, see <https://stackoverflow.com/a/76769083>
    def __init__(self, playlogs=None):
        super().__init__(playlogs)
        self.data = playlogs or []

    @classmethod
    def filename_to_gamename(Class, filename):
        return filename.removesuffix(Class.FILENAME_SUFFIX).replace('-', ' ')

    # FIXME: better more descriptive name
    # FIXME: shouldn't require supplied path to be the current dir FFS
    @classmethod
    def generate(Class, path=None):
        os.chdir(path) # HACK
        files = [f for f in os.listdir(path) if f.endswith(Class.FILENAME_SUFFIX)]
        logs = [Playlog(f, game=Class.filename_to_gamename(f)) for f in files]
        for i, log in enumerate(logs):
            with open(log.file) as f:
                first_line = f.readline()
                if first_line.startswith(Class.NAMELINE_PREFIX):
                    name = first_line.removeprefix(Class.NAMELINE_PREFIX).strip()
                    logs[i] = log._replace(game=name)
        return Class(logs)

    def game_names(self):
        # TODO: sort order?
        return [playlog.game for playlog in self.data]

    @classmethod
    # TODO: instead return number representing how close a match
    def compare_names(Class, name_a, name_b):
        return name_a.lower() == name_b.lower()

    def get_filenames_for(self, game):
        """Return list of playlog files that possibly record that game."""
        return [p.file for p in self.data if self.compare_names(p.game, game)]

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
