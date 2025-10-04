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
    'draw_pile': [], 'discard_pile': [], 'royal_piles': [ [], [], [], [] ], 'executor_piles': [ [], [], [], [] ], 
    'hand': [],
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
    if key_state_tracker.get_key_state('backspace', key_state_tracker.JUST_PRESSED): new_game()
    update_board()
# Exit function
def _end():
    return

def setup_var():
    BOARD_DIV['royal_card_zone_anchor'] = (3,1)
    BOARD_DIV['royal_card_anchors'] = (((0,1),(0,2),(0,3)),((12,1),(12,2),(12,3)),((24,1),(24,2),(24,3)),((36,1),(36,2),(36,3)))
    BOARD_DIV['royal_pile_zone'] = ((0,0), (44,12))
    BOARD_DIV['drew_card_anchors'] = ((56, 4), (59, 4), (62, 4))
    BOARD_DIV['royal_pile_cursor_anchor_points'] = ((9, 14), (21, 14), (33, 14), (45, 14))
    BOARD_DIV['discard_pile_render_anchor'] = (-1,17)

    render_div(BOARD_DIV)
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
    BOARD_DIV['executor_piles'] = [ [], [], [], [] ]
    BOARD_DIV['selected_card_index'] = 0
    BOARD_DIV['selected_pile_index'] = 0
    BOARD_DIV['discard_pile'] = []
    BOARD_DIV['draw_pile'] = []
    BOARD_DIV['hand'] = []
    BOARD_DIV['joker_remain'] = 2
    
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
    BOARD_DIV['pad'].addstr(
        BOARD_DIV['royal_card_zone_anchor'][1] + 23,
        BOARD_DIV['royal_card_zone_anchor'][0] + 51, 
        f'JOKER REMAIN: {BOARD_DIV["joker_remain"]}/2')
    render_royal_piles()
    render_draw_pile()
    render_discard_pile()
    render_div(BOARD_DIV)

def draw_hand():
    global BOARD_DIV
    if BOARD_DIV['draw_pile'] == []: new_game(); return
    # Discard all remaining card in hand
    BOARD_DIV['hand'] = [card for card in BOARD_DIV['hand'] if card != 'INVALID_CARD']
    BOARD_DIV['discard_pile'] += BOARD_DIV['hand']
    render_discard_pile()
    BOARD_DIV['hand'] = []
    
    for i in range(3):
        if not draw_card():
            lose()
            break
    render_draw_pile()
    render_div(BOARD_DIV)
    
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
    if len(BOARD_DIV['hand']) > BOARD_DIV['selected_card_index'] and BOARD_DIV['hand'][BOARD_DIV['selected_card_index']] == 'INVALID_CARD':
        return 9 # Invalid card selected
    if len(BOARD_DIV['hand']) == 0:
        return 2 # No card in hand
    if len(BOARD_DIV['royal_piles'][BOARD_DIV['selected_pile_index']]) == 0: 
        return 8 # No royal card in the pile
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

    
    BOARD_DIV['executor_piles'][BOARD_DIV['selected_pile_index']].append(BOARD_DIV['hand'][BOARD_DIV['selected_card_index']])
    BOARD_DIV['hand'][BOARD_DIV['selected_card_index']] = 'INVALID_CARD'
    BOARD_DIV['selected_card_index'] = -1 if len(BOARD_DIV['hand']) == 0 else clamp(BOARD_DIV['selected_card_index'], 0, len(BOARD_DIV['hand']) - 1)
    if executor_index == 2: # If the executor pile is full, remove the royal card
        BOARD_DIV['royal_piles'][BOARD_DIV['selected_pile_index']].pop()
        BOARD_DIV['executor_piles'][BOARD_DIV['selected_pile_index']].clear()
    render_royal_piles()
    render_draw_pile()
    render_div(BOARD_DIV)
    return 0
def play_joker():
    if BOARD_DIV['joker_remain'] <= 0: return
    BOARD_DIV['joker_remain'] -= 1
    executor_index = len(BOARD_DIV['executor_piles'][BOARD_DIV['selected_pile_index']])
    BOARD_DIV['executor_piles'][BOARD_DIV['selected_pile_index']].append('!!')
    if executor_index == 2: # If the executor pile is full, remove the royal card
        BOARD_DIV['royal_piles'][BOARD_DIV['selected_pile_index']].pop()
        BOARD_DIV['executor_piles'][BOARD_DIV['selected_pile_index']].clear()
    BOARD_DIV['pad'].addstr(
        BOARD_DIV['royal_card_zone_anchor'][1] + 23,
        BOARD_DIV['royal_card_zone_anchor'][0] + 51, 
        f'JOKER REMAIN: {BOARD_DIV["joker_remain"]}/2')
    render_royal_piles()
    render_draw_pile()
    render_div(BOARD_DIV)
def render_royal_piles():
    global BOARD_DIV
    keybind_char = ['*', '*', '*', '*']
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
                color_pair_obj=resources.get_color_pair_obj(
                    (
                        (1 + SUITS.index(suit(BOARD_DIV['executor_piles'][x][y])) if suit(BOARD_DIV['executor_piles'][x][y]) != '!' else 6))))
