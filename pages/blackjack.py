from components import resources, image_drawer, scene_manager, key_state_tracker
from components.key_state_tracker import get_key_state, get_axis
from curses import newpad, color_pair
from random import randint, shuffle
KEY_MAP_DISPLAY_TABLE = ['blackjack']
# origin_x, origin_y, rows, columns = 0, 0, 0, 0
BOARD_DIV   = { 'index':0, 'src':'blackjack_board.txt', 'deck_progress_index':0, 'deck':[], 
    'player_hands_data':[{'ace':0, 'point':0, 'cards':[], 'doubled_down':False, 'surrendered':False }], 
    'player_focused_hand_index':0, 
    'dealer_hand_data':{'ace':0, 'point':0, 'insurance_bet':False, 'cards':[], 'is_face_up':[]}, 
    'y_pos':(3,14), 'game_result':[0,0,0], 'round_result':[0,0,0],  'round_state':0, 'player_hand_ratio_coord': {'x':(48,62,76), 'y':(24,25,26)}}
DECK_DIV    = { 'index':1, 'src':'blackjack_deck.txt', 'card_counts':{}, 'x_pos':(2,6,10,14,18,22,26,30,34,38,42,46,52), 'y_pos':(0,0,0,0), 'suit_offset':( (0,0), (58,0), (0,8), (58,8) ) }
SETTING_DIV = { 'index':2, 'src':'blackjack_setting.txt', 'cursor_option_values':[0,1,0,1,1,1], 'cursor_option_ranges':((0,1),(0,1),(0,1),(0,1),(0,1),(1,9)), 'cursor_display_values':(('-HIT-','STAND'),('← _ →','← * →'),('← _ →','← * →'),('← _ →','← * →'),('← _ →','← * →'),2),'cursor_index':0}
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
        # Begin the round
        if key_state_tracker.get_key_state('a', key_state_tracker.JUST_PRESSED): render_div(DECK_DIV)
        elif key_state_tracker.get_key_state('e', key_state_tracker.JUST_PRESSED): 
            begin_the_round()
            if not(len(BOARD_DIV['dealer_hand_data']['cards']) == 2 and BOARD_DIV['dealer_hand_data']['cards'][1][0] == 'A' and SETTING_DIV['cursor_option_values'][1]): 
                BOARD_DIV['round_state'] = 2
                BOARD_DIV['pad'].addstr(23, 1, '╔───────────────────╗ ╔───────────────────╗ ╔─────────────╗ ╔─────────────────╗ ╔──────────────────────────╗')
                BOARD_DIV['pad'].addstr(24, 1, '│ [E] - DRAW A CARD │ │ [D] - DOUBLE DOWN │ │ [F] - SPLIT │ │ [R] - SURRENDER │ │ [SPACE] - PASS TO DEALER │')
                BOARD_DIV['pad'].addstr(25, 1, '╚───────────────────╝ ╚───────────────────╝ ╚─────────────╝ ╚─────────────────╝ ╚──────────────────────────╝')
            else:
                BOARD_DIV['round_state'] = 1
                BOARD_DIV['pad'].addstr(23, 0, '                      ╔──────────────────────────╗ ╔──────────────────────────╗                      ')
                BOARD_DIV['pad'].addstr(24, 0, '                      │ [X] - TAKE INSURANCE BET │ │ [C] - PEEK FOR BLACKJACK │                      ')
                BOARD_DIV['pad'].addstr(25, 0, '                      ╚──────────────────────────╝ ╚──────────────────────────╝                      ')
        return
    if BOARD_DIV['round_state'] == 1:
        if key_state_tracker.get_key_state('a', key_state_tracker.JUST_PRESSED): render_div(DECK_DIV)
        insurance_option = key_state_tracker.get_axis('x', 'c')
        if insurance_option != 0:
            if insurance_option == -1: BOARD_DIV['dealer_hand_data']['insurance_bet'] = True
            BOARD_DIV['round_state'] = 2
            resolve_insurance_bet()
        move_vector = key_state_tracker.get_axis('w', 's')
        if move_vector != 0:
            BOARD_DIV['player_focused_hand_index'] = resources.clip_range(BOARD_DIV['player_focused_hand_index'] + move_vector, 0, len(BOARD_DIV['player_hands_data']) - 1)
            rerender_player_hand()
        return
    if BOARD_DIV['round_state'] == 2:
        # Player take their turn
        if key_state_tracker.get_key_state('a', key_state_tracker.JUST_PRESSED): render_div(DECK_DIV)
        elif key_state_tracker.get_key_state('e', key_state_tracker.JUST_PRESSED): player_draw_card()
        elif key_state_tracker.get_key_state('d', key_state_tracker.JUST_PRESSED): double_down()
        elif key_state_tracker.get_key_state('f', key_state_tracker.JUST_PRESSED): split()
        elif key_state_tracker.get_key_state('r', key_state_tracker.JUST_PRESSED): surrender()
        elif key_state_tracker.get_key_state('space', key_state_tracker.JUST_PRESSED): finish_turn()
        move_vector = key_state_tracker.get_axis('w', 's')
        if move_vector != 0:
            BOARD_DIV['player_focused_hand_index'] = resources.clip_range(BOARD_DIV['player_focused_hand_index'] + move_vector, 0, len(BOARD_DIV['player_hands_data']) - 1)
            rerender_player_hand()
        return
    if BOARD_DIV['round_state'] == 3:
        # Dealer take their turn
        if key_state_tracker.get_key_state('a', key_state_tracker.JUST_PRESSED): render_div(DECK_DIV)
        elif key_state_tracker.get_key_state('space', key_state_tracker.JUST_PRESSED): dealer_draw_card(True)
        return
    if BOARD_DIV['round_state'] == 4:
        # Prepare for the next round
        if key_state_tracker.get_key_state('a', key_state_tracker.JUST_PRESSED): render_div(DECK_DIV)
        elif key_state_tracker.get_key_state('space', key_state_tracker.JUST_PRESSED): new_round()
        return
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
        SETTING_DIV['pad'].addstr(6 + SETTING_DIV['cursor_index'], 10, '(')
        SETTING_DIV['pad'].addstr(6 + SETTING_DIV['cursor_index'], 16, ')')
        SETTING_DIV['cursor_index'] = resources.clip_range(SETTING_DIV['cursor_index'] + move_vector[0], 0, 5)
        SETTING_DIV['pad'].addstr(6 + SETTING_DIV['cursor_index'], 10, '>')
        SETTING_DIV['pad'].addstr(6 + SETTING_DIV['cursor_index'], 16, '<')
    if move_vector[1] != 0:
        cursor_option_values[SETTING_DIV['cursor_index']] = resources.clip_range(SETTING_DIV['cursor_option_values'][SETTING_DIV['cursor_index']] + move_vector[1], SETTING_DIV['cursor_option_ranges'][SETTING_DIV['cursor_index']][0], SETTING_DIV['cursor_option_ranges'][SETTING_DIV['cursor_index']][1])
        if type(SETTING_DIV['cursor_display_values'][SETTING_DIV['cursor_index']]) == int:
            SETTING_DIV['pad'].addstr(6 + SETTING_DIV['cursor_index'], 11 + SETTING_DIV['cursor_display_values'][SETTING_DIV['cursor_index']], str(SETTING_DIV['cursor_option_values'][SETTING_DIV['cursor_index']]))
        else:
            SETTING_DIV['pad'].addstr(6 + SETTING_DIV['cursor_index'], 11, SETTING_DIV['cursor_display_values'][SETTING_DIV['cursor_index']][cursor_option_values[SETTING_DIV['cursor_index']]])
    render_div(SETTING_DIV)

