# Halted, revisit later, I forgot solitaire can move multiple card, should've coded freecell instead -_-
from components import resources, image_drawer, scene_manager, key_state_tracker
from components.key_state_tracker import get_key_state, get_axis
from curses import newpad, color_pair
from random import randint, shuffle
SUIT_SYMBOL, SUITS, RANKS, POINTS = ('♥','♦','♠','♣'), ('H','D','S','C'), ('A','2','3','4','5','6','7','8','9','10','J','Q','K'), (1,2,3,4,5,6,7,8,9,10,11,12,13)
KEY_MAP_DISPLAY_TABLE=[0,0,0,0,1,1,1,1,1,1,1]
BOARD_DIV = { 
    'index':0, 'src':'solitaire_board.txt',
    'stock_pile':[], 'waste_pile':[],
    'foundation_piles':[[] for _ in range(4)], 
    'facedown_card_amounts':[i for i in range(7)],
    'tableau_piles':[[] for _ in range(7)],
    'focused_index': [-1, -1], # [0] for [tableau_piles=0, foundation_piles=1]; [1] for pile index; -1 means None
    'pad':None
}
SETTING_DIV = {
    'draw_amount':3
}
TABLEAU_KEYBIND = ['1','2','3','4','5','6','7']
FOUNDATION_KEYBIND = ['1','2','3','4']
STOCK_KEYBIND=['1','2','3','4','5','6']
def _start():
    global origin_x, origin_y, rows, columns
    origin_x, origin_y, rows, columns = scene_manager.get_drawable_screen_data()
    new_game()
def _update():
    BOARD_DIV['pad'].addstr(25, 0, f'{key_state_tracker.get_key_state('ctrl', key_state_tracker.PRESSED)} {key_state_tracker.get_key_state('shift', key_state_tracker.PRESSED)}')
    for i in range(len(TABLEAU_KEYBIND)):
        if key_state_tracker.get_key_state(TABLEAU_KEYBIND[i], key_state_tracker.JUST_PRESSED):
            BOARD_DIV['pad'].addstr(0, 0, str(pile_selection_action_resolver(['tableau_piles', i])))
            rerender_board()
            break
    for i in range(len(FOUNDATION_KEYBIND)):
        if key_state_tracker.get_key_state('ctrl', key_state_tracker.PRESSED) and key_state_tracker.get_key_state(FOUNDATION_KEYBIND[i], key_state_tracker.JUST_PRESSED):
            BOARD_DIV['pad'].addstr(0, 0, str(pile_selection_action_resolver(['foundation_piles', i])))
            rerender_board()x
            break
    for i in range(SETTING_DIV['draw_amount']):
        if key_state_tracker.get_key_state('shift', key_state_tracker.PRESSED) and key_state_tracker.get_key_state(STOCK_KEYBIND[i], key_state_tracker.JUST_PRESSED):
            BOARD_DIV['pad'].addstr(0, 0, str(pile_selection_action_resolver(['waste_pile', i])))
            rerender_board()
            break
    if key_state_tracker.get_key_state('e'): 
        draw_card()
        rerender_board()
def draw_card():
    if len(BOARD_DIV['stock_pile']) == 0:
        BOARD_DIV['stock_pile'] = BOARD_DIV['waste_pile']
        BOARD_DIV['waste_pile'] = []
        return
    for i in range(SETTING_DIV['draw_amount']):
        if BOARD_DIV['stock_pile'] == 0: return
        BOARD_DIV['waste_pile'].append(BOARD_DIV['stock_pile'].pop(0))
