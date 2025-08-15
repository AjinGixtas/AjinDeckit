from components import resources, image_drawer, scene_manager, key_state_tracker
from components.key_state_tracker import get_key_state, get_axis
from curses import newpad, color_pair
from random import randint, shuffle
from pathlib import Path
KEY_MAP_DISPLAY_TABLE=['regicide']
DECLARE_ATTACK, ACTIVATE_SUIT, DEAL_DAMAGE, SUFFER_DAMAGE, END = 0, 1, 2, 3, 4
BOARD_DIV = {
    'index':0, 'src':'boards/regicide_board.txt', 'discard_pile':[], 'draw_pile':[], 'active_pile':[], 'hand':[], 'is_rank_over_suit':False,
    'royal_pile':[], 'boss_rank':None, 'boss_suit':None, 'boss_health':0, 'boss_attack':0, 'boss_suit_disabled': False, 'boss_suit_remaining': [],
    'attack_output': None, 'joker_left':0, 'game_phase':DECLARE_ATTACK, 'waiting_for_next_game': False
}
PILE_DIV = {
    'index':1,'src':'regicide_pile.txt', 'pad': None
}
SETTING_DIV = {
    'hand_size':8,
    'joker_in_pile_amount':0, 
    'starting_joker_amount':2,
    'boss_stat': { 'J':(20,10), 'Q':(30,15), 'K':(40,20) },
    'auto_pass_phase': True
}

FOCUSED_DIV_INDEX = BOARD_DIV['index']
SUIT_SYMBOL, SUITS, RANKS, POINTS = ('♣','♠','♦','♥',), ('C', 'S', 'D', 'H'), ('A','2','3','4','5','6','7','8','9','10','J','Q','K'), (1,2,3,4,5,6,7,8,9,10,SETTING_DIV['boss_stat']['J'][1],SETTING_DIV['boss_stat']['Q'][1],SETTING_DIV['boss_stat']['K'][1])
def _start():
    global origin_x, origin_y, rows, columns, BOARD_DIV
    origin_x, origin_y, rows, columns = scene_manager.get_drawable_screen_data()
    setup_var()
    new_game()
def setup_var():
    global BOARD_DIV
    BOARD_DIV = {
        'index':0, 'src':'boards/regicide_board.txt', 'discard_pile':[], 'draw_pile':[], 'active_pile':[], 'hand':[], 'is_rank_over_suit':False,
        'royal_pile':[], 'boss_rank':None, 'boss_suit':None, 'boss_health':0, 'boss_attack':0, 'boss_suit_disabled': False, 'attack_output': None,
        'joker_left':0, 'game_phase':DECLARE_ATTACK,
    }
    BOARD_DIV['hand_zone_length'] = 80
    BOARD_DIV['hand_amount_anchor'] = (81, 13)
    BOARD_DIV['attack_data_display_anchor'] = (1,11)
    BOARD_DIV['player_hand_anchor'] = (2,16)
    BOARD_DIV['active_card_zone_length'] = 89
    BOARD_DIV['active_card_anchor'] = (27, 2)
    
    PILE_DIV['draw_pile_anchor'] = (0, 0)
    PILE_DIV['discard_pile_anchor'] = (0, 8)
    PILE_DIV['pile_display_length'] = 118
def _update():
    global BOARD_DIV
    if FOCUSED_DIV_INDEX == BOARD_DIV['index']: update_board_div()
    elif FOCUSED_DIV_INDEX == PILE_DIV['index']: update_pile_div()
def _end():
    return