def new_game():
    global curent_focus_zone_index, DECK, PLAYER_HAND, DEALER_HAND, BOARD_DIV, DECK_DIV, SETTING_DIV
    BOARD_DIV, DECK_DIV, SETTING_DIV = build_div(BOARD_DIV), build_div(DECK_DIV), build_div(SETTING_DIV)
    image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path / 'drawings' / 'cards' / '___card.txt', 100, 6, color_pair_obj=resources.get_color_pair_obj(5))
    for y in range(len(SUITS)):
        suit_offset = DECK_DIV['suit_offset'][y]
        for x in range(len(RANKS)):
            image_drawer.draw_colored_image(DECK_DIV['pad'], resources.screen_data_path/'drawings'/ 'cards' / ('___card.txt' if x != 12 else (RANKS[x]+SUITS[y]+".txt")), suit_offset[0]+4*x, suit_offset[1]+1, color_pair_obj=resources.get_color_pair_obj(resources.SUITS_INDEX_DICT[SUITS[y]]))
            DECK_DIV['pad'].addstr(suit_offset[1]+2, suit_offset[0]+1+4*x, RANKS[x], resources.get_color_pair_obj(resources.SUITS_INDEX_DICT[SUITS[y]]))
            DECK_DIV['pad'].addstr(suit_offset[1]+3, suit_offset[0]+1+4*x, SUIT_SYMBOL[y], resources.get_color_pair_obj(resources.SUITS_INDEX_DICT[SUITS[y]]))
    BOARD_DIV['pad'].refresh(0, 0, BOARD_DIV['origin'][0], BOARD_DIV['origin'][1], BOARD_DIV['end'][0], BOARD_DIV['end'][1])
    new_round()
    BOARD_DIV['game_result'] = [0.0,0,0.0]
    BOARD_DIV['pad'].addstr(1, 100, f'{float(BOARD_DIV['game_result'][0])}W'.rjust(6, '0'), resources.get_color_pair_obj(5))
    BOARD_DIV['pad'].addstr(1, 107, f'{BOARD_DIV['game_result'][1]}D'.rjust(4, '0'), resources.get_color_pair_obj(3))
    BOARD_DIV['pad'].addstr(1, 112, f'{float(BOARD_DIV['game_result'][2])}L'.rjust(6, '0'), resources.get_color_pair_obj(4))
