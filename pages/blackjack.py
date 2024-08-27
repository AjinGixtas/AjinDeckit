from components import resources, image_drawer, scene_manager, key_state_tracker
from components.key_state_tracker import get_key_state, get_axis
from curses import newpad
from random import randint
KEY_MAP_DISPLAY_TABLE = [0,0,0,0,0,0,1,1,1]
origin_x, origin_y, rows, columns = 0, 0, 0, 0
BOARD_DIV   = { 'index':0, 'src':'blackjack_board.txt', 'deck':[], 'player_hand':[], 'dealer_hand':[] }
DECK_DIV    = { 'index':1, 'src':'blackjack_deck.txt', 'card_counts':{}, 'x_pos':(2,6,10,14,18,22,26,30,34,38,42,46,50,56), 'y_pos':(0,8,16,24) }
SETTING_DIV = { 'index':2, 'src':'blackjack_setting.txt', 'cursor_option_values':[0,0,1], 'cursor_option_ranges':((0,1),(0,1),(1,9)), 'cursor_display_values':(('-HIT-','STAND'),('← _ →','← * →'),2),'cursor_index':0}

RANKS, SUITS = ['C','S','D','H'], ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
def _start():
    global origin_x, origin_y, rows, columns
    origin_x, origin_y, rows, columns = scene_manager.get_drawable_screen_data()
    new_game()

def _update(): 
    if key_state_tracker.get_key_state('ctrl', key_state_tracker.JUST_PRESSED) and key_state_tracker.get_key_state('s', key_state_tracker.JUST_PRESSED): 
        render_div(SETTING_DIV)
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
    draw_random_card()
    if key_state_tracker.get_key_state('e', key_state_tracker.JUST_PRESSED):
        render_div(DECK_DIV)
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
    if key_state_tracker.get_key_state('r', key_state_tracker.JUST_PRESSED):
        # Surrender
        pass
    if key_state_tracker.get_key_state('w', key_state_tracker.JUST_PRESSED):
        # Finish turn
        pass
    render_div(BOARD_DIV)
def update_deck():
    if key_state_tracker.get_key_state('e', key_state_tracker.JUST_PRESSED): render_div(BOARD_DIV)

cursor_option_values = None
def update_setting():
    global SETTING_DIV, cursor_option_values
    if key_state_tracker.get_key_state('e', key_state_tracker.JUST_PRESSED): 
        render_div(BOARD_DIV)
        return
    if key_state_tracker.get_key_state('enter', key_state_tracker.JUST_PRESSED):
        new_game()
        SETTING_DIV['cursor_option_values'] = cursor_option_values
        return
    move_vector = key_state_tracker.get_axis('w', 's', 'a', 'd')
    if move_vector[0] != 0:
        SETTING_DIV['pad'].addstr(9 + SETTING_DIV['cursor_index'], 11, '(')
        SETTING_DIV['pad'].addstr(9 + SETTING_DIV['cursor_index'], 17, ')')
        SETTING_DIV['cursor_index'] = resources.clip_range(SETTING_DIV['cursor_index'] + move_vector[0], 0, 2)
        SETTING_DIV['pad'].addstr(9 + SETTING_DIV['cursor_index'], 11, '[')
        SETTING_DIV['pad'].addstr(9 + SETTING_DIV['cursor_index'], 17, ']')
    if move_vector[1] != 0:
        cursor_option_values[SETTING_DIV['cursor_index']] = resources.clip_range(SETTING_DIV['cursor_option_values'][SETTING_DIV['cursor_index']] + move_vector[1], SETTING_DIV['cursor_option_ranges'][SETTING_DIV['cursor_index']][0], SETTING_DIV['cursor_option_ranges'][SETTING_DIV['cursor_index']][1])
        if type(SETTING_DIV['cursor_display_values'][SETTING_DIV['cursor_index']]) == int:
            SETTING_DIV['pad'].addstr(9 + SETTING_DIV['cursor_index'], 12 + SETTING_DIV['cursor_display_values'][SETTING_DIV['cursor_index']], str(SETTING_DIV['cursor_option_values'][SETTING_DIV['cursor_index']]))
        else:
            SETTING_DIV['pad'].addstr(9 + SETTING_DIV['cursor_index'], 12, SETTING_DIV['cursor_display_values'][SETTING_DIV['cursor_index']][cursor_option_values[SETTING_DIV['cursor_index']]])
    render_div(SETTING_DIV)

