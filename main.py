from tkinter import Tk
import sys, os
import json
import subprocess as sb

def init_config():
    global config, debug, root, main_cfg

    if os.path.isfile(config):
        for key in main_cfg.keys():
            if not key in read_config().keys():
                change_config(**main_cfg)

                if debug:
                    print(f"Initialized base config")
                break
    else:
        change_config(position=[0,0], size='100x120')
def change_config(**kwargs):
    global config
    if os.path.isfile(config):
        content = json.load(open(config, 'r'))
    else:
        content = {}

    for key, value in kwargs.items():
        content[key] = value

    json.dump(content, open(config, 'w'))
def read_config():
    global config
    return json.load(open(config, 'r'))

def dragwin(event):
    x = root.winfo_pointerx() - _offsetx
    y = root.winfo_pointery() - _offsety
    root.geometry(f"+{x}+{y}")

def clickwin(event):
    global _offsetx, _offsety, button_pressed
    _offsetx = event.x
    _offsety = event.y
    button_pressed = True

def releasewin(event):
    global button_pressed
    button_pressed = False

def hotkeys(event):
    if button_pressed and event.keysym == 'Escape':
        root.destroy()
    if button_pressed and event.keysym == 'Tab':
        sys.exit(os.execl(sys.executable, sys.executable, *sys.argv))

def save_coordinates(event):
    global config, _offsetx, _offsety
    if read_config()['save_pos']:
        _offsetx = root.winfo_pointerx() - root.winfo_rootx()
        _offsety = root.winfo_pointery() - root.winfo_rooty()

        change_config(position=[root.winfo_rootx(), root.winfo_rooty()])
        if debug:
            print(f'Moved to {[root.winfo_rootx(), root.winfo_rooty()]} and saved to config')
    else:
        if debug:
            print(f'Moved to {[root.winfo_rootx(), root.winfo_rooty()]} and is not saved to config')

root = Tk()
root.overrideredirect(1)
root.attributes("-topmost", True)
root.configure(background="black")
root.attributes('-alpha', 0.7)

config = "config.json"
main_cfg = {
    'position': [1124, 302],
    'size': "220x280",
    'save_pos': True
}
debug = True

button_pressed = False

init_config()
cfg = read_config()

root.geometry(cfg['size'])
root.geometry(f"+{cfg['position'][0]}+{cfg['position'][1]}")

if debug:
    print(f"Initialized at {cfg['position']} with size {cfg['size']}")

root.bind('<Button-2>', clickwin)
root.bind('<B2-Motion>', dragwin)
root.bind('<ButtonRelease-2>', save_coordinates)

root.bind('<Escape>', hotkeys)
root.bind('<Tab>', hotkeys)

root.mainloop()