def update_board_div():
    global BOARD_DIV
    def select_card(str_index):
        index = int(str_index)-1
        if not (0 <= index and index < 10 and index < len(BOARD_DIV['hand'])): return
        BOARD_DIV['hand'][index][1] = not BOARD_DIV['hand'][index][1]
    def declare_attack_phase_update():
        NUM_KEYS=['1','2','3','4','5','6','7','8','9']
        update_hand = False
        for num_key in NUM_KEYS:
            if key_state_tracker.get_key_state(num_key, key_state_tracker.JUST_PRESSED):
                select_card(num_key)
                update_hand = True
        if key_state_tracker.get_key_state('j', key_state_tracker.JUST_PRESSED): new_hand()
        # Sorting card
        if key_state_tracker.get_key_state('n', key_state_tracker.JUST_PRESSED): 
            BOARD_DIV['is_rank_over_suit'] = False
            BOARD_DIV['hand'] = sort_hand(BOARD_DIV['hand'], RANKS, SUITS, is_rank_over_suit=BOARD_DIV['is_rank_over_suit'])
            update_hand = True
        elif key_state_tracker.get_key_state('m', key_state_tracker.JUST_PRESSED):
            BOARD_DIV['is_rank_over_suit'] = True
            BOARD_DIV['hand'] = sort_hand(BOARD_DIV['hand'], RANKS, SUITS, is_rank_over_suit=BOARD_DIV['is_rank_over_suit'])
            update_hand = True
        
        # Attack and move to the next phase
        if key_state_tracker.get_key_state('space', key_state_tracker.JUST_PRESSED):
            BOARD_DIV['attack_output'] = exec_attack()
            if not isinstance(BOARD_DIV['attack_output'], int) and BOARD_DIV['attack_output'] != (0, 0, 0, 0):
                BOARD_DIV['game_phase'] = ACTIVATE_SUIT
                render_active_pile()
        if key_state_tracker.get_key_state('i', key_state_tracker.JUST_PRESSED): activate_joker()
        if update_hand: render_hand()
    def activate_suit_phase_update():
        # Activate suit and move to the next phase
        if key_state_tracker.get_key_state('space', key_state_tracker.JUST_PRESSED) or SETTING_DIV['auto_pass_phase']:
            BOARD_DIV['game_phase'] = DEAL_DAMAGE
            activate_suit()
            render_hand()
            render_pile_data()
    def deal_damage_phase_update():
        # Deal damage and move to the next phase
        if key_state_tracker.get_key_state('space', key_state_tracker.JUST_PRESSED) or SETTING_DIV['auto_pass_phase']:
            BOARD_DIV['game_phase'] = SUFFER_DAMAGE
            calc_damage_tolerance()
            damage_boss(BOARD_DIV['attack_output'][2])
            render_boss()
            render_hand()
    def suffer_damage_phase_update():
        update_hand = False
        if BOARD_DIV['boss_health'] <= 0: 
            BOARD_DIV['game_phase'] = DECLARE_ATTACK
            next_boss()
            render_boss()
            render_active_pile()
            render_pile_data()
            render_hand()
            return
        if BOARD_DIV['boss_attack'] <= 0:
            BOARD_DIV['game_phase'] = DECLARE_ATTACK
            render_hand()
            return
        NUM_KEYS=['1','2','3','4','5','6','7','8','9']
        for num_key in NUM_KEYS:
            if key_state_tracker.get_key_state(num_key, key_state_tracker.JUST_PRESSED):
                select_card(num_key)
                update_hand = True
        if key_state_tracker.get_key_state('j', key_state_tracker.JUST_PRESSED): new_hand()
        if key_state_tracker.get_key_state('space', key_state_tracker.JUST_PRESSED):
            damage_absorbtion_result = take_damage()
            if damage_absorbtion_result == 0:
                BOARD_DIV['game_phase'] = DECLARE_ATTACK
                render_pile_data()
                update_hand = True
        if update_hand: render_hand()
    if not BOARD_DIV['waiting_for_next_game']:
        if BOARD_DIV['game_phase'] == DECLARE_ATTACK: declare_attack_phase_update()
        if BOARD_DIV['game_phase'] == ACTIVATE_SUIT: activate_suit_phase_update()
        if BOARD_DIV['game_phase'] == DEAL_DAMAGE: deal_damage_phase_update()
        if BOARD_DIV['game_phase'] == SUFFER_DAMAGE: suffer_damage_phase_update()
    if key_state_tracker.get_key_state('a', key_state_tracker.JUST_PRESSED): 
        start_pile_div()
        render_div(PILE_DIV)
    if key_state_tracker.get_key_state('backspace', key_state_tracker.PRESSED):
        new_game()