RANK = ('A','2','3','4','5','6','7','8','9','10','J','Q','K')
SUIT = ('C', 'S', 'D', 'H')
def render_draw_pile():
    BOARD_DIV['pad'].addstr(BOARD_DIV['royal_card_zone_anchor'][1] + 3, BOARD_DIV['royal_card_zone_anchor'][0] + 53, '×' + f'{len(BOARD_DIV["draw_pile"])}'.rjust(2, '0'))

    for i in range(-1, 7, 1):
        BOARD_DIV['pad'].addstr(
            BOARD_DIV['royal_card_zone_anchor'][1] + BOARD_DIV['drew_card_anchors'][0][1] + i, 
            BOARD_DIV['royal_card_zone_anchor'][0] + BOARD_DIV['drew_card_anchors'][0][0], ' ' * 16)
    image_drawer.draw_colored_image(
                    BOARD_DIV['pad'], 
                    resources.screen_data_path/'drawings'/'cards'/'___card.txt', 
                    BOARD_DIV['royal_card_zone_anchor'][0]+52, BOARD_DIV['royal_card_zone_anchor'][1] + 4, color_pair_obj=resources.get_color_pair_obj(5))
    for i in range(len(BOARD_DIV['hand'])):
        if BOARD_DIV['hand'][i] == 'INVALID_CARD':
            continue
        image_drawer.draw_colored_image(
            BOARD_DIV['pad'], 
            resources.screen_data_path/'drawings'/'cards'/f'{BOARD_DIV["hand"][i]}.txt', 
            BOARD_DIV['royal_card_zone_anchor'][0] + BOARD_DIV['drew_card_anchors'][i][0], 
            BOARD_DIV['royal_card_zone_anchor'][1] + BOARD_DIV['drew_card_anchors'][i][1] + (0 if i == BOARD_DIV['selected_card_index'] else 0), 
            color_pair_obj=resources.get_color_pair_obj((1+SUITS.index(suit(BOARD_DIV['hand'][i])))))

    for i in range(4):
        BOARD_DIV['pad'].addstr(
            BOARD_DIV['royal_card_zone_anchor'][1] + 18 + i, 
            BOARD_DIV['royal_card_zone_anchor'][0] + 48, ' ' * 26)
    full_pile = BOARD_DIV['draw_pile'] + [x for sublist in BOARD_DIV['royal_piles'] for x in sublist]
    for i in range(len(full_pile)):
        x_offset = RANK.index(rank(full_pile[i])) * 2
        y_offset = SUIT.index(suit(full_pile[i]))
        BOARD_DIV['pad'].addstr(
            BOARD_DIV['royal_card_zone_anchor'][1] + 18 + y_offset,
            BOARD_DIV['royal_card_zone_anchor'][0] + 48 + x_offset, '•', resources.get_color_pair_obj(y_offset+1))
def render_discard_pile():
    msg = ""
    if len(BOARD_DIV['discard_pile']) < 5:
        msg = f'DISCARDED CARDS ({len(BOARD_DIV["discard_pile"])}/5) ─────────────────────────────────────'
    elif len(BOARD_DIV['discard_pile']) <= 7:
        msg = f'CARD SHORTAGE! NEED JOKERS TO KILL ROYAL CARDS ({len(BOARD_DIV["discard_pile"])}/7) '
    else: 
        msg = f'NOT ENOUGH CARDS TO KILL ALL ROYALS ({len(BOARD_DIV["discard_pile"])}/7) ───────────'
    BOARD_DIV['pad'].addstr(
        BOARD_DIV['royal_card_zone_anchor'][1] + 16,
        BOARD_DIV['royal_card_zone_anchor'][0], msg, 
        resources.get_color_pair_obj(0 if len(BOARD_DIV['discard_pile']) < 5 else 4)
    )
    for i in range(7):
        BOARD_DIV['pad'].addstr(BOARD_DIV['royal_card_zone_anchor'][1] + BOARD_DIV['discard_pile_render_anchor'][1] + i, BOARD_DIV['royal_card_zone_anchor'][0] + BOARD_DIV['discard_pile_render_anchor'][0], ' ' * 45)
    for i in range(min(len(BOARD_DIV['discard_pile']), 7)):
        image_drawer.draw_colored_image(
            BOARD_DIV['pad'], 
            resources.screen_data_path/'drawings'/'cards'/f'{BOARD_DIV["discard_pile"][i]}.txt', 
            BOARD_DIV['royal_card_zone_anchor'][0] + BOARD_DIV['discard_pile_render_anchor'][0] + i * 4, 
            BOARD_DIV['royal_card_zone_anchor'][1] + BOARD_DIV['discard_pile_render_anchor'][1], 
            color_pair_obj=resources.get_color_pair_obj((1+SUITS.index(suit(BOARD_DIV['discard_pile'][i])))))

def suit(card:str) -> str: return card[-1]
def rank(card:str) -> str: return card[:-1]
def point(rank:str) -> int: return POINT_LOOKUP_TABLE[rank]

def update_board():
    if key_state_tracker.get_key_state('w', key_state_tracker.JUST_PRESSED): draw_hand()
    vector = -1
    if key_state_tracker.get_key_state('i', key_state_tracker.JUST_PRESSED): vector = 0
    elif key_state_tracker.get_key_state('o', key_state_tracker.JUST_PRESSED): vector = 1
    elif key_state_tracker.get_key_state('p', key_state_tracker.JUST_PRESSED): vector = 2
    elif key_state_tracker.get_key_state('j', key_state_tracker.JUST_PRESSED): play_joker(); return
    if vector != -1: 
        BOARD_DIV['selected_card_index'] = vector
        play_card(); render_draw_pile(); render_div(BOARD_DIV)
    vector = key_state_tracker.get_axis('a', 'd')
    if vector != 0: 
        BOARD_DIV['selected_pile_index'] = (BOARD_DIV['selected_pile_index'] + vector) % 4
        render_royal_piles(); render_div(BOARD_DIV)
def lose():
    return
def clamp(val:int, lower_bound:int, upper_bound:int) -> int: return max(min(val, upper_bound), lower_bound)


POINT_LOOKUP_TABLE = {
    'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 
    '10': 10, 'J': 11, 'Q': 12, 'K': 13, '!': 10
}