def new_round():
    global curent_focus_zone_index, BOARD_DIV, DECK_DIV
    BOARD_DIV['deck'] = [f'{rank}{suit}' for suit in SUITS for rank in RANKS for _ in range(SETTING_DIV['cursor_option_values'][5])]
    shuffle(BOARD_DIV['deck'])
    BOARD_DIV['deck_progress_index'] = 0
    BOARD_DIV['player_hands_data'] = [{'ace':0, 'point':0, 'cards':[], 'doubled_down': False, 'surrendered':False}]
    BOARD_DIV['dealer_hand_data'] =   {'ace':0, 'point':0, 'insurance_bet':False, 'peaked_blacjack':False, 'cards':[], 'is_face_up':[]}
    BOARD_DIV['player_focused_hand_index'] = 0
    BOARD_DIV['round_state'] = 0
    curent_focus_zone_index = BOARD_DIV['index']
    for i in range(7): BOARD_DIV['pad'].addstr(3 + i, 2, '                                                                                         ')
    for i in range(7): BOARD_DIV['pad'].addstr(14 + i, 2, '                                                                                         ')
    BOARD_DIV['pad'].addstr(22, 1, '                                                                                         ')
    DECK_DIV['card_counts'] = {f'{rank}{suit}': SETTING_DIV['cursor_option_values'][3] for suit in SUITS for rank in RANKS}
    
    for y in range(len(SUITS)):
        suit_offset = DECK_DIV['suit_offset'][y]
        for x in range(len(RANKS)):
            DECK_DIV['pad'].addstr(suit_offset[1], suit_offset[0]+DECK_DIV['x_pos'][x], str(SETTING_DIV['cursor_option_values'][5]))
    
    BOARD_DIV['pad'].addstr(5, 105, str(len(BOARD_DIV['deck'])).rjust(3, '0'))
    BOARD_DIV['pad'].addstr(5, 101, str(len(BOARD_DIV['deck'])).rjust(3, '0'))
    BOARD_DIV['pad'].addstr(23, 0, '                   ╔───────────────────────╗ ╔──────────────────────────╗                   ')
    BOARD_DIV['pad'].addstr(24, 0, '                   │ [E] - START THE ROUND │ │ [DEL] - START A NEW GAME │                   ')
    BOARD_DIV['pad'].addstr(25, 0, '                   ╚───────────────────────╝ ╚──────────────────────────╝                   ')
    BOARD_DIV['pad'].addstr(2, 2,  '[----------------│----]                         ')
    BOARD_DIV['pad'].addstr(13, 2, '[----------------│----]                         ')
    BOARD_DIV['pad'].addstr(0, 93, '                         ')
    BOARD_DIV['pad'].refresh(0, 0, BOARD_DIV['origin'][0], BOARD_DIV['origin'][1], BOARD_DIV['end'][0], BOARD_DIV['end'][1])
    
    BOARD_DIV['game_result'] = [BOARD_DIV['game_result'][0] + BOARD_DIV['round_result'][0], BOARD_DIV['game_result'][1] + BOARD_DIV['round_result'][1], BOARD_DIV['game_result'][2] + BOARD_DIV['round_result'][2]]
    BOARD_DIV['pad'].addstr(1, 100, f'{float(BOARD_DIV['game_result'][0])}W'.rjust(6, '0'), resources.get_color_pair_obj(5))
    BOARD_DIV['pad'].addstr(1, 107, f'{BOARD_DIV['game_result'][1]}D'.rjust(4, '0'), resources.get_color_pair_obj(3))
    BOARD_DIV['pad'].addstr(1, 112, f'{float(BOARD_DIV['game_result'][2])}L'.rjust(6, '0'), resources.get_color_pair_obj(4))
    BOARD_DIV['round_result'] = [0.0, 0, 0.0]
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