def pile_selection_action_resolver(index):
    global BOARD_DIV
    if BOARD_DIV['focused_index'] == [-1,-1] and len(BOARD_DIV[index[0]][index[1]]) > 0: # We've found our focus O_O
        BOARD_DIV['focused_index'] = index
        return 0
    if BOARD_DIV['focused_index'] == index: # Press the same index twice removes it
        BOARD_DIV['focused_index'] = [-1, -1]
        return 1
    if BOARD_DIV['focused_index'][0] == index[0] and (index[0] == 'foundation_piles' or index[0] == 'waste_pile') and len(BOARD_DIV[index[0]][index[1]]) > 0: # Foundation and waste pile can't move between eachother due to suit constraint so we just assign new index
        BOARD_DIV['focused_index'] = index
        return 2
    if BOARD_DIV['focused_index'] == [-1, -1]: 
        return 3
    card_move = BOARD_DIV[BOARD_DIV['focused_index'][0]][BOARD_DIV['focused_index'][1]]
    card_hold = BOARD_DIV[index[0]][index[1]]
    if len(card_move) == 0: return 4
    if BOARD_DIV['focused_index'][0] == 'foundation_piles' and index[0] == 'tableau_piles':
        if card_move[-1][:-1] == 'K' and len(card_hold) == 0: 
            BOARD_DIV[index[0]][index[1]].append(BOARD_DIV[BOARD_DIV['focused_index'][0]][BOARD_DIV['focused_index'][1]].pop())
            BOARD_DIV['focused_index'] = [-1, -1]
            return 5
        if card_move[-1][-1] in ('D','H') == card_hold[-1][-1] in ('D','H'): return
        if not (RANKS.index(card_move[-1][:-1])+1 == RANKS.index(card_hold[-1][:-1])): return
        BOARD_DIV[index[0]][index[1]].append(BOARD_DIV[BOARD_DIV['focused_index'][0]][BOARD_DIV['focused_index'][1]].pop())
        BOARD_DIV['focused_index'] = [-1, -1]
        return 6
    if BOARD_DIV['focused_index'][0] == 'tableau_piles' and index[0] == 'foundation_piles':
        if card_move[-1][:-1] == 'A' and len(card_hold) == 0 and SUITS.index(card_move[-1][-1]) == index[1]: 
            BOARD_DIV[index[0]][index[1]].append(BOARD_DIV[BOARD_DIV['focused_index'][0]][BOARD_DIV['focused_index'][1]].pop())
            BOARD_DIV['focused_index'] = [-1, -1]
            return 7
        if not (SUITS.index(card_move[-1][-1]) == index[1]): return
        if not (len(card_hold) > 0 and RANKS.index(card_move[-1][:-1])-1 == RANKS.index(card_hold[-1][:-1])): return
        BOARD_DIV[index[0]][index[1]].append(BOARD_DIV[BOARD_DIV['focused_index'][0]][BOARD_DIV['focused_index'][1]].pop())
        BOARD_DIV['focused_index'] = [-1, -1]
        return 8
    if BOARD_DIV['focused_index'][0] == 'tableau_piles' and index[0] == 'tableau_piles':
        if card_move[-1][:-1] == 'K' and len(card_hold) == 0:
            BOARD_DIV[index[0]][index[1]].append(BOARD_DIV[BOARD_DIV['focused_index'][0]][BOARD_DIV['focused_index'][1]].pop())
            BOARD_DIV['focused_index'] = [-1, -1]
            return 9
        if (card_move[-1][-1] in ('D','H')) == (card_hold[-1][-1] in ('D','H')): return 10
        if not (RANKS.index(card_move[-1][:-1])+1 == RANKS.index(card_hold[-1][:-1])): return 11
        BOARD_DIV[index[0]][index[1]].append(BOARD_DIV[BOARD_DIV['focused_index'][0]][BOARD_DIV['focused_index'][1]].pop())
        BOARD_DIV['focused_index'] = [-1, -1]
        return 12
def _end():
    return
def new_game():
    global BOARD_DIV
    BOARD_DIV = build_div(BOARD_DIV)
    BOARD_DIV['stock_pile']=[]
    BOARD_DIV['waste_pile']=[]
    BOARD_DIV['foundation_piles']=[[] for _ in range(4)]
    BOARD_DIV['tableau_piles']=[[] for _ in range(7)]
    BOARD_DIV['facedown_card_amounts']=[i for i in range(7)]
    BOARD_DIV['focused_index']=[-1, -1]
    for suit in SUITS:
        for rank in RANKS:
            BOARD_DIV['stock_pile'].append(rank+suit)
    shuffle(BOARD_DIV['stock_pile'])
    for pile_index in range(7):
        for i in range(pile_index+1):
            BOARD_DIV['tableau_piles'][pile_index].append(BOARD_DIV['stock_pile'].pop())
    rerender_board()
