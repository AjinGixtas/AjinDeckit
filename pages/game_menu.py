from components import resources, scene_manager
from components.key_state_tracker import get_key_state, get_axis
from curses import newpad
KEY_MAP_DISPLAY_TABLE = ['game_menu']
origin_x, origin_y, rows, columns = 0, 0, 0, 0
MENU_DIV = {}
def _start():
    global origin_x, origin_y, rows, columns, MENU_DIV
    origin_x, origin_y, rows, columns = scene_manager.get_drawable_screen_data()
    MENU_DIV = { 
        'cursor_options_value' : (scene_manager.BLACKJACK_INDEX, scene_manager.REGICIDE_INDEX, scene_manager.ROYAL_EXECUTION_INDEX),
        'cursor_pos_arr' : ((2, 7), (2, 35), (2, 63)),
        'cursor_pos' : 0
    }
    with open(resources.screen_data_path / 'game_menu.txt', 'r', encoding='utf-8') as f:
        MENU_DIV['size'] = tuple(map(int, f.readline().split()))
        MENU_DIV['pad'] = newpad(MENU_DIV['size'][0], MENU_DIV['size'][1])
        for i in range(MENU_DIV['size'][0]):
            MENU_DIV['pad'].insstr(i, 0, f.readline().rstrip())
    MENU_DIV['origin'] = ((rows - MENU_DIV['size'][0]) // 2, (columns - MENU_DIV['size'][1]) //2)
    MENU_DIV['end'] = (MENU_DIV['origin'][0] + MENU_DIV['size'][0], MENU_DIV['origin'][1] + MENU_DIV['size'][1])
    MENU_DIV['pad'].addstr(MENU_DIV['cursor_pos_arr'][MENU_DIV['cursor_pos']][0], MENU_DIV['cursor_pos_arr'][MENU_DIV['cursor_pos']][1], '*')
    MENU_DIV['pad'].refresh(0, 0, MENU_DIV['origin'][0], MENU_DIV['origin'][1], MENU_DIV['end'][0], MENU_DIV['end'][1])
def _update(): 
    global MENU_DIV
    move_vector = get_axis('a', 'd')
    if move_vector != 0:
        MENU_DIV['pad'].addstr(MENU_DIV['cursor_pos_arr'][MENU_DIV['cursor_pos']][0], MENU_DIV['cursor_pos_arr'][MENU_DIV['cursor_pos']][1], ' ')
        MENU_DIV['cursor_pos'] = resources.clip_range(MENU_DIV['cursor_pos'] + move_vector, 0, 2)
        MENU_DIV['pad'].addstr(MENU_DIV['cursor_pos_arr'][MENU_DIV['cursor_pos']][0], MENU_DIV['cursor_pos_arr'][MENU_DIV['cursor_pos']][1], '*')
        MENU_DIV['pad'].refresh(0, 0, MENU_DIV['origin'][0], MENU_DIV['origin'][1], MENU_DIV['end'][0], MENU_DIV['end'][1])
    if get_key_state('enter'): scene_manager.change_page(MENU_DIV['cursor_options_value'][MENU_DIV['cursor_pos']])
def _end():
    global MENU_DIV
    MENU_DIV['pad'].clear()
    MENU_DIV['pad'] = None