def draw_random_card(is_face_up=True):
    global BOARD_DIV
    card = BOARD_DIV['deck'][BOARD_DIV['deck_progress_index']]
    BOARD_DIV['deck_progress_index'] += 1
    BOARD_DIV['pad'].addstr(5, 101, str(len(BOARD_DIV['deck']) - BOARD_DIV['deck_progress_index']).rjust(3, '0'))
    if is_face_up:
        DECK_DIV['card_counts'][card] -= 1
        DECK_DIV['pad'].addstr(DECK_DIV['y_pos'][resources.get_first_dupe_index(SUITS, card[-1])], DECK_DIV['x_pos'][resources.get_first_dupe_index(RANKS, card[:-1])], str(DECK_DIV['card_counts'][card]))
    return card
def player_draw_card():
    global BOARD_DIV
    BOARD_DIV['pad'].addstr(22, 1, '                                                                                                                     ')
    if BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['point'] == 21:
        BOARD_DIV['pad'].addstr(22, 1, 'You already got the best possible hand, we are not letting you ruin it!                                               ')
        return
    if BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['point'] < 21 and len(BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards']) >= 5 and SETTING_DIV['cursor_option_values'][3] == 1:
        BOARD_DIV['pad'].addstr(22, 1, 'Five Card Charlie activated! You win this hand!                                                                       ')
        BOARD_DIV['pad'].addstr(22, 1, 'Five Card Charlie', resources.get_color_pair_obj(6))
        return
    if BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['point'] > 21:
        BOARD_DIV['pad'].addstr(22, 1, 'You already busted. No need to draw more card :)')
        BOARD_DIV['pad'].addstr(22, 13, 'busted', resources.get_color_pair_obj(4))
        return
    if len(BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards']) != 0:
        if BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards'][0][0] == 'A' and len(BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards']) == 2 and len(BOARD_DIV['player_hands_data']) != 1 and SETTING_DIV['cursor_option_values'][4] == 0:
            BOARD_DIV['pad'].addstr(22, 1, 'Splitted Aces are only allowed to draw one addition card!                                                             ')
            return
    if BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['surrendered']:
        BOARD_DIV['pad'].addstr(22, 1, 'You have surrendered this hand! Maybe don\'t give up so soon next time?                                               ')
        BOARD_DIV['pad'].addstr(22, 10, 'surrendered', resources.get_color_pair_obj(4))
        return
    if BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['doubled_down']:
        BOARD_DIV['pad'].addstr(22, 1, 'You have doubled down, no more card will be drawn!                                                                    ')
        BOARD_DIV['pad'].addstr(22, 10, 'doubled down', resources.get_color_pair_obj(2))
        return

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
    BOARD_DIV['pad'].addstr(22, 1, '                                                                                                                      ')
    if BOARD_DIV['dealer_hand_data']['point'] > 17 or (BOARD_DIV['dealer_hand_data']['point'] == 17 and SETTING_DIV['cursor_option_values'][0] == 1): 
        round_end()
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
        pass
    rerender_dealer_hand()
    if BOARD_DIV['dealer_hand_data']['point'] > 21:
        BOARD_DIV['pad'].addstr(22, 1, 'Dealer busted! All standing hands won.                                                                                ')
        round_end()