def rerender_board():
    global BOARD_DIV
    # Clear tableau board from the previous game
    for i in range(17):
        BOARD_DIV['pad'].addstr(10+i, 1, '                                                                               ')
    # Mark amount of hidden card for tableau piles
    image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path / 'drawings' / 'cards' / f'___card.txt', 0, 1, color_pair_obj=resources.get_color_pair_obj(5))
    # Render foundational piles
    for s in range(len(SUITS)):
        if BOARD_DIV['foundation_piles'][s] == []:
            image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path/'drawings'/'cards'/(f'{SUITS[s]}_emblem.txt'), 36+11*s, 1, color_pair_obj=resources.get_color_pair_obj(4-s))
        else:
            image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path/'drawings'/'cards'/(f'{BOARD_DIV['foundation_piles'][s][-1]}.txt'), 36+11*s, 1, color_pair_obj=resources.get_color_pair_obj(4-s))
    # Render tableau piles
    tableau_anchor = (3,10)
    card_pile_offset = (0,3,5,7,9,11)
    for i in range(len(BOARD_DIV['tableau_piles'])):
        pile_size = 0
        BOARD_DIV['facedown_card_amounts'][i] = max(min(BOARD_DIV['facedown_card_amounts'][i], len(BOARD_DIV['tableau_piles'][i])-1), 0)
        if BOARD_DIV['facedown_card_amounts'][i] > 0:
            image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path/'drawings'/'cards'/f'___card.txt', tableau_anchor[0]+11*i, tableau_anchor[1]+card_pile_offset[pile_size], color_pair_obj=resources.get_color_pair_obj(5))
            BOARD_DIV['pad'].addstr(tableau_anchor[1]+1+card_pile_offset[pile_size], tableau_anchor[0]+2+11*i, f'×{BOARD_DIV['facedown_card_amounts'][i]}', resources.get_color_pair_obj(5))
            pile_size += 1
        faceup_card_amount = len(BOARD_DIV['tableau_piles'][i]) - BOARD_DIV['facedown_card_amounts'][i]
        # Render all faceup card if they are small enough
        if faceup_card_amount <= 3:
            for j in range(-faceup_card_amount, 0, 1):
                image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path/'drawings'/'cards'/f'{BOARD_DIV['tableau_piles'][i][j]}{"_M" if j != -1 else ""}.txt', tableau_anchor[0]+11*i, tableau_anchor[1]+card_pile_offset[pile_size], color_pair_obj=resources.get_color_pair_obj(0 if BOARD_DIV['focused_index'][0] == 'tableau_piles' and BOARD_DIV['focused_index'][1] == i and j == -1 else 4-SUITS.index(BOARD_DIV['tableau_piles'][i][j][-1])))
                pile_size += 1
            continue
        image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path/'drawings'/'cards'/f'{BOARD_DIV['tableau_piles'][i][-faceup_card_amount]}_M.txt', tableau_anchor[0]+11*i, tableau_anchor[1]+card_pile_offset[pile_size], color_pair_obj=resources.get_color_pair_obj(4-SUITS.index(BOARD_DIV['tableau_piles'][i][-faceup_card_amount][-1])))
        pile_size+=1
        image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path/'drawings'/'cards'/f'___card.txt', tableau_anchor[0]+11*i, tableau_anchor[1]+card_pile_offset[pile_size], color_pair_obj=resources.get_color_pair_obj(5))
        BOARD_DIV['pad'].addstr(tableau_anchor[1]+1+card_pile_offset[pile_size], tableau_anchor[0]+1+11*i, f'..   ..', resources.get_color_pair_obj(5))
        pile_size+=1
        image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path/'drawings'/'cards'/f'{BOARD_DIV['tableau_piles'][i][-1]}.txt', tableau_anchor[0]+11*i, tableau_anchor[1]+card_pile_offset[pile_size], color_pair_obj=resources.get_color_pair_obj(0 if BOARD_DIV['focused_index'][0] == 'tableau_piles' and BOARD_DIV['focused_index'][1] == i else 4-SUITS.index(BOARD_DIV['tableau_piles'][i][-1][-1])))
    # Render stock pile
    BOARD_DIV['pad'].addstr(2, 2, f'×{len(BOARD_DIV['stock_pile'])}', resources.get_color_pair_obj(5))
    # Render waste pile
    waste_anchor = (12, 1)
    for i in range(min(SETTING_DIV['draw_amount'], len(BOARD_DIV['waste_pile']))):
        image_drawer.draw_colored_image(BOARD_DIV['pad'], resources.screen_data_path / 'drawings' / 'cards' / f'{BOARD_DIV['waste_pile'][-i]}.txt', waste_anchor[0]+2*i, waste_anchor[1], color_pair_obj=resources.get_color_pair_obj(4-SUITS.index(BOARD_DIV['waste_pile'][-i][-1])))
        
    BOARD_DIV['pad'].refresh(0, 0, BOARD_DIV['origin'][0], BOARD_DIV['origin'][1], BOARD_DIV['end'][0], BOARD_DIV['end'][1])
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