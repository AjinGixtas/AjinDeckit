from components import resources, image_drawer, scene_manager, key_state_tracker
from components.key_state_tracker import get_key_state, get_axis
from curses import newpad, color_pair
from random import randint
KEY_MAP_DISPLAY_TABLE = [0,0,0,0,0,0,1,1,1]
origin_x, origin_y, rows, columns = 0, 0, 0, 0
BOARD_DIV   = { 'index':0, 'src':'blackjack_board.txt', 'deck':[], 'player_hands_data':[{'ace':0, 'point':0, 'cards':[], 'doubled_down':False, 'surrendered':False }], 'player_focused_hand_index':0, 'dealer_hand_data':{'ace':0, 'point':0, 'cards':[], 'is_face_up':[]}, 'y_pos':(6,18), 'game_result_stat':[0,0,0],  'round_state':0, 'player_hand_ratio_coord': {'x':(48,62,76), 'y':(29,30,31)}}
DECK_DIV    = { 'index':1, 'src':'blackjack_deck.txt', 'card_counts':{}, 'x_pos':(2,6,10,14,18,22,26,30,34,38,42,46,52), 'y_pos':(0,8,16,24) }
SETTING_DIV = { 'index':2, 'src':'blackjack_setting.txt', 'cursor_option_values':[0,0,0,1], 'cursor_option_ranges':((0,1),(0,1),(0,1),(1,9)), 'cursor_display_values':(('-HIT-','STAND'),('← _ →','← * →'),('← _ →','← * →'),2),'cursor_index':0}
curent_focus_zone_index = BOARD_DIV['index']
SUIT_SYMBOL, SUITS, RANKS, POINTS = ('♣', '♠', '♦', '♥'), ('C','S','D','H'), ('2','3','4','5','6','7','8','9','10','J','Q','K','A'), ( 2,  3 , 4 , 5 , 6 , 7 , 8 , 9 , 10 , 10, 10, 10, 11)
def _start():
    global origin_x, origin_y, rows, columns
    origin_x, origin_y, rows, columns = scene_manager.get_drawable_screen_data()
    new_game()
def _update(): 
    global curent_focus_zone_index
    if key_state_tracker.get_key_state('delete', key_state_tracker.JUST_PRESSED) and curent_focus_zone_index != SETTING_DIV['index']: 
        render_div(SETTING_DIV)
        return
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
    global BOARD_DIV
    render_div(BOARD_DIV)
    if BOARD_DIV['round_state'] == 0:
        if key_state_tracker.get_key_state('a', key_state_tracker.JUST_PRESSED): render_div(DECK_DIV)
        elif key_state_tracker.get_key_state('e', key_state_tracker.JUST_PRESSED): player_draw_card()
        return
    if BOARD_DIV['round_state'] == 1:
        if key_state_tracker.get_key_state('a', key_state_tracker.JUST_PRESSED): render_div(DECK_DIV)
        elif key_state_tracker.get_key_state('e', key_state_tracker.JUST_PRESSED): player_draw_card()
        elif key_state_tracker.get_key_state('d', key_state_tracker.JUST_PRESSED): double_down()
        elif key_state_tracker.get_key_state('f', key_state_tracker.JUST_PRESSED): split()
        elif key_state_tracker.get_key_state('r', key_state_tracker.JUST_PRESSED): surrender()
        elif key_state_tracker.get_key_state('enter', key_state_tracker.JUST_PRESSED): finish_turn()
        move_vector = key_state_tracker.get_axis('w', 's')
        if move_vector != 0:
            BOARD_DIV['player_focused_hand_index'] = resources.clip_range(BOARD_DIV['player_focused_hand_index'] + move_vector, 0, len(BOARD_DIV['player_hands_data']) - 1)
            rerender_player_hand()
        return
    if BOARD_DIV['round_state'] == 2:
        if key_state_tracker.get_key_state('a', key_state_tracker.JUST_PRESSED): render_div(DECK_DIV)
        elif key_state_tracker.get_key_state('enter', key_state_tracker.JUST_PRESSED): dealer_draw_card(True)
        return
    if BOARD_DIV['round_state'] == 3:
        if key_state_tracker.get_key_state('a', key_state_tracker.JUST_PRESSED): render_div(DECK_DIV)
        elif key_state_tracker.get_key_state('enter', key_state_tracker.JUST_PRESSED): new_round()