from copy import deepcopy
def start_pile_div():
    global BOARD_DIV, PILE_DIV
    for i in range(0, 7): PILE_DIV['pad'].addstr(PILE_DIV['draw_pile_anchor'][1]+i, PILE_DIV['draw_pile_anchor'][0], ' ' * PILE_DIV['pile_display_length'])
    for i in range(0, 7): PILE_DIV['pad'].addstr(PILE_DIV['discard_pile_anchor'][1]+i, PILE_DIV['discard_pile_anchor'][0], ' ' * PILE_DIV['pile_display_length'])
    marker = PILE_DIV['draw_pile_anchor'][0]
    draw_pile = deepcopy(BOARD_DIV['draw_pile'])
    draw_pile.sort(key=lambda card:  (SUITS.index(suit(card)), RANKS.index(rank(card)) ))
    for i in range(len(draw_pile)):
        image_drawer.draw_colored_image(PILE_DIV['pad'], resources.screen_data_path/'drawings'/'cards'/f'{draw_pile[i]}.txt', marker, PILE_DIV['draw_pile_anchor'][1], color_pair_obj=resources.get_color_pair_obj(1+SUITS.index(suit(draw_pile[i]))))
        marker += 1 + len(rank(draw_pile[i]))
    marker = PILE_DIV['discard_pile_anchor'][0]
    discard_pile = deepcopy(BOARD_DIV['discard_pile'])
    discard_pile.sort(key=lambda card:  (SUITS.index(suit(card)), RANKS.index(rank(card)) ))
    for i in range(len(BOARD_DIV['discard_pile'])):
        image_drawer.draw_colored_image(PILE_DIV['pad'], resources.screen_data_path/'drawings'/'cards'/f'{discard_pile[i]}.txt', marker, PILE_DIV['discard_pile_anchor'][1], color_pair_obj=resources.get_color_pair_obj(1+SUITS.index(suit(discard_pile[i]))))
        marker += 1 + len(rank(discard_pile[i]))
    refresh_div(PILE_DIV)
