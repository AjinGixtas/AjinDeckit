import curses

ScreenH = 0
ScreenW = 0
CursorX = 1
CursorY = 1

def repaint(screen):   
   global ScreenH
   global ScreenW
   global CursorX
   global CursorY

   ScreenH, ScreenW = screen.getmaxyx()
   cloc = 'OO'
   cloclen =  len (cloc)
   screen.addstr(ScreenH - 2, ScreenW - cloclen, cloc,  curses.color_pair(1));
   screen.addstr(ScreenH - 1, ScreenW - cloclen, cloc,  curses.color_pair(1));


def Main(screen):
   curses.init_pair (1, curses.COLOR_WHITE, curses.COLOR_BLUE)
   repaint (screen)   

   while True:
      ch = screen.getch()
      if ch == ord('q'):
         break

      repaint (screen)     


curses.wrapper(Main)