def new_game():
    global curent_focus_zone_index, DECK, PLAYER_HAND, DEALER_HAND, BOARD_DIV, DECK_DIV, SETTING_DIV
    curent_focus_zone_index = BOARD_DIV['index']
    BOARD_DIV, DECK_DIV, SETTING_DIV = build_div(BOARD_DIV), build_div(DECK_DIV), build_div(SETTING_DIV)
    BOARD_DIV['deck'], BOARD_DIV['player_hand'], BOARD_DIV['dealer_hand'] = [f'{rank}{suit}' for suit in SUITS for rank in RANKS for _ in range(SETTING_DIV['cursor_option_values'][2])], [], []
    DECK_DIV['card_counts'] = {f'{rank}{suit}': SETTING_DIV['cursor_option_values'][2] for suit in SUITS for rank in RANKS}
    
    [DECK_DIV['pad'].addstr(y, x, str(SETTING_DIV['cursor_option_values'][2])) for x in DECK_DIV['x_pos'] for y in DECK_DIV['y_pos']]
    
    BOARD_DIV['pad'].addstr(16, 110, str(52 * SETTING_DIV['cursor_option_values'][2]).rjust(3, '0'))
    BOARD_DIV['pad'].addstr(16, 106, str(len(BOARD_DIV['deck'])).rjust(3, '0'))
    BOARD_DIV['pad'].refresh(0, 0, BOARD_DIV['origin'][0], BOARD_DIV['origin'][1], BOARD_DIV['end'][0], BOARD_DIV['end'][1])

def build_div(div):
    with open(resources.screen_data_path / div['src'], 'r', encoding='utf-8') as f:
        div['size'] = tuple(map(int, f.readline().split()))
        div['pad'] = newpad(div['size'][0], div['size'][1])
        for i in range(div['size'][0]):
            div['pad'].insstr(i, 0, f.readline().rstrip())
    if div.get('cursor_index', None) != None:
        for i in range(len(div['cursor_option_values'])):
            if type(SETTING_DIV['cursor_display_values'][i]) == int: div['pad'].addstr(9+i, 13+SETTING_DIV['cursor_display_values'][i], str(SETTING_DIV['cursor_option_values'][i]))
            else: div['pad'].addstr(9+i, 12, SETTING_DIV['cursor_display_values'][i][SETTING_DIV['cursor_option_values'][i]])
    div['origin'] = ((rows - div['size'][0])//2+1 , (columns - div['size'][1]) // 2+1)
    div['end'] = (div['origin'][0] + div['size'][0], div['origin'][1] + div['size'][1])
    return div
def draw_random_card():
    global BOARD_DIV
    BOARD_DIV['pad'].addstr(16, 106, str(len(BOARD_DIV['deck']) - 1))
    return BOARD_DIV['deck'].pop(randint(0, len(BOARD_DIV['deck']) - 1))
def reveal_hold_card(card_name):
    global DECK_DIV
    DECK_DIV['card_counts'][card_name] -= 1
    DECK_DIV['pad'].addstr(DECK_DIV['y_pos'][resources.get_first_dupe_index(SUITS, card_name[1])], DECK_DIV['x_pos'][resources.get_first_dupe_index(RANKS, card_name[0])], str(DECK_DIV['card_counts'][card_name]))
def render_div(div): 
    global curent_focus_zone_index, BOARD_DIV, DECK_DIV, SETTING_DIV, cursor_option_values
    curent_focus_zone_index = div['index']
    cursor_option_values = SETTING_DIV.get('cursor_option_values', None)
    div['pad'].refresh(0, 0, div['origin'][0], div['origin'][1], div['end'][0], div['end'][1])