def double_down():
    global BOARD_DIV
    BOARD_DIV['pad'].addstr(22, 1, '                                                                                                                      ')
    if BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['point'] == 21: # Already won
        BOARD_DIV['pad'].addstr(22, 1, 'You already won. No double down allowed!                                                                               ')
        return
    if BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['point'] > 21: # Already lost XD
        BOARD_DIV['pad'].addstr(22, 1, 'No need for doubling down, you already lost XD                                                                         ')
        return
    if BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['doubled_down']:
        BOARD_DIV['pad'].addstr(22, 1, 'You have doubled down!                                                                                                 ')
        return
    
    player_draw_card()
    BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['doubled_down'] = True
    rerender_player_hand()
def split():
    global BOARD_DIV
    BOARD_DIV['pad'].addstr(22, 1, '                                                                                                                      ')
    if not (len(BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards']) == 2 and BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards'][0][0] == BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards'][1][0]): 
        BOARD_DIV['pad'].addstr(22, 1, 'Your hand must have exactly 2 card of the same rank!')
        return
    
    card = BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards'].pop()
    BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['point'] = 11 if card[0] == 'A' else int(BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['point'] / 2)
    BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['ace'] = 1
    BOARD_DIV['player_hands_data'].append({'ace': (1 if card[0]=='A' else 0), 'point':POINTS[resources.get_first_dupe_index(RANKS, card[:-1])], 'cards':[card], 'doubled_down':False, 'surrendered':False})
    BOARD_DIV['pad'].addstr(12, 88, str(len(BOARD_DIV['player_hands_data'])).rjust(2, '0'))
    BOARD_DIV['pad'].addstr(21, 77, '[▼] Hand below')
    rerender_player_hand()
def finish_turn():
    BOARD_DIV['pad'].addstr(22, 1, '                                                                                                                      ')
    BOARD_DIV['dealer_hand_data']['is_face_up'][0] = True
    BOARD_DIV['round_state'] = 3
    rerender_dealer_hand()
    if SETTING_DIV['cursor_option_values'][2] == 1:
        BOARD_DIV['pad'].addstr(23, 1, '╔────────────────────────────────╗                                                                                   ')
        BOARD_DIV['pad'].addstr(24, 1, '│ [SPACE] -  DEALER DRAW A CARD  │                                                                                   ')
        BOARD_DIV['pad'].insstr(25, 1, '╚────────────────────────────────╝                                                                                   ')
        return
    while BOARD_DIV['dealer_hand_data']['point'] < 17: 
        dealer_draw_card(True)
    dealer_draw_card(True)
    dealer_draw_card(True)
def surrender():
    global BOARD_DIV
    if BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['doubled_down']: 
        BOARD_DIV['pad'].addstr(23, 1, 'You have doubled down on this hand! You placed your trust on your hand and it has failed you >:D                      ')
        return
    BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['surrendered'] = True
    rerender_player_hand()

def rerender_player_hand():
    global BOARD_DIV
    blank = ' ' * 89
    BOARD_DIV['pad'].addstr(13, 85, str(BOARD_DIV['player_focused_hand_index']+1).rjust(2, '0'))
    BOARD_DIV['pad'].addstr(13, 77, '              ' if BOARD_DIV['player_focused_hand_index'] == 0 else '[▲] Hand above')
    BOARD_DIV['pad'].addstr(20, 77, '              ' if BOARD_DIV['player_focused_hand_index'] == len(BOARD_DIV['player_hands_data']) - 1 else '[▼] Hand below')
    for i in range(7): BOARD_DIV['pad'].addstr(BOARD_DIV['y_pos'][1] + i, 2, blank)
    for i in range(len(BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards'])):
        image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path / 'drawings' / 'cards' / f'{BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards'][i]}.txt', int(2 + 80.00 / (len(BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards'])*2) * (i*2+1)), BOARD_DIV['y_pos'][1], color_pair_obj=resources.get_color_pair_obj(resources.SUITS_INDEX_DICT[BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards'][i][-1]]))
    ace_remain = BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['ace']
    bar = ''
    for card in BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards']:
        if card[0] != 'A': 
            string = SUIT_SYMBOL[resources.get_first_dupe_index(SUITS, card[-1])] * POINTS[resources.get_first_dupe_index(RANKS, card[:-1])]
        else:
            string = SUIT_SYMBOL[resources.get_first_dupe_index(SUITS, card[-1])] * (11 if ace_remain > 0 else 1)
            ace_remain -= 1
        BOARD_DIV['pad'].addstr(13, 3 + len(bar), string, resources.get_color_pair_obj(resources.SUITS_INDEX_DICT[card[-1]]))
        bar += string
    if BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['doubled_down']:  BOARD_DIV['pad'].addstr(13, 3, bar, resources.get_color_pair_obj(6))
    elif BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['surrendered']: BOARD_DIV['pad'].addstr(13, 3, bar)
    if len(bar) <= 21: 
        BOARD_DIV['pad'].addstr(13, 3 + len(bar), '-' * (21 - len(bar)))
        if len(bar) < 17: BOARD_DIV['pad'].addstr(13, 19,'│')
    if len(bar) > 21: BOARD_DIV['pad'].addstr(22, 1, 'HAND BUSTED!                                                                                                          ', resources.get_color_pair_obj(4))
    BOARD_DIV['pad'].addstr(13, max(25, 2 + len(bar)), f' {BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['point']}P')
def rerender_dealer_hand():
    global BOARD_DIV
    blank = ' ' * 89
    for i in range(7): BOARD_DIV['pad'].addstr(BOARD_DIV['y_pos'][0] + i, 2, blank)
    for i in range(len(BOARD_DIV['dealer_hand_data']['cards'])):
        if BOARD_DIV['dealer_hand_data']['is_face_up'][i] == True: 
            image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path / 'drawings' / 'cards' / f'{BOARD_DIV['dealer_hand_data']['cards'][i]}.txt', int(2 + 80.00 / (len(BOARD_DIV['dealer_hand_data']['cards'])*2) * (i*2+1)), BOARD_DIV['y_pos'][0], color_pair_obj=resources.get_color_pair_obj(resources.SUITS_INDEX_DICT[BOARD_DIV['dealer_hand_data']['cards'][i][-1]]))
        else: image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path / 'drawings' / 'cards' / '___card.txt', int(2 + 80.00 / (len(BOARD_DIV['dealer_hand_data']['cards'])*2) * (i*2+1)), BOARD_DIV['y_pos'][0], color_pair_obj=resources.get_color_pair_obj(5))
    ace_remain = BOARD_DIV['dealer_hand_data']['ace']
    hidden, bar = False, ''
    
    for i in range(len(BOARD_DIV['dealer_hand_data']['cards'])):
        if not BOARD_DIV['dealer_hand_data']['is_face_up'][i]: 
            hidden = True
            continue
        if BOARD_DIV['dealer_hand_data']['cards'][i][0] != 'A': 
            string = SUIT_SYMBOL[resources.get_first_dupe_index(SUITS, BOARD_DIV['dealer_hand_data']['cards'][i][-1])] * POINTS[resources.get_first_dupe_index(RANKS, BOARD_DIV['dealer_hand_data']['cards'][i][:-1])]
        else:
            string = SUIT_SYMBOL[resources.get_first_dupe_index(SUITS, BOARD_DIV['dealer_hand_data']['cards'][i][-1])] * (11 if ace_remain > 0 else 1)
            ace_remain -= 1
        BOARD_DIV['pad'].addstr(2, 3 + len(bar), string, resources.get_color_pair_obj(resources.SUITS_INDEX_DICT[BOARD_DIV['dealer_hand_data']['cards'][i][-1]]))
        bar += string
    if len(bar) <= 21: 
        BOARD_DIV['pad'].addstr(2, 3 + len(bar), ('?' if hidden else '-') * (21 - len(bar)))
        if len(bar) < 17: BOARD_DIV['pad'].addstr(2, 19,'│')
    if not hidden: BOARD_DIV['pad'].addstr(2, max(25, 2 + len(bar)), f' {BOARD_DIV['dealer_hand_data']['point']}P    ')
    elif len(BOARD_DIV['dealer_hand_data']['cards']) > 1: BOARD_DIV['pad'].addstr(2, max(25, 2 + len(bar)), f' {POINTS[resources.get_first_dupe_index(RANKS, BOARD_DIV['dealer_hand_data']['cards'][1][:-1])]}+P')