def update_deck():
    if key_state_tracker.get_key_state('a', key_state_tracker.JUST_PRESSED): render_div(BOARD_DIV)
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
        SETTING_DIV['pad'].addstr(9 + SETTING_DIV['cursor_index'], 10, '(')
        SETTING_DIV['pad'].addstr(9 + SETTING_DIV['cursor_index'], 16, ')')
        SETTING_DIV['cursor_index'] = resources.clip_range(SETTING_DIV['cursor_index'] + move_vector[0], 0, 2)
        SETTING_DIV['pad'].addstr(9 + SETTING_DIV['cursor_index'], 10, '>')
        SETTING_DIV['pad'].addstr(9 + SETTING_DIV['cursor_index'], 16, '<')
    if move_vector[1] != 0:
        cursor_option_values[SETTING_DIV['cursor_index']] = resources.clip_range(SETTING_DIV['cursor_option_values'][SETTING_DIV['cursor_index']] + move_vector[1], SETTING_DIV['cursor_option_ranges'][SETTING_DIV['cursor_index']][0], SETTING_DIV['cursor_option_ranges'][SETTING_DIV['cursor_index']][1])
        if type(SETTING_DIV['cursor_display_values'][SETTING_DIV['cursor_index']]) == int:
            SETTING_DIV['pad'].addstr(9 + SETTING_DIV['cursor_index'], 11 + SETTING_DIV['cursor_display_values'][SETTING_DIV['cursor_index']], str(SETTING_DIV['cursor_option_values'][SETTING_DIV['cursor_index']]))
        else:
            SETTING_DIV['pad'].addstr(9 + SETTING_DIV['cursor_index'], 11, SETTING_DIV['cursor_display_values'][SETTING_DIV['cursor_index']][cursor_option_values[SETTING_DIV['cursor_index']]])
    render_div(SETTING_DIV)

def new_game():
    global curent_focus_zone_index, DECK, PLAYER_HAND, DEALER_HAND, BOARD_DIV, DECK_DIV, SETTING_DIV
    BOARD_DIV, DECK_DIV, SETTING_DIV = build_div(BOARD_DIV), build_div(DECK_DIV), build_div(SETTING_DIV)
    BOARD_DIV['game_result_stat'] = [0,0,0]
    image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path / 'drawings' / '___card.txt', 101, 11, color_pair_obj=resources.get_color_pair_obj(3))
    for y in range(len(SUITS)):
        for x in range(len(RANKS)):
            image_drawer.draw_colored_image(DECK_DIV['pad'], resources.screen_data_path/'drawings'/'___card.txt', 4*x, 1+8*y, color_pair_obj=resources.get_color_pair_obj(2 if SUITS[y] in ('H', 'D') else 1))
            DECK_DIV['pad'].addstr(2+8*y, 1+4*x, RANKS[x], resources.get_color_pair_obj(2 if SUITS[y] in ('H', 'D') else 1))
            DECK_DIV['pad'].addstr(3+8*y, 1+4*x, SUIT_SYMBOL[y], resources.get_color_pair_obj(2 if SUITS[y] in ('H', 'D') else 1))
    BOARD_DIV['pad'].refresh(0, 0, BOARD_DIV['origin'][0], BOARD_DIV['origin'][1], BOARD_DIV['end'][0], BOARD_DIV['end'][1])
    new_round()
