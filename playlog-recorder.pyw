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

class PlaylogEntry():
    def __init__(self, entry_date, last_played, play_time):
        self.entry_date = entry_date
        self.last_played = last_played
        self.play_time = play_time

    @classmethod
    def now(Class, last_played, play_time):
        # FIXME: ensure consistent results in date locale-wise
        entry_date = datetime.datetime.now().strftime(PREF_DATE_FMT)
        return Class(entry_date, last_played, play_time)

    def __str__(self):
        entry = f"""\
        {self.entry_date}:
        \tlast played: {self.last_played}
        \tplay time: {self.play_time} hours
        """
        return textwrap.dedent(entry)

    def __repr__(self):
        name = type(self).__name__
        args = ', '.join([f'{k}={repr(v)}' for (k,v) in vars(self).items()])
        return f'{name}({args})'

def parse_playlog_entries(file):
    entries = []
    with open(file) as fd:
        for line in fd:
            line = line.rstrip()
            if not line: continue
            if line[-1] == ':':
                entries.append(PlaylogEntry(line[:-1], '', ''))
            # indented by tab or at least two spaces
            elif line[0] == '\t' or line[0:2] == '  ':
                key, value = line.lstrip().split(': ', 1)
                if key.lower() == 'last played':
                    entries[-1].last_played = value
                if key.lower() == 'play time':
                    entries[-1].play_time = value.removesuffix('hours').strip()
                # ignore unrecognized keys
            else:
                pass # ignore unrecognized lines
    return entries

Playlog = collections.namedtuple('Playlog', ['file', 'game'])

class PlaylogFolder():
    """A folder with Playlogs in it. Duh."""

    FILENAME_SUFFIX = '-playlog.txt'
    NAMELINE_PREFIX = 'NAME:'
    PLAYLOGS_FOLDER = os.path.join(os.path.expanduser('~'), 'Documents', 'playlogs')

    # TODO: allow configuring prefix/suffix(s) via keyword arguments
    def __init__(self, path=None):
        # XXX: what if path doesn't exist or isn't a folder?
        self.path = path or self.PLAYLOGS_FOLDER
        self.update()

    def _get_game_name(self, file):
        # used as a fallback when a file lacks a NAME: line
        name = os.path.basename(file).removesuffix(self.FILENAME_SUFFIX).replace('-', ' ')
        with open(file) as f:
            first_line = f.readline()
            if first_line.startswith(self.NAMELINE_PREFIX):
                name = first_line.removeprefix(self.NAMELINE_PREFIX).strip()
        return name

    def update(self):
        is_playlog = lambda f: f.is_file() and f.name.endswith(self.FILENAME_SUFFIX)
        files = [f for f in os.scandir(self.path) if is_playlog(f)]
        logs = [Playlog(f.path, game=self._get_game_name(f)) for f in files]
        self._logs = logs

    def game_names(self):
        # TODO: sort order?
        return [playlog.game for playlog in self._logs]

    @classmethod
    # TODO: instead return number representing how close a match
    def compare_names(Class, name_a, name_b):
        return name_a.lower() == name_b.lower()

    def get_filenames_for(self, game):
        """Return list of playlog files that possibly record that game."""
        return [p.file for p in self._logs if self.compare_names(p.game, game)]

    def get_last_played_for(self, game):
        files = self.get_filenames_for(game)
        if not files:
            return '(never)'
        elif len(files) == 1:
            entries = parse_playlog_entries(files[0])
            if not entries:
                return '(never)'
            entry_date_text = entries[-1].entry_date
            date = parse_date(entry_date_text)
            if date:
                if date.year == datetime.datetime.now().year:
                    return date.strftime('%b %d')
                else:
                    return date.strftime('%b %d, %Y')
            else:
                return entry_date_text
        else:
            return 'Unknown (duplicate playlogs error!)'


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

PLAYLOG_HOLDER = PlaylogFolder()

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
        self.game_select['values'] = PLAYLOG_HOLDER.game_names()
        self.game_select.bind('<<ComboboxSelected>>', lambda e: self.last_played.config(values=[PLAYLOG_HOLDER.get_last_played_for(self.game_select.get())]))

        Label(frm, text='Last played:').grid(column=0, row=1, sticky=LABEL_SIDE)
        self.last_played = ttk.Combobox(frm)
        self.last_played.grid(column=1, row=1)
        self.last_played['values'] = ['(never)']

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