def update_pile_div():
    if key_state_tracker.get_key_state('a', key_state_tracker.JUST_PRESSED): render_div(BOARD_DIV)
    
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
    div['origin'] = ((rows - div['size'][0])//2+1, (columns - div['size'][1]) // 2+1)
    div['end'] = (div['origin'][0] + div['size'][0], div['origin'][1] + div['size'][1])
    return div

def new_game():
    global BOARD_DIV, PILE_DIV
    BOARD_DIV = build_div(BOARD_DIV)
    PILE_DIV = build_div(PILE_DIV)
    BOARD_DIV['waiting_for_next_game'] = False
    BOARD_DIV['joker_left'] = SETTING_DIV['starting_joker_amount']
    BOARD_DIV['draw_pile'] = []
    BOARD_DIV['discard_pile'] = []
    BOARD_DIV['active_pile'] = []
    BOARD_DIV['royal_pile'] = []
    BOARD_DIV['hand'] = []
    BOARD_DIV['boss_rank'] = None
    BOARD_DIV['boss_suit'] = None
    BOARD_DIV['game_phase'] = DECLARE_ATTACK
    BOARD_DIV['boss_suit_remaining'] = ['C', 'S', 'D', 'H']
    # Setup royal pile
    for rank in ('K', 'Q', 'J'):
        rank_pile = []
        for suit in SUITS:
            rank_pile.append(rank + suit)
        shuffle(rank_pile)  
        BOARD_DIV['royal_pile'] += rank_pile
    # Setup tavern pile
    for rank in ('A','2','3','4','5','6','7','8','9','10'):
        for suit in SUITS:
            BOARD_DIV['draw_pile'].append(rank+suit)
    JOKER_SUIT = ['C','H','S','D']
    for joker in range(SETTING_DIV['joker_in_pile_amount']):
        BOARD_DIV['draw_pile'].append('!'+JOKER_SUIT[joker%4])
    shuffle(BOARD_DIV['draw_pile'])
    draw_card(SETTING_DIV['hand_size'])
    next_boss()
    render_board()
    refresh_div(BOARD_DIV)
def next_boss():
    global BOARD_DIV
    if len(BOARD_DIV['royal_pile']) <= 0:
        win()
        return
    if BOARD_DIV['boss_rank'] != None and len(BOARD_DIV['boss_rank']) > 0:
        if BOARD_DIV['boss_suit_remaining'] == None or len(BOARD_DIV['boss_suit_remaining']) == 0: BOARD_DIV['boss_suit_remaining'] = ['C', 'S', 'D', 'H']
        killed_boss = BOARD_DIV['boss_rank'] + BOARD_DIV['boss_suit']
        if BOARD_DIV['boss_health'] == 0: # Perfect kill!
            BOARD_DIV['draw_pile'].append(killed_boss)
        else:
            BOARD_DIV['discard_pile'].append(killed_boss)
    next_boss = BOARD_DIV['royal_pile'].pop()
    BOARD_DIV['boss_rank'] = rank(next_boss)
    BOARD_DIV['boss_suit'] = suit(next_boss)
    BOARD_DIV['boss_suit_disabled'] = False
    BOARD_DIV['boss_health'], BOARD_DIV['boss_attack'] = SETTING_DIV['boss_stat'][BOARD_DIV['boss_rank']]
    BOARD_DIV['discard_pile'].extend(BOARD_DIV['active_pile'])
    BOARD_DIV['active_pile'] = []
    BOARD_DIV['boss_suit_remaining'].remove(BOARD_DIV['boss_suit'])
    render_pile_data()
def calc_attack():
    cards = [card for card, selected in BOARD_DIV['hand'] if selected]
    if len(cards) == 0: return (0, 0, 0, 0)
    attackers, companions = [], []
    for i in range(len(cards)):
        if rank(cards[i]) == 'A': 
            companions.append(cards[i])
            continue
        attackers.append(cards[i])
    # GUARD BLOCK
    if len(attackers) == 1: # Single attack spotted!
        if len(companions) > 1: return 1 # One companion allowed!
    if len(attackers) > 1: # Combo attack spotted!
        if len(companions) > 0: return 2 # No companion allowed!
        if not all(rank(attacker) == rank(attackers[0]) for attacker in attackers): return 3 # All rank must be the same!
        if sum(POINTS[RANKS.index(rank(attacker))] for attacker in attackers) > 10: return 4 # Attack deal at most 10 damage!
    
    if len(attackers) == 0: # Putting companions without attackers feels weird. It's fine (probably), but let's not take the chance :p
        attackers, companions = companions, []
    SUIT_ORDER = ['H', 'D', 'C', 'S']
    active_suits = [False,False,False,False]
    attack_power = 0
    for attacker in attackers:
        attack_power += POINTS[RANKS.index(rank(attacker))]
        active_suits[SUIT_ORDER.index(suit(attacker))] = True
    for companion in companions:
        attack_power += POINTS[RANKS.index(rank(companion))]
        active_suits[SUIT_ORDER.index(suit(companion))] = True
    if not BOARD_DIV['boss_suit_disabled']: active_suits[SUIT_ORDER.index(BOARD_DIV['boss_suit'])] = False # Enable suit value then disable it by boss late is clean code
    heal = attack_power if active_suits[0] else 0
    draw = attack_power if active_suits[1] else 0
    damage = (attack_power * 2) if active_suits[2] else attack_power
    shield =  attack_power if active_suits[3] else 0
    return (heal, draw, damage, shield)
def exec_attack():
    data = calc_attack()
    if isinstance(data, int): return 1 # Error in attack founded!
    for i in reversed(range(len(BOARD_DIV['hand']))):
        if BOARD_DIV['hand'][i][1]:
            card = BOARD_DIV['hand'].pop(i)[0]
            BOARD_DIV['active_pile'].append(card)
    return data
def activate_suit():
    global BOARD_DIV
    heal(BOARD_DIV['attack_output'][0])
    draw_card(BOARD_DIV['attack_output'][1])
    shield(BOARD_DIV['attack_output'][3])

def activate_joker():
    if BOARD_DIV['joker_left'] <= 0: return
    BOARD_DIV['joker_left'] -= 1
    BOARD_DIV['boss_suit_disabled'] = True
    render_boss()
    render_hand()
def new_hand():
    if BOARD_DIV['joker_left'] <= 0: return
    BOARD_DIV['joker_left'] -= 1
    for i in range(len(BOARD_DIV['hand'])):
        BOARD_DIV['hand'][i][1] = True
    discard_cards = [card for card, selected in BOARD_DIV['hand'] if selected]
    for card in discard_cards:
        BOARD_DIV['discard_pile'].append(card)
    BOARD_DIV['hand'] = []
    draw_card(SETTING_DIV['hand_size'])
    render_hand()
    render_pile_data()

def heal(amount):
    shuffle(BOARD_DIV['discard_pile'])
    for i in range(min(amount, len(BOARD_DIV['discard_pile']))):
        BOARD_DIV['draw_pile'].insert(0, BOARD_DIV['discard_pile'].pop())
def draw_card(amount):
    global BOARD_DIV
    for i in range(min(amount, len(BOARD_DIV['draw_pile']), SETTING_DIV['hand_size']-len(BOARD_DIV['hand']))):
        BOARD_DIV['hand'].append([BOARD_DIV['draw_pile'].pop(), False])
def damage_boss(damage): 
    BOARD_DIV['boss_health'] -= damage
def shield(shield): 
    BOARD_DIV['boss_attack'] = max(0, BOARD_DIV['boss_attack'] - shield)

def calc_damage():
    cards = [card for card, selected in BOARD_DIV['hand'] if selected]
    point_total = 0
    for card in cards:
        point_total += POINTS[RANKS.index(rank(card))]
    return point_total
def take_damage():
    if calc_damage() < BOARD_DIV['boss_attack']: return 1
    discard_cards = [card for card, selected in BOARD_DIV['hand'] if selected]
    kept_cards = [[card, selected] for card, selected in BOARD_DIV['hand'] if not selected]
    for card in discard_cards:
        BOARD_DIV['discard_pile'].append(card)
    BOARD_DIV['hand'] = kept_cards
    return 0

def win():
    BOARD_DIV['waiting_for_next_game'] = True
    BOARD_DIV['pad'].addstr(24, 1, "You've won! Press `backspace` to start a new game.")
    refresh_div(BOARD_DIV)
def lose():
    BOARD_DIV['waiting_for_next_game'] = True
    BOARD_DIV['pad'].addstr(24, 1, "You've lost! Press `backspace` to start a new game.")
    refresh_div(BOARD_DIV)
def calc_damage_tolerance():
    global BOARD_DIV
    total_health = 0
    for card in BOARD_DIV['hand']:
        total_health += POINTS[RANKS.index(rank(card[0]))]
    # Not enough card with no bailout joker
    if total_health < BOARD_DIV['boss_attack'] and BOARD_DIV['joker_left'] == 0:
        lose()
def suit(card): return card[-1]
def rank(card): return card[:-1]

def render_board():
    render_boss()
    render_hand()
    render_pile_data()
    render_active_pile()
    
def render_boss():
    BOARD_DIV['boss_card_anchor'] = (2,2) # (x,y)
    image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path/'drawings'/'cards'/(str(BOARD_DIV['boss_rank'])+BOARD_DIV['boss_suit']+'.txt'), BOARD_DIV['boss_card_anchor'][0], BOARD_DIV['boss_card_anchor'][1], color_pair_obj=resources.get_color_pair_obj((1+SUITS.index(BOARD_DIV['boss_suit'])) if not BOARD_DIV['boss_suit_disabled'] else 0 ))
    BOARD_DIV['pad'].addstr(4, 20, f"{BOARD_DIV['boss_health']:3}", resources.get_color_pair_obj(5))
    BOARD_DIV['pad'].addstr(5, 20, f"{BOARD_DIV['boss_attack']:3}", resources.get_color_pair_obj(6))
    BOARD_DIV['pad'].addstr(6, 20, str(SUIT_SYMBOL[SUITS.index(BOARD_DIV['boss_suit'])]), resources.get_color_pair_obj((1+SUITS.index(BOARD_DIV['boss_suit'])) if not BOARD_DIV['boss_suit_disabled'] else 0))
    RANK_NAME = ('JACK', 'QUEEN', 'KING')
    SUIT_NAME = ('CLUB', 'SPADE', 'DIAMOND', 'HEART')
    boss_name = f'{RANK_NAME[RANKS.index(BOARD_DIV['boss_rank'])-10]} OF {SUIT_NAME[SUITS.index(BOARD_DIV['boss_suit'])]}'
    boss_name_div_width = 21
    BOARD_DIV['pad'].addstr(1, 2, boss_name + (' ' * int((boss_name_div_width-len(boss_name)))), resources.get_color_pair_obj(1+SUITS.index(BOARD_DIV['boss_suit'])) if not BOARD_DIV['boss_suit_disabled'] else 0)
    BOARD_DIV['pad'].refresh(1, 1, BOARD_DIV['origin'][0]+1, BOARD_DIV['origin'][1]+1, BOARD_DIV['origin'][0]+8, BOARD_DIV['origin'][1]+22)
