from pynput.keyboard import Listener, GlobalHotKeys, KeyCode, Key
from time import time
from copy import deepcopy
from msvcrt import kbhit, getch
JUST_PRESSED = 0
PRESSED = 1
JUST_RELEASED = 2
BLOCK_TIME = .25

keyboard_listener, hotkey_listener = None, None
def ctrl_q():
    if kbhit(): _ = getch()
    key_states[JUST_PRESSED].append(GlobalKey('ctrl'))
    key_states[JUST_PRESSED].append(GlobalKey('q'))
def _start():
    global keyboard_listener, hotkey_listener
    keyboard_listener = Listener(on_press=on_press, on_release=on_release)
    
    hotkeys = { '<ctrl>+q': ctrl_q }
    hotkey_listener = GlobalHotKeys(hotkeys)
    
    keyboard_listener.start()
    hotkey_listener.start()
def _update():
    key_states[JUST_PRESSED].clear()
    key_states[JUST_RELEASED].clear()
def _end():
    keyboard_listener.stop()
    hotkey_listener.stop()

key_states, just_pressed_time_stamp = [ [], [], [] ], {}
def get_key_state(key, state = PRESSED):
    global key_states, just_pressed_time_stamp
    _key_states = deepcopy(key_states)
    if state == PRESSED:
        if any(key == key_state.name for key_state in _key_states[JUST_PRESSED]): return True
        
        _key = next((obj for obj in just_pressed_time_stamp.keys() if obj.name == key), None)
        if _key == None: return False
        if time() - just_pressed_time_stamp[_key] < BLOCK_TIME: return False
    return any(key == key_state.name for key_state in _key_states[state])
def get_axis(negative_x_key, positive_x_key, negative_y_key = '', positive_y_key = ''):
    if positive_y_key == '' or negative_y_key == '': return 1 if get_key_state(positive_x_key) else -1 if get_key_state(negative_x_key) else 0
    return (1 if get_key_state(positive_x_key) else -1 if get_key_state(negative_x_key) else 0, 1 if get_key_state(positive_y_key) else -1 if get_key_state(negative_y_key) else 0)

def on_press(key):
    global key_states, just_pressed_time_stamp
    if kbhit(): _ = getch()
    key = GlobalKey(key)
    key_states[JUST_PRESSED].append(key)
    key_states[PRESSED].append(key)
    just_pressed_time_stamp[key] = time()
def on_release(key):
    global key_states, just_pressed_time_stamp
    if kbhit(): _ = getch()
    key = GlobalKey(key)
    key_states[JUST_RELEASED].append(GlobalKey(key))
    key_states[PRESSED] = [ x for x in key_states[JUST_PRESSED] if x.vk != key.vk ]

def find_first_matching_key(d, attribute_name, target_value):
    for key in d.keys():
        if getattr(key, attribute_name, None) == target_value:
            return key
    return None

class GlobalKey:
    def __init__(self, obj):
        if isinstance(obj, KeyCode):
            self.vk = obj.vk
            self.name = obj.char
        elif isinstance(obj, Key):
            self.vk = -1
            self.name = obj.name
        else:
            self.vk = -1
            self.name = obj

    def __repr__(self):
        return f"GlobalKey(vk={self.vk}, name='{self.name}')"

    def __eq__(self, other):
        if isinstance(other, GlobalKey):
            return self.vk == other.vk and self.name == other.name
        return False

    def __hash__(self):
        return hash((self.vk, self.name))