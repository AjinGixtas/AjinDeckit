# --- AI CODE START ---
import logging

logging.basicConfig(
    filename='royal_execution.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
# --- AI CODE END ---


from components import resources, image_drawer, scene_manager, key_state_tracker
from components.key_state_tracker import get_key_state, get_axis
from curses import newpad, color_pair
from random import randint, shuffle
KEY_MAP_DISPLAY_TABLE=['royal_execution']
BOARD_DIV = {
    'index': 0, 'src': 'boards/royal_execution_board.txt', 'pad': None,
    'draw_pile': [], 'discard_pile': [], 'royal_piles': [ [], [], [], [] ], 'executor_piles': [ [], [], [], [] ], 'hand': [],
    'deck_progress_index': 0,
    'selected_card_index': -1, 'selected_pile_index': -1,
}
SETTING_DIV = {
}
SUIT_SYMBOL, SUITS, RANKS, POINTS = ('♣','♠','♦','♥',), ('C', 'S', 'D', 'H'), ('A','2','3','4','5','6','7','8','9','10','J','Q','K'), (1,2,3,4,5,6,7,8,9,10,11,12,13)
# Entry function
def _start():
    global origin_x, origin_y, rows, columns, BOARD_DIV
    origin_x, origin_y, rows, columns = scene_manager.get_drawable_screen_data()
    BOARD_DIV = build_div(BOARD_DIV)
    setup_var()
    new_game()
    render_div(BOARD_DIV)
# Run every frame
def _update():
    update_board()
# Exit function
def _end():
    return

def setup_var():
    BOARD_DIV['royal_card_zone_anchor'] = (3,1)
    BOARD_DIV['royal_card_anchors'] = (((0,1),(0,2),(0,3)),((12,1),(12,2),(12,3)),((24,1),(24,2),(24,3)),((36,1),(36,2),(36,3)))
    BOARD_DIV['royal_pile_zone'] = ((0,0), (44,12))
    BOARD_DIV['drew_card_anchors'] = ((55, 3), (58, 3), (61, 3))
    BOARD_DIV['royal_pile_cursor_anchor_points'] = ((9, 14), (21, 14), (33, 14), (45, 14))
    BOARD_DIV['pad'].addstr(
        BOARD_DIV['royal_card_zone_anchor'][1] + BOARD_DIV['royal_pile_cursor_anchor_points'][0][1], 
        BOARD_DIV['royal_card_zone_anchor'][0] + BOARD_DIV['royal_pile_cursor_anchor_points'][0][0], '[z]')
    BOARD_DIV['pad'].addstr(
        BOARD_DIV['royal_card_zone_anchor'][1] + BOARD_DIV['royal_pile_cursor_anchor_points'][1][1], 
        BOARD_DIV['royal_card_zone_anchor'][0] + BOARD_DIV['royal_pile_cursor_anchor_points'][1][0], '[x]')
    BOARD_DIV['pad'].addstr(
        BOARD_DIV['royal_card_zone_anchor'][1] + BOARD_DIV['royal_pile_cursor_anchor_points'][2][1], 
        BOARD_DIV['royal_card_zone_anchor'][0] + BOARD_DIV['royal_pile_cursor_anchor_points'][2][0], '[c]')
    BOARD_DIV['pad'].addstr(
        BOARD_DIV['royal_card_zone_anchor'][1] + BOARD_DIV['royal_pile_cursor_anchor_points'][3][1], 
        BOARD_DIV['royal_card_zone_anchor'][0] + BOARD_DIV['royal_pile_cursor_anchor_points'][3][0], '[v]')
def build_div(div):
    with open(resources.screen_data_path / div['src'], 'r', encoding='utf-8') as f:
        div['size'] = tuple(map(int, f.readline().split()))
        div['pad'] = newpad(div['size'][0], div['size'][1])
        for i in range(div['size'][0]):
            div['pad'].insstr(i, 0, f.readline().rstrip())
    if div.get('cursor_index', None) != None:
        SETTING_DIV['pad'].addstr(6 + SETTING_DIV['cursor_index'], 10, '>')
        SETTING_DIV['pad'].addstr(6 + SETTING_DIV['cursor_index'], 16, '<')
        for i in range(len(div['cursor_option_values'])):
            if type(SETTING_DIV['cursor_display_values'][i]) == int: div['pad'].addstr(6+i, 11+SETTING_DIV['cursor_display_values'][i], str(SETTING_DIV['cursor_option_values'][i]))
            else: div['pad'].addstr(6+i, 11, SETTING_DIV['cursor_display_values'][i][SETTING_DIV['cursor_option_values'][i]])
    div['origin'] = ((rows - div['size'][0])//2+1 , (columns - div['size'][1]) // 2+1)
    div['end'] = (div['origin'][0] + div['size'][0], div['origin'][1] + div['size'][1])
    return div
def render_div(div): 
    global curent_focus_zone_index, BOARD_DIV, DECK_DIV, SETTING_DIV, cursor_option_values
    curent_focus_zone_index = div['index']
    cursor_option_values = SETTING_DIV.get('cursor_option_values', None)
    div['pad'].refresh(0, 0, div['origin'][0], div['origin'][1], div['end'][0], div['end'][1])
def new_game():
    global BOARD_DIV
    BOARD_DIV['royal_piles'] = [ [], [], [], [] ]
    BOARD_DIV['draw_pile'] = []
    BOARD_DIV['discard_pile'] = []
    BOARD_DIV['hand'] = []
    
    for tavern_rank in ('A','2','3','4','5','6','7','8','9','10'):
        for suit in SUITS:
            BOARD_DIV['draw_pile'].append(tavern_rank+suit)
    shuffle(BOARD_DIV['draw_pile'])
    
    royal_pile = []
    for royal_rank in ('K', 'Q', 'J'):
        rank_pile = []
        for suit in SUITS:
            rank_pile.append(royal_rank + suit)
        shuffle(rank_pile)  
        royal_pile += rank_pile
    shuffle(royal_pile)
    marker = 0
    for i in range(4):
        for j in range(3):
            BOARD_DIV['royal_piles'][i].append(royal_pile[marker])
            marker += 1
    render_royal_piles()
    render_draw_pile()

def draw_hand():
    global BOARD_DIV
    # Discard all remaining card in hand
    BOARD_DIV['discard_pile'] += BOARD_DIV['hand']
    BOARD_DIV['hand'] = []
    for i in range(3):
        if not draw_card():
            lose()
            break
    render_draw_pile()
def draw_card():
    global BOARD_DIV
    if len(BOARD_DIV['draw_pile']) == 0:
        return False
    if len(BOARD_DIV['draw_pile']) > 0:
        BOARD_DIV['hand'].append(BOARD_DIV['draw_pile'].pop())
    return True

def play_card() -> int:
    global BOARD_DIV
    if BOARD_DIV['selected_card_index'] == -1 or BOARD_DIV['selected_pile_index'] == -1:
        return 1 # No card selected
    if len(BOARD_DIV['hand']) == 0:
        return 2 # No card in hand
    if len(BOARD_DIV['executor_piles'][BOARD_DIV['selected_pile_index']]) > 3:
        return 3 # executor pile is full
    card = BOARD_DIV['hand'][BOARD_DIV['selected_card_index']]
    if rank(card) == 'K' or rank(card) == 'Q' or rank(card) == 'J':
        return 4 # HOW DID THESE ROYAL CARDS GET IN HAND?
    executor_index = len(BOARD_DIV['executor_piles'][BOARD_DIV['selected_pile_index']])
    if (executor_index == 0 and 
            point(rank(BOARD_DIV['hand'][BOARD_DIV['selected_card_index']])) < 
            point(rank(BOARD_DIV['royal_piles'][BOARD_DIV['selected_pile_index']][-1])) - 10
        ):
        return 5 # First card fail the minimum point check
    if (executor_index == 1 and 
            point(rank(BOARD_DIV['hand'][BOARD_DIV['selected_card_index']])) + 
            point(rank(BOARD_DIV['executor_piles'][BOARD_DIV['selected_pile_index']][0])) <
            point(rank(BOARD_DIV['royal_piles'][BOARD_DIV['selected_pile_index']][-1]))
        ):
        return 6 # Second card fail the point check
    if (executor_index == 2 and 
            suit(BOARD_DIV['hand'][BOARD_DIV['selected_card_index']]) != 
            suit(BOARD_DIV['royal_piles'][BOARD_DIV['selected_pile_index']][-1])
        ): 
        return 7 # Third card fail the suit check
    if len(BOARD_DIV['royal_piles'][BOARD_DIV['selected_pile_index']]) == 0: 
        return 8 # No royal card in the pile
    
    BOARD_DIV['executor_piles'][BOARD_DIV['selected_pile_index']].append(BOARD_DIV['hand'].pop(BOARD_DIV['selected_card_index']))
    BOARD_DIV['selected_card_index'] = -1
    if executor_index == 2: # If the executor pile is full, remove the royal card
        BOARD_DIV['royal_piles'][BOARD_DIV['selected_pile_index']].pop()
        BOARD_DIV['executor_piles'][BOARD_DIV['selected_pile_index']].clear()
    render_royal_piles()
    render_draw_pile()
    return 0


def render_royal_piles():
    global BOARD_DIV
    keybind_char = ['z', 'x', 'c', 'v']
    for i in range(15):
        BOARD_DIV['pad'].addstr(BOARD_DIV['royal_card_zone_anchor'][1] + 1 + i, BOARD_DIV['royal_card_zone_anchor'][0], ' ' * 49)
    for x in range(4):
        executor_pile_anchor_x = 0
        # --- Render Royal cards ---
        for y in range(len(BOARD_DIV['royal_piles'][x])):
            if y != len(BOARD_DIV['royal_piles'][x])-1: 
                image_drawer.draw_colored_image(
                    BOARD_DIV['pad'], 
                    resources.screen_data_path/'drawings'/'cards'/'___card.txt', 
                    BOARD_DIV['royal_card_zone_anchor'][0] + BOARD_DIV['royal_card_anchors'][x][y][0], 
                    BOARD_DIV['royal_card_zone_anchor'][1] + BOARD_DIV['royal_card_anchors'][x][y][1], 
                    color_pair_obj=resources.get_color_pair_obj(5))
            else:
                image_drawer.draw_colored_image(BOARD_DIV['pad'], 
                resources.screen_data_path/'drawings'/'cards'/f'{BOARD_DIV['royal_piles'][x][y]}.txt', 
                BOARD_DIV['royal_card_zone_anchor'][0] + BOARD_DIV['royal_card_anchors'][x][y][0], 
                BOARD_DIV['royal_card_zone_anchor'][1] + BOARD_DIV['royal_card_anchors'][x][y][1], 
                color_pair_obj=resources.get_color_pair_obj((1+SUITS.index(suit(BOARD_DIV['royal_piles'][x][y])))))
                executor_pile_anchor_x = BOARD_DIV['royal_card_zone_anchor'][1] + BOARD_DIV['royal_card_anchors'][x][y][1] + 2
            if x == BOARD_DIV['selected_pile_index']:
                BOARD_DIV['pad'].addstr(
                    BOARD_DIV['royal_card_zone_anchor'][1] + BOARD_DIV['royal_pile_cursor_anchor_points'][x][1], 
                    BOARD_DIV['royal_card_zone_anchor'][0] + BOARD_DIV['royal_pile_cursor_anchor_points'][x][0], f'[{keybind_char[x]}]')
            else:
                BOARD_DIV['pad'].addstr(
                    BOARD_DIV['royal_card_zone_anchor'][1] + BOARD_DIV['royal_pile_cursor_anchor_points'][x][1], 
                    BOARD_DIV['royal_card_zone_anchor'][0] + BOARD_DIV['royal_pile_cursor_anchor_points'][x][0], f' {keybind_char[x]} ')
        # --- Render Executor cards ---
        for y in range(len(BOARD_DIV['executor_piles'][x])):
            image_drawer.draw_colored_image(BOARD_DIV['pad'], 
                resources.screen_data_path/'drawings'/'cards'/f'{BOARD_DIV['executor_piles'][x][y]}.txt', 
                BOARD_DIV['royal_card_zone_anchor'][0] + BOARD_DIV['royal_card_anchors'][x][y][0], 
                executor_pile_anchor_x + y * 2, 
                color_pair_obj=resources.get_color_pair_obj((1+SUITS.index(suit(BOARD_DIV['executor_piles'][x][y])))))
    render_div(BOARD_DIV) # FUCK IT

def render_draw_pile():
    BOARD_DIV['pad'].addstr(BOARD_DIV['royal_card_zone_anchor'][1] + 2, BOARD_DIV['royal_card_zone_anchor'][0] + 52, f'×{len(BOARD_DIV["draw_pile"])}')

    for i in range(-1, 7, 1):
        BOARD_DIV['pad'].addstr(
            BOARD_DIV['royal_card_zone_anchor'][1] + BOARD_DIV['drew_card_anchors'][0][1] + i, 
            BOARD_DIV['royal_card_zone_anchor'][0] + BOARD_DIV['drew_card_anchors'][0][0], ' ' * 16)
    image_drawer.draw_colored_image(
                    BOARD_DIV['pad'], 
                    resources.screen_data_path/'drawings'/'cards'/'___card.txt', 
                    BOARD_DIV['royal_card_zone_anchor'][0]+51, BOARD_DIV['royal_card_zone_anchor'][1] + 3, color_pair_obj=resources.get_color_pair_obj(5))
    for i in range(len(BOARD_DIV['hand'])):
        image_drawer.draw_colored_image(
            BOARD_DIV['pad'], 
            resources.screen_data_path/'drawings'/'cards'/f'{BOARD_DIV["hand"][i]}.txt', 
            BOARD_DIV['royal_card_zone_anchor'][0] + BOARD_DIV['drew_card_anchors'][i][0], 
            BOARD_DIV['royal_card_zone_anchor'][1] + BOARD_DIV['drew_card_anchors'][i][1] + (-1 if i == BOARD_DIV['selected_card_index'] else 0), 
            color_pair_obj=resources.get_color_pair_obj((1+SUITS.index(suit(BOARD_DIV['hand'][i])))))
    render_div(BOARD_DIV) # FUCK IT


def suit(card:str) -> str: return card[-1]
def rank(card:str) -> str: return card[:-1]
def point(rank:str) -> int: return POINT_LOOKUP_TABLE[rank]

def update_board():
    if key_state_tracker.get_key_state('a', key_state_tracker.JUST_PRESSED): draw_hand()
    if key_state_tracker.get_key_state('space', key_state_tracker.JUST_PRESSED): 
        # Logging before play_card
        logging.info(f'Attempting to play card. BOARD_DIV before: {repr(BOARD_DIV)}')
        exit_code = play_card()
        # Logging after play_card
        logging.info(f'Attempted play_card. BOARD_DIV after: {repr(BOARD_DIV)}, exit_code: {exit_code}')
    new_index = -2
    if key_state_tracker.get_key_state('1'):  new_index = 0
    elif key_state_tracker.get_key_state('2'): new_index = 1
    elif key_state_tracker.get_key_state('3'): new_index = 2
    if (new_index != -2):
        new_index = clamp(new_index, 0, len(BOARD_DIV['hand']) - 1)
        if (new_index != BOARD_DIV['selected_card_index']): 
            BOARD_DIV['selected_card_index'] = new_index
            render_draw_pile()

    new_index = -2
    if key_state_tracker.get_key_state('z'): new_index = 0
    elif key_state_tracker.get_key_state('x'): new_index = 1
    elif key_state_tracker.get_key_state('c'): new_index = 2
    elif key_state_tracker.get_key_state('v'): new_index = 3
    if (new_index != -2):
        new_index = clamp(new_index, 0, 3)
        if (new_index != BOARD_DIV['selected_pile_index']): 
            BOARD_DIV['selected_pile_index'] = new_index
            render_royal_piles()
        
def lose():
    return
def clamp(val:int, lower_bound:int, upper_bound:int) -> int: return max(min(val, upper_bound), lower_bound)


POINT_LOOKUP_TABLE = {
    'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 
    '10': 10, 'J': 11, 'Q': 12, 'K': 13
}