def render_hand():
    global BOARD_DIV
    def render_attack_data():
        attack_evaluation = calc_attack()
        #BOARD_DIV['pad'].addstr(BOARD_DIV['attack_data_display_anchor'][1]-1, BOARD_DIV['attack_data_display_anchor'][0], f"{attack_evaluation}                                 ")
        BOARD_DIV['pad'].addstr(BOARD_DIV['attack_data_display_anchor'][1], BOARD_DIV['attack_data_display_anchor'][0], "                                                                                 ")
        BOARD_DIV['pad'].addstr(BOARD_DIV['attack_data_display_anchor'][1], BOARD_DIV['attack_data_display_anchor'][0]+9, "HEAL: 0", resources.get_color_pair_obj(4 if BOARD_DIV['boss_suit'] != 'H' or BOARD_DIV['boss_suit_disabled'] else 7))
        BOARD_DIV['pad'].addstr(BOARD_DIV['attack_data_display_anchor'][1], BOARD_DIV['attack_data_display_anchor'][0]+26, "DRAW: 0", resources.get_color_pair_obj(3 if BOARD_DIV['boss_suit'] != 'D' or BOARD_DIV['boss_suit_disabled'] else 7))
        BOARD_DIV['pad'].addstr(BOARD_DIV['attack_data_display_anchor'][1], BOARD_DIV['attack_data_display_anchor'][0]+43, "DAMAGE: 0", resources.get_color_pair_obj(1 if BOARD_DIV['boss_suit'] != 'C' or BOARD_DIV['boss_suit_disabled'] else 0))
        BOARD_DIV['pad'].addstr(BOARD_DIV['attack_data_display_anchor'][1], BOARD_DIV['attack_data_display_anchor'][0]+62, "SHIELD: 0", resources.get_color_pair_obj(2 if BOARD_DIV['boss_suit'] != 'S' or BOARD_DIV['boss_suit_disabled'] else 7))
        
        if isinstance(attack_evaluation, tuple):
            BOARD_DIV['pad'].addstr(BOARD_DIV['attack_data_display_anchor'][1], BOARD_DIV['attack_data_display_anchor'][0]+15, f"{attack_evaluation[0] if BOARD_DIV['boss_suit'] != 'H' or BOARD_DIV['boss_suit_disabled'] else ' ' :<5}")
            BOARD_DIV['pad'].addstr(BOARD_DIV['attack_data_display_anchor'][1], BOARD_DIV['attack_data_display_anchor'][0]+32, f"{f"{attack_evaluation[1] if attack_evaluation[1] <= SETTING_DIV['hand_size'] - len(BOARD_DIV['hand']) + sum(b for _, b in BOARD_DIV['hand']) else f"{attack_evaluation[1]}({SETTING_DIV['hand_size'] - len(BOARD_DIV['hand']) + sum(b for _, b in BOARD_DIV['hand'])})"}" if BOARD_DIV['boss_suit'] != 'D' or BOARD_DIV['boss_suit_disabled']else ' ' :<5}")
            BOARD_DIV['pad'].addstr(BOARD_DIV['attack_data_display_anchor'][1], BOARD_DIV['attack_data_display_anchor'][0]+51, f"{attack_evaluation[2]:<3}")
            BOARD_DIV['pad'].addstr(BOARD_DIV['attack_data_display_anchor'][1], BOARD_DIV['attack_data_display_anchor'][0]+70, f"{attack_evaluation[3] if BOARD_DIV['boss_suit'] != 'S' or BOARD_DIV['boss_suit_disabled'] else ' ':<5}")
        elif isinstance(attack_evaluation, int):
            if attack_evaluation == 1: 
                BOARD_DIV['pad'].addstr(BOARD_DIV['attack_data_display_anchor'][1], BOARD_DIV['attack_data_display_anchor'][0],   " Only one Ace is allowed in companion attack!" + " " * 36)
                BOARD_DIV['pad'].addstr(BOARD_DIV['attack_data_display_anchor'][1], BOARD_DIV['attack_data_display_anchor'][0]+6,       "one", resources.get_color_pair_obj(4))
            else:
                BOARD_DIV['pad'].addstr(BOARD_DIV['attack_data_display_anchor'][1], BOARD_DIV['attack_data_display_anchor'][0], " Combo attack", resources.get_color_pair_obj(6))
                if attack_evaluation == 2: 
                    BOARD_DIV['pad'].addstr(BOARD_DIV['attack_data_display_anchor'][1], BOARD_DIV['attack_data_display_anchor'][0],    " Combo attack can only use card of the same rank!" + " " * 32)
                    BOARD_DIV['pad'].addstr(BOARD_DIV['attack_data_display_anchor'][1], BOARD_DIV['attack_data_display_anchor'][0]+39,                                        "same", resources.get_color_pair_obj(4))
                if attack_evaluation == 3: 
                    BOARD_DIV['pad'].addstr(BOARD_DIV['attack_data_display_anchor'][1], BOARD_DIV['attack_data_display_anchor'][0],    " Combo attack can only use card of the same rank!" + " " * 32)
                    BOARD_DIV['pad'].addstr(BOARD_DIV['attack_data_display_anchor'][1], BOARD_DIV['attack_data_display_anchor'][0]+39,                                        "same", resources.get_color_pair_obj(4))
                if attack_evaluation == 4: 
                    BOARD_DIV['pad'].addstr(BOARD_DIV['attack_data_display_anchor'][1], BOARD_DIV['attack_data_display_anchor'][0],   " Combo attack can't deal more than 10 damage!" + " " * 36)
                    BOARD_DIV['pad'].addstr(BOARD_DIV['attack_data_display_anchor'][1], BOARD_DIV['attack_data_display_anchor'][0]+35,                                   "10", resources.get_color_pair_obj(4))
    def render_absorb_damage_data():
        damage_evaluation = calc_damage()
        notification = f"Damage absorbed: {damage_evaluation}/{BOARD_DIV['boss_attack']} {f"(Over absorbed by {damage_evaluation - BOARD_DIV['boss_attack']} damage)" if damage_evaluation > BOARD_DIV['boss_attack'] else " "}"
        BOARD_DIV['pad'].addstr(BOARD_DIV['attack_data_display_anchor'][1], BOARD_DIV['attack_data_display_anchor'][0], notification + ' ' * (81 - len(notification)), resources.get_color_pair_obj(4))
    part_size = len(str(SETTING_DIV['hand_size']))
    hand_amount = f'[{len(BOARD_DIV['hand']):0{part_size}}/{SETTING_DIV['hand_size']}]'
    BOARD_DIV['pad'].addstr(BOARD_DIV['hand_amount_anchor'][1], BOARD_DIV['hand_amount_anchor'][0]-len(hand_amount), hand_amount)
    BOARD_DIV['hand'] = sort_hand(BOARD_DIV['hand'], RANKS, SUITS, is_rank_over_suit=BOARD_DIV['is_rank_over_suit'])
    BOARD_DIV['pad'].addstr(BOARD_DIV['player_hand_anchor'][1]-1, BOARD_DIV['player_hand_anchor'][0], ' ' * 79)
    BOARD_DIV['pad'].addstr(BOARD_DIV['player_hand_anchor'][1]+6, BOARD_DIV['player_hand_anchor'][0], ' ' * 79)
    for i in range(BOARD_DIV['player_hand_anchor'][1]-1, BOARD_DIV['player_hand_anchor'][1]+7):
        BOARD_DIV['pad'].addstr(i, BOARD_DIV['player_hand_anchor'][0], ' ' * 79)
    if BOARD_DIV['game_phase'] == DECLARE_ATTACK: render_attack_data()
    elif BOARD_DIV['game_phase'] == SUFFER_DAMAGE: render_absorb_damage_data()

    for i in range(len(BOARD_DIV['hand'])):
        image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path/'drawings'/'cards'/f'{BOARD_DIV['hand'][i][0]}.txt', BOARD_DIV['player_hand_anchor'][0] + int(BOARD_DIV['hand_zone_length']/SETTING_DIV['hand_size']*i), BOARD_DIV['player_hand_anchor'][1] + (-1 if BOARD_DIV['hand'][i][1] else 0), color_pair_obj=resources.get_color_pair_obj(1+SUITS.index(suit(BOARD_DIV['hand'][i][0]))))
    BOARD_DIV['pad'].refresh(11, 1, BOARD_DIV['origin'][0]+11, BOARD_DIV['origin'][1]+1, BOARD_DIV['origin'][0]+22, BOARD_DIV['origin'][1]+81)
