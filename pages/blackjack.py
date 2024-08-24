from components import resources, image_drawer, scene_manager
from components.key_state_tracker import get_key_state, get_axis
from curses import newpad
KEY_MAP_DISPLAY_TABLE = [0,0,0,0,0,0,1,1,1]
origin_x, origin_y, rows, columns = 0, 0, 0, 0
TABLE_DIV, DRAW_PILE_DIV = {}, {}
def _start():
    global origin_x, origin_y, rows, columns
    origin_x, origin_y, rows, columns = scene_manager.get_drawable_screen_data()
    render_board()
def _update(): 
    global TABLE_DIV
    pass
def _end():
    global TABLE_DIV
    TABLE_DIV['pad'].clear()
    TABLE_DIV['pad'] = None
def render_board():
    global TABLE_DIV
    with open(resources.screen_data_path / 'blackjack.txt', 'r', encoding='utf-8') as f:
        TABLE_DIV['size'] = tuple(map(int, f.readline().split()))
        TABLE_DIV['pad'] = newpad(TABLE_DIV['size'][0], TABLE_DIV['size'][1])
        for i in range(TABLE_DIV['size'][0]):
            TABLE_DIV['pad'].insstr(i, 0, f.readline().rstrip())
    TABLE_DIV['origin'] = ((rows - TABLE_DIV['size'][0])//2+1 , (columns - TABLE_DIV['size'][1]) // 2+1)
    TABLE_DIV['end'] = (TABLE_DIV['origin'][0] + TABLE_DIV['size'][0], TABLE_DIV['origin'][1] + TABLE_DIV['size'][1])
    TABLE_DIV['pad'].refresh(0, 0, TABLE_DIV['origin'][0], TABLE_DIV['origin'][1], TABLE_DIV['end'][0], TABLE_DIV['end'][1])
def render_deck():
    global DECK_DIV
    with open(resources.screen_data_path / 'blackjack_deck.txt', 'r', encoding='utf-8') as f:
        DECK_DIV['size'] = tuple(map(int, f.readline().split()))
        DECK_DIV['pad'] = newpad(DECK_DIV['size'][0], DECK_DIV['size'][1])
        for i in range(DECK_DIV['size'][0]):
            DECK_DIV['pad'].insstr(i, 0, f.readline().rstrip())
    DECK_DIV['origin'] = ((rows - DECK_DIV['size'][0])//2+1 , (columns - DECK_DIV['size'][1]) // 2+1)
    DECK_DIV['end'] = (DECK_DIV['origin'][0] + DECK_DIV['size'][0], DECK_DIV['origin'][1] + DECK_DIV['size'][1])
    DECK_DIV['pad'].refresh(0, 0, DECK_DIV['origin'][0], DECK_DIV['origin'][1], DECK_DIV['end'][0], DECK_DIV['end'][1])