from components import key_state_tracker, scene_manager, resources, image_drawer

KEY_MAP_DISPLAY_TABLE = [1,1,1,1,1,0,0,1]
char = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
suit = ['C', 'S', 'D', 'H']
def _start():
    for s in range(len(suit)):
        for c in range(len(char)):
            print(char[c] + suit[s])
            image_drawer.draw_bw_image(resources.stdscr, 'screen_data/drawings/' + char[c] + suit[s] + '.txt', c * 9, s * 7)
    resources.stdscr.refresh()
def _update(): pass
def _end(): pass