def new_round():
    global curent_focus_zone_index, BOARD_DIV, DECK_DIV
    BOARD_DIV['deck'] = [f'{rank}{suit}' for suit in SUITS for rank in RANKS for _ in range(SETTING_DIV['cursor_option_values'][3])]
    BOARD_DIV['player_hands_data'] = [{'ace':0, 'point':0, 'cards':[], 'doubled_down': False, 'surrendered':False}]
    BOARD_DIV['dealer_hand_data'] =   {'ace':0, 'point':0, 'cards':[], 'is_face_up':[]}
    BOARD_DIV['player_focused_hand_index'] = 0
    BOARD_DIV['round_state'] = 0
    curent_focus_zone_index = BOARD_DIV['index']
    for i in range(7): BOARD_DIV['pad'].addstr(6 + i, 2, '                                                                                         ')
    for i in range(7): BOARD_DIV['pad'].addstr(18 + i, 2, '                                                                                         ')
    BOARD_DIV['pad'].addstr(27, 1, '                                                                                         ')
    DECK_DIV['card_counts'] = {f'{rank}{suit}': SETTING_DIV['cursor_option_values'][3] for suit in SUITS for rank in RANKS}
    [DECK_DIV['pad'].addstr(y, x, str(SETTING_DIV['cursor_option_values'][3])) for x in DECK_DIV['x_pos'] for y in DECK_DIV['y_pos']]
    BOARD_DIV['pad'].addstr(10, 106, str(52 * SETTING_DIV['cursor_option_values'][3]).rjust(3, '0'))
    BOARD_DIV['pad'].addstr(10, 102, str(len(BOARD_DIV['deck'])).rjust(3, '0'))
    BOARD_DIV['pad'].addstr(28, 1, '╔───────────────────╗ ╔───────────────────╗ ╔─────────────╗ ╔─────────────────╗ ╔───────────────────────────────────╗')
    BOARD_DIV['pad'].addstr(29, 1, '│ [E] - START ROUND │ │ [D] - DOUBLE DOWN │ │ [F] - SPLIT │ │ [R] - SURRENDER │ │ [ENTER] - STOP AND PASS TO DEALER │')
    BOARD_DIV['pad'].addstr(30, 1, '╚───────────────────╝ ╚───────────────────╝ ╚─────────────╝ ╚─────────────────╝ ╚───────────────────────────────────╝')
    BOARD_DIV['pad'].addstr(17, 2, '[----------------│----]                         ')
    BOARD_DIV['pad'].addstr(3, 93, '                       ')
    BOARD_DIV['pad'].refresh(0, 0, BOARD_DIV['origin'][0], BOARD_DIV['origin'][1], BOARD_DIV['end'][0], BOARD_DIV['end'][1])
    
    BOARD_DIV['game_result_stat'] = [BOARD_DIV['game_result_stat'][0] + result[0], BOARD_DIV['game_result_stat'][1] + result[1], BOARD_DIV['game_result_stat'][2] + result[2]]
    BOARD_DIV['pad'].addstr(4, 100, f'{BOARD_DIV['game_result_stat'][0]}W'.rjust(4, '0'), resources.get_color_pair_obj(3))
    BOARD_DIV['pad'].addstr(4, 105, f'{BOARD_DIV['game_result_stat'][1]}D'.rjust(4, '0'), resources.get_color_pair_obj(4))
    BOARD_DIV['pad'].addstr(4, 110, f'{float(BOARD_DIV['game_result_stat'][2])}L'.rjust(6, '0'), resources.get_color_pair_obj(2))