def render_active_pile():
    global BOARD_DIV
    # Clear drawing for the next draw step
    for y in range(BOARD_DIV['active_card_anchor'][1], BOARD_DIV['active_card_anchor'][1]+7):
        BOARD_DIV['pad'].addstr(y, 24, ' '*93)
    # Draw active cards
    for i in range(len(BOARD_DIV['active_pile'])):
        image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path/'drawings'/'cards'/f'{BOARD_DIV['active_pile'][i]}.txt', BOARD_DIV['active_card_anchor'][0] + int(BOARD_DIV['active_card_zone_length']/(len(BOARD_DIV['active_pile'])+1)*(i+1)) - 5, BOARD_DIV['active_card_anchor'][1], color_pair_obj=resources.get_color_pair_obj(1+SUITS.index(suit(BOARD_DIV['active_pile'][i]))))
    # Draw upcoming suits
    BOARD_DIV['pad'].addstr(1, 110, ' ' * 7)
    for i in range(len(BOARD_DIV['boss_suit_remaining'])):
        BOARD_DIV['pad'].addstr(1, 109+i*2, SUIT_SYMBOL[SUITS.index(BOARD_DIV['boss_suit_remaining'][i])], resources.get_color_pair_obj(1+SUITS.index(BOARD_DIV['boss_suit_remaining'][i])))
    BOARD_DIV['pad'].refresh(1, 24, BOARD_DIV['origin'][0]+1, BOARD_DIV['origin'][1]+24, BOARD_DIV['origin'][0]+8, BOARD_DIV['origin'][1]+116)
