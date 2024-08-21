stdscr = None
screen_data_path = None
def _start(_stdscr):
    from os.path import dirname, abspath
    import sys
    global stdscr, screen_data_path
    screen_data_path = sys._MEIPASS if getattr(sys, 'frozen', False) else (dirname(abspath(__file__)) + '/..')  + '/screen_data'
    stdscr = _stdscr
    
def _update(): pass
def _end(): pass