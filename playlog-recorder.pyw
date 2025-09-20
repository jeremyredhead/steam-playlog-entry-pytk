#==LOGIC SECTION==
import os
import datetime
import textwrap
import collections

# Constants
DATE_FORMATS = [
    '%Y %b. %d, %I:%M %p',
    '%Y %b %d, %I:%M %p',
    '%Y %B %d, %I:%M %p',
    '%I:%M %p %m/%d/%Y', # Ms. Notepad's F5 date formatting
]
PREF_DATE_FMT = DATE_FORMATS[0]

def parse_date(s):
    parse = datetime.datetime.strptime
    for fmt in DATE_FORMATS:
        try:
            return parse(s, fmt)
        except:
            pass
    return None

# adapted from <https://stackoverflow.com/a/7406369>
def sanitize_filename(filename):
    """Sanitize a string so it is legal filename (replaces slash characters too!)"""
    is_legal = lambda c: c.isalnum() or c in ('.', '_')
    # TODO: sanitize more better
    filename = ''.join(c if is_legal(c) else '-' for c in filename).strip()
    return filename

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

class Playlog():
    # constants also used by PlaylogFolder
    FILE_SUFFIX = '-playlog.txt'
    NAME_MARKER = 'NAME:'

    def __init__(self, file, file_suffix=None, name_marker=None):
        self.file = file # fullpath or os.DirEntry ?
        self.file_suffix = file_suffix or self.FILE_SUFFIX
        self.name_marker = name_marker or self.NAME_MARKER
        self.game = self._get_game_name()
        self.entries = [] # initialized in self.refresh()
        self.refresh()

    def write_entry(self, entry):
        # TODO: verify that entry is a PlaylogEntry or nah?
        with open(self.file, 'a+t') as f:
            f.write(str(entry))
        self.refresh()

    def _get_game_name(self):
        filename = os.path.basename(self.file)
        # used as a fallback when a file lacks a NAME: line
        name = filename.removesuffix(self.file_suffix).replace('-', ' ')
        with open(self.file) as f:
            first_line = f.readline()
            if first_line.startswith(self.name_marker):
                name = first_line.removeprefix(self.name_marker).strip()
        return name

    def refresh(self):
        entries = []
        with open(self.file) as fd:
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
        self.entries = entries