def build_div(div):
    with open(resources.screen_data_path / div['src'], 'r', encoding='utf-8') as f:
        div['size'] = tuple(map(int, f.readline().split()))
        div['pad'] = newpad(div['size'][0], div['size'][1])
        for i in range(div['size'][0]):
            div['pad'].insstr(i, 0, f.readline().rstrip())
    if div.get('cursor_index', None) != None:
        SETTING_DIV['pad'].addstr(9 + SETTING_DIV['cursor_index'], 10, '>')
        SETTING_DIV['pad'].addstr(9 + SETTING_DIV['cursor_index'], 16, '<')
        for i in range(len(div['cursor_option_values'])):
            if type(SETTING_DIV['cursor_display_values'][i]) == int: div['pad'].addstr(9+i, 11+SETTING_DIV['cursor_display_values'][i], str(SETTING_DIV['cursor_option_values'][i]))
            else: div['pad'].addstr(9+i, 11, SETTING_DIV['cursor_display_values'][i][SETTING_DIV['cursor_option_values'][i]])
    div['origin'] = ((rows - div['size'][0])//2+1 , (columns - div['size'][1]) // 2+1)
    div['end'] = (div['origin'][0] + div['size'][0], div['origin'][1] + div['size'][1])
    return div
def render_div(div): 
    global curent_focus_zone_index, BOARD_DIV, DECK_DIV, SETTING_DIV, cursor_option_values
    curent_focus_zone_index = div['index']
    cursor_option_values = SETTING_DIV.get('cursor_option_values', None)
    div['pad'].refresh(0, 0, div['origin'][0], div['origin'][1], div['end'][0], div['end'][1])

def draw_random_card(is_face_up=True):
    global BOARD_DIV
    BOARD_DIV['pad'].addstr(10, 102, str(len(BOARD_DIV['deck']) - 1).rjust(3, '0'))
    card = BOARD_DIV['deck'].pop(randint(0, len(BOARD_DIV['deck']) - 1))
    if is_face_up:
        DECK_DIV['card_counts'][card] -= 1
        DECK_DIV['pad'].addstr(DECK_DIV['y_pos'][resources.get_first_dupe_index(SUITS, card[-1])], DECK_DIV['x_pos'][resources.get_first_dupe_index(RANKS, card[:-1])], str(DECK_DIV['card_counts'][card]))
    return card
def player_draw_card():
    global BOARD_DIV
    if BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['point'] == 21:
        BOARD_DIV['pad'].addstr(27, 1, 'You already got the best possible hand, we are not letting you ruin it!                                                ')
        return
    if BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['doubled_down']:
        BOARD_DIV['pad'].addstr(27, 1, 'You have doubled down! No take back allowed!                                                                           ')
        return
    if BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['doubled_down']:
        BOARD_DIV['pad'].addstr(27, 1, 'You have surrendered this hand! Maybe don\'t give up so soon next time?                                                ')
        return


    if BOARD_DIV['round_state'] == 0: 
        BOARD_DIV['round_state'] = 1
        dealer_draw_card(False)
        dealer_draw_card(True)
        player_draw_card()
        BOARD_DIV['pad'].addstr(5, 26, f'{POINTS[resources.get_first_dupe_index(RANKS, BOARD_DIV['dealer_hand_data']['cards'][1][:-1])]}+??')
        BOARD_DIV['pad'].addstr(29,9,'DRAW A CARD')
    card = draw_random_card()
    if card[0] == 'A': BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['ace'] += 1
    BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['point'] += POINTS[resources.get_first_dupe_index(RANKS, card[:-1])]
    BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards'].append(card)
    if BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['point'] > 21 and BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['ace'] > 0:
        BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['point'] -= 10
        BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['ace'] -= 1
    rerender_player_hand()
def dealer_draw_card(is_face_up):    
    global BOARD_DIV
    if BOARD_DIV['dealer_hand_data']['point'] > 17 or (BOARD_DIV['dealer_hand_data']['point'] == 17 and SETTING_DIV['cursor_option_values'][0] == 1): 
        game_end()
        return
    card = draw_random_card(is_face_up)
    if card[0] == 'A': BOARD_DIV['dealer_hand_data']['ace'] += 1
    BOARD_DIV['dealer_hand_data']['point'] += POINTS[resources.get_first_dupe_index(RANKS, card[:-1])]
    BOARD_DIV['dealer_hand_data']['cards'].append(card)
    BOARD_DIV['dealer_hand_data']['is_face_up'].append(is_face_up)
    if BOARD_DIV['dealer_hand_data']['ace'] > 0:
        if BOARD_DIV['dealer_hand_data']['point'] > 21:
            BOARD_DIV['dealer_hand_data']['point'] -= 10
            BOARD_DIV['dealer_hand_data']['ace'] -= 1
    if SETTING_DIV['cursor_option_values'][1] == 1 and BOARD_DIV['dealer_hand_data']['point'] == 21:
        # Blackjack peaked
        pass
    rerender_dealer_hand()
    if BOARD_DIV['dealer_hand_data']['point'] > 21:
        BOARD_DIV['pad'].addstr(27, 1, 'Dealer busted! All standing hands won.')
        game_end()

def double_down():
    global BOARD_DIV
    player_draw_card()
    BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['doubled_down'] = True
    rerender_player_hand()
def split():
    global BOARD_DIV
    if not (len(BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards']) == 2 and BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards'][0][0] == BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards'][1][0]): 
        BOARD_DIV['pad'].addstr(28, 30, 'Your hand must have exactly 2 card of the same rank!')
        return
    card = BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards'].pop()
    BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['point'] = 11 if card[0] == 'A' else int(BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['point'] / 2)
    BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['ace'] = int(BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['ace'] / 2)
    BOARD_DIV['player_hands_data'].append({'ace': (1 if card[0]=='A' else 0), 'point':POINTS[resources.get_first_dupe_index(RANKS, card[:-1])], 'cards':[card], 'doubled_down':False, 'surrendered':False})
    BOARD_DIV['pad'].addstr(16, 88, str(len(BOARD_DIV['player_hands_data'])).rjust(2, '0'))
    BOARD_DIV['pad'].addstr(25, 77, '[▼] Hand below')
    rerender_player_hand()
def finish_turn():
    BOARD_DIV['dealer_hand_data']['is_face_up'][0] = True
    BOARD_DIV['round_state'] = 2
    rerender_dealer_hand()
    if SETTING_DIV['cursor_option_values'][2] == 0:
        BOARD_DIV['pad'].addstr(28, 1, '╔────────────────────────────────╗                                                                                   ')
        BOARD_DIV['pad'].addstr(29, 1, '│ [ENTER] -  DEALER DRAW A CARD  │                                                                                   ')
        BOARD_DIV['pad'].insstr(30, 1, '╚────────────────────────────────╝                                                                                   ')
        return
    while BOARD_DIV['dealer_hand_data']['point'] < 17: 
        dealer_draw_card(True)
    dealer_draw_card(True)
    dealer_draw_card(True)
def surrender():
    global BOARD_DIV
    BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['surrendered'] = True

def rerender_player_hand():
    global BOARD_DIV
    blank = ' ' * 89
    BOARD_DIV['pad'].addstr(16, 85, str(BOARD_DIV['player_focused_hand_index']+1).rjust(2, '0'))
    BOARD_DIV['pad'].addstr(25, 77, '              ' if BOARD_DIV['player_focused_hand_index'] == len(BOARD_DIV['player_hands_data']) - 1 else '[▼] Hand below')
    BOARD_DIV['pad'].addstr(17, 77, '              ' if BOARD_DIV['player_focused_hand_index'] == 0 else '[▲] Hand above')
    for i in range(7): BOARD_DIV['pad'].addstr(BOARD_DIV['y_pos'][1] + i, 2, blank)
    for i in range(len(BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards'])):
        image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path / 'drawings' / f'{BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards'][i]}.txt', int(2 + 80.00 / (len(BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards'])*2) * (i*2+1)), BOARD_DIV['y_pos'][1], color_pair_obj=resources.get_color_pair_obj(2 if BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards'][i][1] in ('H', 'D') else 1))
    
    ace_remain = BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['ace']
    bar = ''
    for card in BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards']:
        if card[0] != 'A': 
            string = SUIT_SYMBOL[resources.get_first_dupe_index(SUITS, card[-1])] * POINTS[resources.get_first_dupe_index(RANKS, card[:-1])]
        else:
            string = SUIT_SYMBOL[resources.get_first_dupe_index(SUITS, card[-1])] * (11 if ace_remain > 0 else 1)
            ace_remain -= 1
        BOARD_DIV['pad'].addstr(17, 3 + len(bar), string, resources.get_color_pair_obj(2 if card[1] in ('H', 'D') else 1))
        bar += string
    if BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['doubled_down']:  BOARD_DIV['pad'].addstr(17, 3, bar, 0)
    if len(bar) <= 21: BOARD_DIV['pad'].addstr(17, 3 + len(bar), '-' * (21 - len(bar)))
def rerender_dealer_hand():
    global BOARD_DIV
    blank = ' ' * 89
    for i in range(7): BOARD_DIV['pad'].addstr(BOARD_DIV['y_pos'][0] + i, 2, blank)
    for i in range(len(BOARD_DIV['dealer_hand_data']['cards'])):
        if BOARD_DIV['dealer_hand_data']['is_face_up'][i] == True: 
            image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path / 'drawings' / f'{BOARD_DIV['dealer_hand_data']['cards'][i]}.txt', int(2 + 80.00 / (len(BOARD_DIV['dealer_hand_data']['cards'])*2) * (i*2+1)), BOARD_DIV['y_pos'][0], color_pair_obj=resources.get_color_pair_obj(2 if BOARD_DIV['dealer_hand_data']['cards'][i][1] in ('H', 'D') else 1))
        else: image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path / 'drawings' / '___card.txt', int(2 + 80.00 / (len(BOARD_DIV['dealer_hand_data']['cards'])*2) * (i*2+1)), BOARD_DIV['y_pos'][0], color_pair_obj=resources.get_color_pair_obj(3))
