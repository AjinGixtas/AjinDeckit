from components import resources, image_drawer, scene_manager, key_state_tracker
from components.key_state_tracker import get_key_state, get_axis
from curses import newpad
KEY_MAP_DISPLAY_TABLE = [0,0,0,0,0,0,1,1,1]
origin_x, origin_y, rows, columns = 0, 0, 0, 0
BOARD_DIV, DECK_DIV, SETTING_DIV, DECK_DATA = { 'index':0 }, { 'index':1 }, { 'index': 2,  'cursor_options_value' : (False, False, 1), 'cursor_pos_arr' : ((1, 3), (2, 3), (3, 5)), 'cursor_index' : 0 }, {}
curent_focus_zone_index = BOARD_DIV['index']

RANK, SUITS = ['C','S','D','H'], ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
PLAYER_HAND, DEALER_HAND = [], []
SOFT_17_STAND, BLACKJACK_PEAK = False, False
def _start():
    global origin_x, origin_y, rows, columns, BOARD_DIV, DECK_DIV, SETTING_DIV
    origin_x, origin_y, rows, columns = scene_manager.get_drawable_screen_data()
    BOARD_DIV = build_div(BOARD_DIV, 'blackjack_board.txt')
    DECK_DIV = build_div(DECK_DIV, 'blackjack_deck.txt')
    SETTING_DIV = build_div(SETTING_DIV, 'blackjack_setting.txt')
    render_div(BOARD_DIV)
def _update(): 
    if curent_focus_zone_index == BOARD_DIV['index']: update_board()
    elif curent_focus_zone_index == DECK_DIV['index']: update_deck()
    elif curent_focus_zone_index == SETTING_DIV['index']: update_setting()
def _end():
    global BOARD_DIV, DECK_DIV, SETTING_DIV
    if SETTING_DIV != None: SETTING_DIV['pad'].clear()
    if BOARD_DIV != None: BOARD_DIV['pad'].clear()
    if DECK_DIV['pad'] != None: DECK_DIV['pad'].clear()
    BOARD_DIV['pad'] = None
    DECK_DIV['pad'] = None
def update_board():
    if key_state_tracker.get_key_state('a', key_state_tracker.JUST_PRESSED):
        render_div(DECK_DIV)
        return
    if key_state_tracker.get_key_state('q', key_state_tracker.JUST_PRESSED):
        render_div(SETTING_DIV)
        return
    if key_state_tracker.get_key_state('s', key_state_tracker.JUST_PRESSED):
        # Draw card
        pass
    if key_state_tracker.get_key_state('d', key_state_tracker.JUST_PRESSED):
        # Double down
        pass
    if key_state_tracker.get_key_state('f', key_state_tracker.JUST_PRESSED):
        # Split
        pass
    if key_state_tracker.get_key_state('g', key_state_tracker.JUST_PRESSED):
        # Surrender
        pass
def update_deck():
    if key_state_tracker.get_key_state('a', key_state_tracker.JUST_PRESSED): render_div(BOARD_DIV)
    
def update_setting():
    pass

def build_div(div, file_path):
    with open(resources.screen_data_path / file_path, 'r', encoding='utf-8') as f:
        div['size'] = tuple(map(int, f.readline().split()))
        div['pad'] = newpad(div['size'][0], div['size'][1])
        for i in range(div['size'][0]):
            div['pad'].insstr(i, 0, f.readline().rstrip())
    div['origin'] = ((rows - div['size'][0])//2+1 , (columns - div['size'][1]) // 2+1)
    div['end'] = (div['origin'][0] + div['size'][0], div['origin'][1] + div['size'][1])
    return div
def render_div(div): 
    global curent_focus_zone_index
    curent_focus_zone_index = div['index']
    div['pad'].refresh(0, 0, div['origin'][0], div['origin'][1], div['end'][0], div['end'][1])