def render_pile_data():
    global BOARD_DIV
    BOARD_DIV['pad'].addstr(10, 90, f"JOKER REMAINING: {BOARD_DIV['joker_left']}")
    BOARD_DIV['pad'].addstr(12, 94, f"{len(BOARD_DIV['draw_pile']):2}" )
    BOARD_DIV['pad'].addstr(12, 105, f"{len(BOARD_DIV['discard_pile']):<2}")
    image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path/'drawings'/'cards'/'___card.txt', 90, 13, color_pair_obj=resources.get_color_pair_obj(5))
    image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path/'drawings'/'cards'/f'{BOARD_DIV['discard_pile'][-1] if len(BOARD_DIV['discard_pile']) else 'blank_card'}.txt', 101, 13, color_pair_obj=resources.get_color_pair_obj( (1+SUITS.index(suit(BOARD_DIV['discard_pile'][-1]))) if len(BOARD_DIV['discard_pile']) > 0 else 0 ))
    BOARD_DIV['pad'].refresh(10, 90, BOARD_DIV['origin'][0]+10, BOARD_DIV['origin'][1]+90, BOARD_DIV['origin'][0]+12, BOARD_DIV['origin'][1]+118)
    refresh_div(BOARD_DIV)
def refresh_div(div):
    div['pad'].refresh(0, 0, div['origin'][0], div['origin'][1], div['end'][0], div['end'][1])
def render_div(div): 
    global FOCUSED_DIV_INDEX
    FOCUSED_DIV_INDEX = div['index']
    refresh_div(div)

def sort_hand(cards, sorted_rank, sorted_suit, is_rank_over_suit=True):
    if is_rank_over_suit: cards.sort(key=lambda card: (sorted_rank.index(rank(card[0])), sorted_suit.index(suit(card[0])) ))
    else:                 cards.sort(key=lambda card: (sorted_suit.index(suit(card[0])),  sorted_rank.index(rank(card[0])) ))
    return cards
