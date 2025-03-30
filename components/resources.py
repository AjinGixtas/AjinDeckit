from curses import start_color, init_pair, color_pair, COLOR_BLUE, COLOR_CYAN, COLOR_RED, COLOR_GREEN, COLOR_BLACK, COLOR_YELLOW, COLOR_MAGENTA, A_DIM
from pathlib import Path
stdscr = None
screen_data_path = None
SUITS_INDEX_DICT = { 'C':1, 'S':2, 'D':3, 'H':4 }
def _start(_stdscr):
    from os.path import dirname, abspath
    import sys
    global stdscr, screen_data_path

    start_color()
    init_pair(1, COLOR_BLUE, COLOR_BLACK)
    init_pair(2, COLOR_CYAN, COLOR_BLACK)
    init_pair(3, COLOR_YELLOW, COLOR_BLACK)
    init_pair(4, COLOR_RED, COLOR_BLACK)
    init_pair(5, COLOR_GREEN, COLOR_BLACK)
    init_pair(6, COLOR_MAGENTA, COLOR_BLACK)
    init_pair(7, COLOR_BLACK, COLOR_BLACK)
    screen_data_path = Path(sys._MEIPASS if getattr(sys, 'frozen', False) else (dirname(abspath(__file__)) + '/..')  + '/screen_data')
    stdscr = _stdscr
# There is no standarized numbering system yet, just wing it!
def get_color_pair_obj(index): return color_pair(index)
def _update(): pass
def _end(): pass
def clip_range(value, min, max): return min if value < min else max if max < value else value
def get_first_dupe_index(arr, val):
    for i in range(len(arr)): 
        if arr[i] == val: return i
    return -1
