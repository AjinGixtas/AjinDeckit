from random import randint
from enum import Enum
KEY_MAP_DISPLAY_TABLE = [0,0,0,0,0,0,0,0,0]
BOARD_DIV = { 'current_phases_index': 0, 'roll_value': (0,0,0) }
ACTIVE_BETS = { 'pass_line':-1, 'come':[], 'place_bet':[], 'lay_bet':[], 'field_bet':False, 'big_6':False, 'big_8':False, 'any_7':False, 'hardways':0, 'bet_11':False, 'bet_3':False, 'bet_12':False }
def _start():
    pass
def _update():
    pass
def roll_dice():
    d1, d2 = randint(1, 6), randint(1, 6)
    return (d1 + d2, d1, d2)
def check_bet():
    global BOARD_DIV, ACTIVE_BETS
    if BOARD_DIV['current_phases_index'] == 0:
        if BOARD_DIV['roll_value'][0] == 7 or BOARD_DIV['roll_value'][0] == 11:
            pass