def begin_the_round():
    global BOARD_DIV
    dealer_draw_card(False)
    dealer_draw_card(True)
    player_draw_card()
    player_draw_card()

def round_end():
    global BOARD_DIV
    if BOARD_DIV['round_state'] >= 4: return
    BOARD_DIV['round_state'] = 4
    BOARD_DIV['pad'].addstr(23, 1, '╔────────────────────────────────╗  DEALER:                                                                          ')
    BOARD_DIV['pad'].addstr(24, 1, '│ [SPACE] -      NEXT ROUND      │  PLAYER:                                                                          ')
    BOARD_DIV['pad'].insstr(25, 1, '╚────────────────────────────────╝                                                                                   ')
    i = 0
    for y in BOARD_DIV['player_hand_ratio_coord']['y']:
        for x in BOARD_DIV['player_hand_ratio_coord']['x']:
            string = f'[{i+1}] {BOARD_DIV['player_hands_data'][i]['point']} in {len(BOARD_DIV['player_hands_data'][i]['cards'])}'
            if BOARD_DIV['player_hands_data'][i]['surrendered']:
                BOARD_DIV['pad'].addstr(y, x + 8 - len(string), string, resources.get_color_pair_obj(6))
                i += 1
                BOARD_DIV['round_result'][2] += .5
                if i == len(BOARD_DIV['player_hands_data']): break
                continue
            BOARD_DIV['pad'].addstr(y, x + 8 - len(string), string, resources.get_color_pair_obj(5 if (BOARD_DIV['dealer_hand_data']['point'] < BOARD_DIV['player_hands_data'][i]['point'] and BOARD_DIV['player_hands_data'][i]['point'] <= 21) or (BOARD_DIV['player_hands_data'][i]['point'] <= 21 and BOARD_DIV['dealer_hand_data']['point'] > 21) or (BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['point'] <= 21 and len(BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards']) >= 5 and SETTING_DIV['cursor_option_values'][3] == 1) else 3 if (BOARD_DIV['dealer_hand_data']['point'] == BOARD_DIV['player_hands_data'][i]['point'] and BOARD_DIV['player_hands_data'][i]['point'] <= 21) else 4))
            
            if (BOARD_DIV['dealer_hand_data']['point'] < BOARD_DIV['player_hands_data'][i]['point'] and BOARD_DIV['player_hands_data'][i]['point'] <= 21) or (BOARD_DIV['player_hands_data'][i]['point'] <= 21 and BOARD_DIV['dealer_hand_data']['point'] > 21) or (BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['point'] <= 21 and len(BOARD_DIV['player_hands_data'][BOARD_DIV['player_focused_hand_index']]['cards']) >= 5 and SETTING_DIV['cursor_option_values'][3] == 1) : 
                BOARD_DIV['round_result'][0] += 2 if BOARD_DIV['player_hands_data'][i]['doubled_down'] else 1 # Win
            elif (BOARD_DIV['dealer_hand_data']['point'] == BOARD_DIV['player_hands_data'][i]['point'] and BOARD_DIV['player_hands_data'][i]['point'] <= 21): 
                BOARD_DIV['round_result'][1] += 1
            else: BOARD_DIV['round_result'][2] += 2 if BOARD_DIV['player_hands_data'][i]['doubled_down'] else 1 # Lost
            i += 1
            if i == len(BOARD_DIV['player_hands_data']): break
        if i == len(BOARD_DIV['player_hands_data']): break
    string = f'{BOARD_DIV['dealer_hand_data']['point']} in {len(BOARD_DIV['dealer_hand_data']['cards'])}'
    BOARD_DIV['pad'].addstr(23, 48 + 8 - len(string), string, resources.get_color_pair_obj(4 if BOARD_DIV['round_result'][2] == 0 and BOARD_DIV['round_result'][1] == 0 else 5 if BOARD_DIV['round_result'][0] == 0 and BOARD_DIV['round_result'][1] == 0 else 3))
    BOARD_DIV['pad'].addstr(0, 99, f'+{float(BOARD_DIV['round_result'][0])}'.rjust(6, ' '), resources.get_color_pair_obj(5))
    BOARD_DIV['pad'].addstr(0, 106, f'+{BOARD_DIV['round_result'][1]}'.rjust(4, ' '), resources.get_color_pair_obj(3))
    BOARD_DIV['pad'].addstr(0, 111, f'+{float(BOARD_DIV['round_result'][2])}'.rjust(6, ' '), resources.get_color_pair_obj(4))
def resolve_insurance_bet():
    global BOARD_DIV
    BOARD_DIV['pad'].addstr(22, 1, 'Dealer peaked for blackjack!                                                                                         ')
    if BOARD_DIV['dealer_hand_data']['point'] == 21:
        BOARD_DIV['dealer_hand_data']['is_face_up'][0] = True
        rerender_dealer_hand()
        BOARD_DIV['pad'].addstr(22, 30, 'Blackjack found and hand is revealed.                                                   ')
        if BOARD_DIV['dealer_hand_data']['insurance_bet']: 
            BOARD_DIV['round_result'][0] += .5
            string = f'+{BOARD_DIV['round_result'][0]}'
            BOARD_DIV['pad'].addstr(0, 105 - len(string), string, resources.get_color_pair_obj(5))
            BOARD_DIV['pad'].addstr(22, 68, 'You won the insurance bet!                       ', resources.get_color_pair_obj(6))
    else:
        BOARD_DIV['pad'].addstr(22, 30, 'None found.                                                         ')
        if BOARD_DIV['dealer_hand_data']['insurance_bet']: 
            BOARD_DIV['round_result'][2] += .5
            string = f'+{BOARD_DIV['round_result'][2]}'
            BOARD_DIV['pad'].addstr(0, 117 - len(string), string, resources.get_color_pair_obj(4))
            BOARD_DIV['pad'].addstr(22, 42, 'You lost the insurance bet!', resources.get_color_pair_obj(4))
    BOARD_DIV['pad'].addstr(23, 1, '╔───────────────────╗ ╔───────────────────╗ ╔─────────────╗ ╔─────────────────╗ ╔──────────────────────────╗')
    BOARD_DIV['pad'].addstr(24, 1, '│ [E] - DRAW A CARD │ │ [D] - DOUBLE DOWN │ │ [F] - SPLIT │ │ [R] - SURRENDER │ │ [SPACE] - PASS TO DEALER │')
    BOARD_DIV['pad'].addstr(25, 1, '╚───────────────────╝ ╚───────────────────╝ ╚─────────────╝ ╚─────────────────╝ ╚──────────────────────────╝')