class PlaylogFolder():
    """A folder with Playlogs in it. Duh."""

    PLAYLOGS_FOLDER = os.path.join(os.path.expanduser('~'), 'Documents', 'playlogs')

    def __init__(self, path=None, *, log_suffix=None, log_name_marker=None):
        # XXX: what if path doesn't exist or isn't a folder?
        self.path = path or self.PLAYLOGS_FOLDER
        self.log_suffix = log_suffix or Playlog.FILE_SUFFIX
        self.log_name_marker = log_name_marker or Playlog.NAME_MARKER
        self._logs = [] # initialized in self.refresh()
        self.refresh()

    def new_playlog(self, game):
        # rough opposite of Playlog._get_game_name
        filename = sanitize_filename(game.lower() + self.log_suffix)
        filename = os.path.join(self.path, filename)
        # XXX: what do if file exist??
        with open(filename, 'x+t') as f:
            f.write(f'{self.log_name_marker} {game}\n')
        new_log = self._Playlog(filename)
        self._logs.append(new_log)
        return new_log

    def write_entry(self, *, game, entry):
        logs = self.get_playlogs_for(game)
        if not logs:
            log = self.new_playlog(game)
        elif len(logs) == 1:
            log = logs[0]
        else:
            raise NotImplementedError("fuck me i'm bad at coding. or designing. w/e")
        log.write_entry(entry)

    def _Playlog(self, file):
        return Playlog(file, file_suffix=self.log_suffix, name_marker=self.log_name_marker)

    def refresh(self):
        is_playlog = lambda f: f.is_file() and f.name.endswith(self.log_suffix)
        files = [f for f in os.scandir(self.path) if is_playlog(f)]
        logs = [self._Playlog(file) for file in files]
        self._logs = logs

    def game_names(self):
        # TODO: sort order?
        return [playlog.game for playlog in self._logs]

    @staticmethod
    # TODO: instead return number representing how close a match
    def compare_names(name_a, name_b):
        return name_a.lower() == name_b.lower()

    def get_playlogs_for(self, game):
        """Return list of playlogs that possibly record that game."""
        return [log for log in self._logs if self.compare_names(log.game, game)]

    def get_last_played_for(self, game):
        logs = self.get_playlogs_for(game)
        if not logs:
            return '(never)'
        elif len(logs) == 1:
            entries = logs[0].entries
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
from tkinter.ttk import *

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
        frm = Frame(root, padding=10)
        frm.grid()

        # REMINDER: .get() to get a field's value (.insert() and .delete() to alter a text field)

        LABEL_SIDE = self.LABEL_SIDE

        Label(frm, text='Game:').grid(column=0, row=0, sticky=LABEL_SIDE)
        self.game_var = StringVar()
        self.game_select = Combobox(frm, textvariable=self.game_var)
        self.game_select.grid(column=1, row=0)
        self.game_select.focus()

        self.refresh_games_dropdown()
        self.game_select.bind('<<ComboboxSelected>>', self.refresh_last_played_dropdown)
        self.game_var.trace_add('write', lambda *_: self.refresh_last_played_dropdown({}))

        Label(frm, text='Last played:').grid(column=0, row=1, sticky=LABEL_SIDE)
        self.last_played = Combobox(frm)
        self.last_played.grid(column=1, row=1)
        self.last_played['values'] = ['(never)']

        Label(frm, text='Play time:').grid(column=0, row=2, sticky=LABEL_SIDE)

        sf = Frame(frm)
        sf.grid(column=1, row=2, sticky='w')
        self.play_time = Entry(sf, width=7)
        self.play_time.grid(column=0, row=0)
        Label(sf, text='hours').grid(column=1, row=0)

        save_button = Button(frm, text='Save entry', command=self.save_entry)
        save_button.grid(column=1, row=3, sticky='e')
        # are you fucking kidding me Tk. really?? you make me do this??
        save_button.bind('<Return>', lambda e: save_button.invoke())

        root.bind('<Escape>', self.maybe_close_window)

        frm.rowconfigure(0, pad=2)
        frm.rowconfigure(1, pad=2)
        frm.rowconfigure(2, pad=2)

    def save_entry(self):
        fields = (self.game_select, self.last_played, self.play_time)
        values = [field.get() for field in fields]
        if not all(values):
            return # TODO: display an error message via Label
        new_entry = PlaylogEntry.now(values[1], values[2])
        try:
            PLAYLOG_HOLDER.write_entry(game=values[0], entry=new_entry)
        except BaseException as err:
            print(err)
            return # TODO: display an error message via Label
        for field in fields:
            field.delete(0, END)
        self.refresh_games_dropdown() # in case of new playlog
        self.game_select.focus()

    def maybe_close_window(self, event):
        fields = (self.game_select, self.last_played, self.play_time)
        values = [field.get() for field in fields]
        if not any(values):
            root.destroy()

    def refresh_games_dropdown(self):
        # TODO: auto-completing combo box
        self.game_select['values'] = PLAYLOG_HOLDER.game_names()

    def refresh_last_played_dropdown(self, event):
        last_played = PLAYLOG_HOLDER.get_last_played_for(self.game_select.get())
        self.last_played.config(values=[last_played])

root = Tk()
# TODO: look into .iconbitmap() et al to set window icon to a custom thing
root.title('Steam Playlog Recorder')
# so we can actually see the whole title; may only work on Windows™️
# doesn't show up in taskbar if -toolwindow is set :c
##root.attributes('-toolwindow', True)
center_window(root, 250, 113)
playlog_entry = AddPlaylogEntry(root)

import sys
if 'idlelib' in sys.modules:
    root.update()
    root.attributes('-topmost', True)
else:
    root.mainloop()
