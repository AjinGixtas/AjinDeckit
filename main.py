from curses import wrapper, curs_set, error
from time import sleep, perf_counter
from components import key_state_tracker, scene_manager, resources
def _main(stdscr):
    global old_settings
    resources._start(stdscr)
    scene_manager._start()
    key_state_tracker._start()
    production_mode = False
    curs_set(0)
    origin_x, origin_y, rows, columns = scene_manager.get_drawable_screen_data()
    
    if rows < 26 or columns < 118:
        print("The window size is too small, some feature and graphic will not be rendered correctly. Consider resizing it!")
        print(f"Current dimension: {columns}×{rows}, required: 118×26")
        return
    while True:
        start = perf_counter()
        if not production_mode: scene_manager.current_page._update()
        else: 
            try: scene_manager.current_page._update()
            except error as e: 
                print("Error encountered! Maybe resizing the terminal window?")
                _end()
                return
            except DatabaseError as e:
                print("Save data corrupted! \nPlease send it to ajingixtascontact@gmail.com for the author to investigate. \nLook at the `Contact` section in the 'README.MD' file for more detail.")
            except Exception as e:
                print("Unexpected error encountered! \nIf the error persist, please report it at ajingixtascontact@gmail.com \nLook at the `Contact` section in the 'README.MD' file for more detail.")
                _end()
                return
        if key_state_tracker.get_key_state('q'): scene_manager.change_page(scene_manager.MENU_INDEX)
        if (key_state_tracker.get_key_state('ctrl', key_state_tracker.PRESSED) and key_state_tracker.get_key_state('q', key_state_tracker.JUST_PRESSED)) or (key_state_tracker.get_key_state('ctrl', key_state_tracker.JUST_PRESSED) and key_state_tracker.get_key_state('q', key_state_tracker.PRESSED)):
            _end()
            return
        key_state_tracker._update()
        end = perf_counter()
        sleep(max(0, 0.015625 - end+start))
def _end():
    from sys import exit
    resources._end()
    key_state_tracker._end()
    scene_manager._end()
    exit()
if __name__ == '__main__':
    wrapper(_main)