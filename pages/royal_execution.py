from components import resources, image_drawer, scene_manager, key_state_tracker
from components.key_state_tracker import get_key_state, get_axis
from curses import newpad, color_pair
from random import randint, shuffle
KEY_MAP_DISPLAY_TABLE=['royal_execution']
BOARD_DIV = {
    'index': 0, 'src': 'boards/royal_execution_board.txt', 'pad': None,
    'draw_pile': [], 'discard_pile': [], 'royal_piles': [ [], [], [], [] ], 'executor_piles': [ [], [], [], [] ], 'hand': []
}
SETTING_DIV = {
}
SUIT_SYMBOL, SUITS, RANKS, POINTS = ('♣','♠','♦','♥',), ('C', 'S', 'D', 'H'), ('A','2','3','4','5','6','7','8','9','10','J','Q','K'), (1,2,3,4,5,6,7,8,9,10,11,12,13)
def _start():
    global origin_x, origin_y, rows, columns, BOARD_DIV
    origin_x, origin_y, rows, columns = scene_manager.get_drawable_screen_data()
    BOARD_DIV = build_div(BOARD_DIV)
    setup_var()
    new_game()
    render_div(BOARD_DIV)
def setup_var():
    BOARD_DIV['royal_card_zone_anchor'] = (5,0)
    BOARD_DIV['royal_card_anchors'] = (((3,2),(3,4),(3,6)),((14,2),(14,4),(14,6)),((25,2),(25,4),(25,6)),((36,2),(36,4),(36,6)))
    BOARD_DIV['royal_pile_zone'] = ((3,2), (44,12))
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
def _update():
    return
def draw_hand():
    global BOARD_DIV
    # Discard all remaining card in hand
    BOARD_DIV['discard_pile'] += BOARD_DIV['hand']
    BOARD_DIV['hand'] = []

def render_royal_piles():
    global BOARD_DIV
    for x in range(4):
        for y in range(len(BOARD_DIV['royal_piles'][x])):
            if y != len(BOARD_DIV['royal_piles'][x])-1: image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path/'drawings'/'cards'/'___card.txt', BOARD_DIV['royal_card_zone_anchor'][0] + BOARD_DIV['royal_card_anchors'][x][y][0], BOARD_DIV['royal_card_zone_anchor'][1] + BOARD_DIV['royal_card_anchors'][x][y][1], color_pair_obj=resources.get_color_pair_obj(5))
            else: image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path/'drawings'/'cards'/f'{BOARD_DIV['royal_piles'][x][y]}.txt', BOARD_DIV['royal_card_zone_anchor'][0] + BOARD_DIV['royal_card_anchors'][x][y][0], BOARD_DIV['royal_card_zone_anchor'][1] + BOARD_DIV['royal_card_anchors'][x][y][1], color_pair_obj=resources.get_color_pair_obj((1+SUITS.index(suit(BOARD_DIV['royal_piles'][x][y])))))
    #print(               f"{BOARD_DIV['royal_pile_zone'][0][1]} {BOARD_DIV['royal_pile_zone'][0][0]} {BOARD_DIV['origin'][1] + BOARD_DIV['royal_pile_zone'][0][1]} {BOARD_DIV['origin'][0] + BOARD_DIV['royal_pile_zone'][0][0]} {BOARD_DIV['origin'][1] + BOARD_DIV['royal_pile_zone'][1][1]} {BOARD_DIV['origin'][0] + BOARD_DIV['royal_pile_zone'][1][0]}")
    BOARD_DIV['pad'].refresh(BOARD_DIV['royal_pile_zone'][0][1],  BOARD_DIV['royal_pile_zone'][0][0],  BOARD_DIV['origin'][1] + BOARD_DIV['royal_pile_zone'][0][1],  BOARD_DIV['origin'][0] + BOARD_DIV['royal_pile_zone'][0][0],  BOARD_DIV['origin'][1] + BOARD_DIV['royal_pile_zone'][1][1],  BOARD_DIV['origin'][0] + BOARD_DIV['royal_pile_zone'][1][0])
def _end():
    return
def suit(card): return card[-1]
def rank(card): return card[:-1]