result = [0,0,0]
def game_end():
    global BOARD_DIV, result
    BOARD_DIV['round_state'] = 3
    
    BOARD_DIV['pad'].addstr(28, 1, '╔────────────────────────────────╗  DEALER:                                                                          ')
    BOARD_DIV['pad'].addstr(29, 1, '│ [ENTER] -      NEXT ROUND      │  PLAYER:                                                                          ')
    BOARD_DIV['pad'].insstr(30, 1, '╚────────────────────────────────╝                                                                                   ')
    
    i = 0
    result = [0, 0, 0]
    for y in BOARD_DIV['player_hand_ratio_coord']['y']:
        for x in BOARD_DIV['player_hand_ratio_coord']['x']:
            string = f'[{i+1}] {BOARD_DIV['player_hands_data'][i]['point']} in {len(BOARD_DIV['player_hands_data'][i]['cards'])}'
            if BOARD_DIV['player_hands_data'][i]['surrendered']:
                BOARD_DIV['pad'].addstr(y, x + 8 - len(string), string, resources.get_color_pair_obj(2))
                i += 1
                result[2] += .5
                if i == len(BOARD_DIV['player_hands_data']): break
                continue
            BOARD_DIV['pad'].addstr(y, x + 8 - len(string), string, resources.get_color_pair_obj(3 if (BOARD_DIV['dealer_hand_data']['point'] < BOARD_DIV['player_hands_data'][i]['point'] and BOARD_DIV['player_hands_data'][i]['point'] <= 21) or (BOARD_DIV['player_hands_data'][i]['point'] <= 21 and BOARD_DIV['dealer_hand_data']['point'] > 21) else 4 if (BOARD_DIV['dealer_hand_data']['point'] == BOARD_DIV['player_hands_data'][i]['point'] and BOARD_DIV['player_hands_data'][i]['point'] <= 21) else 2))
            
            if (BOARD_DIV['dealer_hand_data']['point'] < BOARD_DIV['player_hands_data'][i]['point'] and BOARD_DIV['player_hands_data'][i]['point'] <= 21) or (BOARD_DIV['player_hands_data'][i]['point'] <= 21 and BOARD_DIV['dealer_hand_data']['point'] > 21): 
                result[0] += 2 if BOARD_DIV['player_hands_data'][i]['doubled_down'] else 1 # Win
            elif (BOARD_DIV['dealer_hand_data']['point'] == BOARD_DIV['player_hands_data'][i]['point'] and BOARD_DIV['player_hands_data'][i]['point'] <= 21): 
                result[1] += 1
            else: result[2] += 2 if BOARD_DIV['player_hands_data'][i]['doubled_down'] else 1 # Lost
            i += 1
            if i == len(BOARD_DIV['player_hands_data']): break
        if i == len(BOARD_DIV['player_hands_data']): break
    string = f'{BOARD_DIV['dealer_hand_data']['point']} in {len(BOARD_DIV['dealer_hand_data']['cards'])}'
    BOARD_DIV['pad'].addstr(28, 48 + 8 - len(string), string, resources.get_color_pair_obj(2 if result[0] == len(BOARD_DIV['player_hands_data']) else 3 if result[2] == len(BOARD_DIV['player_hands_data']) else 4))
    string = f'+{result[0]}'
    BOARD_DIV['pad'].addstr(3, 103 - len(string), string, resources.get_color_pair_obj(3))
    string = f'+{result[1]}'
    BOARD_DIV['pad'].addstr(3, 108 - len(string), string, resources.get_color_pair_obj(4))
    string = f'+{float(result[2])}'
    BOARD_DIV['pad'].addstr(3, 115 - len(string), string, resources.get_color_pair_obj(2))
