from tkinter import Tk, Label, Canvas, Frame
from pathlib import Path

import sys, os
import psutil
import keyboard as kb

from .utils import sysInfo, Config


def hotkeys(e):
    global config, always_on_top
    if kb.is_pressed(config['hotkeys']['set_active_window']):
        always_on_top = not always_on_top
        root.wm_attributes("-topmost", always_on_top)
        if config['debug']:
            print('Pressed "set_active_window" hotkey')

    elif kb.is_pressed(config['hotkeys']['close_window']):
        root.destroy()
        sys.exit()

kb.hook(hotkeys)


def toWidth(x: int) -> int:
    return x*config['window']['size'][0]/125

def default_label(text: str = 'label', color: str = 'white'):
    global config
    label = Label(root, text=text, fg=color, font=("Helvetica Bold", 12, "bold"))
    label.configure(background=config['window']['background_color'])
    label.pack(side="top", anchor="w")
    return label


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

def th_hotkeys(event):
    global config
    if button_pressed and event.keysym == config['window']['close_key']:
        root.destroy()
    elif button_pressed and event.keysym == config['window']['restart_key']:
        sys.exit(os.execl(sys.executable, sys.executable, *sys.argv))
    elif event.keysym == config['window']['to_start_position_key']:
        root.geometry(f"+{config['window']['position'][0]}+{config['window']['position'][1]}")
    elif button_pressed and event.keysym == config['window']['save_pos_key']:
        save_coordinates(True)

def save_coordinates(event):
    global config, _offsetx, _offsety, last_pos, last_saved_pos

    if config['window']['auto_save_pos'] or event == True:
        _offsetx = root.winfo_pointerx() - root.winfo_rootx() 
        _offsety = root.winfo_pointery() - root.winfo_rooty()

        if last_saved_pos != [root.winfo_rootx(), root.winfo_rooty()]:
            config.change(window__position=[root.winfo_rootx(), root.winfo_rooty()])
            last_saved_pos = [root.winfo_rootx(), root.winfo_rooty()]

    if config['debug'] and last_pos != [root.winfo_rootx(), root.winfo_rooty()]:
        print(f'Moved to {[root.winfo_rootx(), root.winfo_rooty()]}')

    last_pos = [root.winfo_rootx(), root.winfo_rooty()]

def update_graph(canvas, percentage, color, y_position, height):
    width = int(( root.winfo_width() - toWidth(3) ) * percentage / 100)
    canvas.create_rectangle(0, y_position, width, y_position + height, fill=color)

def update_canvas(canvas, cfg: dict):
    canvas.config(
        background=config['window']['background_color'],
        highlightbackground=cfg['graph']['border_color'],
        highlightthickness=cfg['graph']['border_width']
    )


def update_window():
    global config, always_on_top
    cfg = config.data['window']

    root.geometry(f"{cfg['size'][0]}x{cfg['size'][1]}")

    if cfg['always_on_top']:
        root.wm_attributes("-topmost", 1)
        always_on_top = True

    root.attributes('-alpha', cfg['transparency'])
    root.configure(background=cfg['background_color'])
    root.wm_attributes("-transparentcolor", cfg['background_color'])
    root.overrideredirect(not cfg['show_frame'])

    root.after(cfg['update_rate'], update_upline)


def update_upline():
    global config
    cfg = config.data['up_line']

    upline.config(height=cfg['height'], background=cfg['color'])

    root.after(cfg['update_rate'], update_upline)

def update_cpu():
    global config
    cfg = config.data['CPU']
    cpu_percentage = psutil.cpu_percent()

    if cfg['text']['show']:
        show = f"{cpu_percentage:.2f}" if cpu_percentage < 10 else f"{cpu_percentage:.1f}"
        cpu_label.config(text=f"{cfg['text']['label']}{show if cpu_percentage < 100 else 99.9}%", fg=cfg['text']['color'])
    if cfg['graph']['show']:
        cpu_canvas.delete("all")
        update_graph(cpu_canvas, cpu_percentage, cfg['graph']['color'], 0, cfg['graph']['height'])
        update_canvas(cpu_canvas, cfg)

    root.after(cfg['update_rate'], update_cpu)

def update_ram():
    global config
    cfg = config.data['RAM']
    ram_percentage = psutil.virtual_memory().percent

    if cfg['text']['show']:
        show = f"{ram_percentage:.2f}" if ram_percentage < 10 else f"{ram_percentage:.1f}"
        ram_label.config(text=f"{cfg['text']['label']}{show if ram_percentage < 100 else 99.9}%", fg=cfg['text']['color'])
    if cfg['graph']['show']:
        ram_canvas.delete("all")
        update_graph(ram_canvas, ram_percentage, cfg['graph']['color'], 0, cfg['graph']['height'])
        update_canvas(ram_canvas, cfg)

    root.after(cfg['update_rate'], update_ram)

def update_disks():
    global config
    cfg = config.data['disks']
    disk_info = sysInfo.get_disks()

    for i, disk in enumerate(disk_info):
        used = (disk['total'] - disk['free'])// (1024 ** 3)
        total = disk['total'] // (1024 ** 3)

        if cfg['text']['show']:
            disk_labels[i].config(text=f"{disk['root']}\\ {used} / {total} GB")

        if cfg['graph']['show']:
            disk_canvases[i].delete("all")
            update_graph(disk_canvases[i], used/total*100, cfg['graph']['color'], 0, cfg['graph']['height'])
            update_canvas(disk_canvases[i], cfg)

    root.after(cfg['update_rate'], update_disks)

def update_lip():
    global config
    cfg = config.data['local_IP']

    if cfg['show']:
        locip_label.config(text=f"    {sysInfo.get_local_ip()}", fg=cfg['color'])

    root.after(cfg['update_rate'], update_lip)

def update_eip():
    global config
    cfg = config.data['external_IP']

    if cfg['show']:
        extip_label.config(text=f"    {sysInfo.get_external_ip()}", fg=cfg['color'])

    root.after(cfg['update_rate'], update_eip)

def update_tcp():
    global config
    cfg = config.data['TCP']

    if cfg['show']:
        tcp_label.config(text=f"{cfg['label']}{sysInfo.get_tcp_connections()} conns", fg=cfg['color'])

    root.after(cfg['update_rate'], update_tcp)

def update_udp():
    global config
    cfg = config.data['UDP']

    if cfg['show']:
        udp_label.config(text=f"{cfg['label']}{sysInfo.get_udp_connections()} conns", fg=cfg['color'])

    root.after(cfg['update_rate'], update_udp)


roaming_path = Path.home() / "AppData" / "Roaming"
app_dir = roaming_path / "sysMonitor"

if not os.path.isdir(app_dir):
    os.mkdir(app_dir)


config = Config(app_dir / "monitor_config.json", default={
    'debug': True,

    'hotkeys': {
        'set_active_window': 'f2',
        'close_window': 'f3',
    },

    'window': {
        'update_rate': 1000,
        'position': [0, 0],
        'size': [130, 300],

        'auto_save_pos': False,
        'always_on_top': False,
        'transparency': 0.8,
        'background_color': 'green',

        'mouse_button': 2,
        'close_key': 'Escape',
        'restart_key': 'Tab',
        'save_pos_key': 'space',
        'to_start_position_key': '1',

        'show_frame': False,
    },

    'up_line': {
        'color': 'white',
        'height': 7,
        'update_rate': 500,
    },

    'CPU': {
        'update_rate': 300,
        'graph': {
            'height': 16,
            'color': "gray",
            'border_width': 2,
            'border_color': "white",
            'show': True,
        },
        'text': {
            'show': True,
            'color': "white",
            'label': "CPU: ",
        },
    },
    'RAM': {
        'update_rate': 300,
        'graph': {
            'height': 16,
            'color': "gray",
            'border_width': 2,
            'border_color': "white",
            'show': True,
        },
        'text': {
            'show': True,
            'color': "white",
            'label': "RAM: ",
        },
    },
    'disks': {
        'update_rate': 3000,
        'graph': {
            'height': 5,
            'color': "yellow",
            'border_width': 2,
            'border_color': "white",
            'show': True,
        },
        'text': {
            'show': True,
            'color': "white",
        },
    },
    'local_IP': {
        'update_rate': 5000,
        'show': True,
        'color': "white",
        'label': "Local IP:",
    },
    'external_IP': {
        'update_rate': 5000,
        'show': True,
        'color': "white",
        'label': "External IP:",
    },
    'TCP': {
        'update_rate': 5000,
        'show': True,
        'color': "white",
        'label': "TCP: ",
    },
    'UDP': {
        'update_rate': 5000,
        'show': True,
        'color': "white",
        'label': "UDP: ",
    }
})

root = Tk()
try:
    root.geometry(f"+{config['window']['position'][0]}+{config['window']['position'][1]}")


    upline = Frame(root, height=config['up_line']['height'], background=config['up_line']['color'])
    upline.pack(fill="x")


    if config['CPU']['text']['show']:
        cpu_label = default_label("CPU load", config['CPU']['text']['color'])
        cpu_canvas = Canvas(root, width=root.winfo_width()+toWidth(120),
            height=config['CPU']['graph']['height']-2,
            background=config['window']['background_color'],
            highlightbackground=config['CPU']['graph']['border_color'],
            highlightthickness=config['CPU']['graph']['border_width'])
        cpu_canvas.pack(side="top", anchor="w")
    if config['CPU']['graph']['show']:
        update_graph(cpu_canvas, 50, config['CPU']['graph']['color'], 0, 19)

    if config['RAM']['text']['show']:
        ram_label = default_label("RAM load", config['RAM']['text']['color'])
        ram_canvas = Canvas(root, width=root.winfo_width()+toWidth(120),
            height=config['RAM']['graph']['height']-2,
            background=config['window']['background_color'],
            highlightbackground=config['RAM']['graph']['border_color'],
            highlightthickness=config['RAM']['graph']['border_width'])
        ram_canvas.pack(side="top", anchor="w")
    if config['RAM']['graph']['show']:
        update_graph(ram_canvas, 50, config['RAM']['graph']['color'], 0, 19)

    disk_labels = []
    disk_canvases = []
    for i in range(len(sysInfo.get_disks())):
        if config['disks']['text']['show']:
            disk_labels.append( default_label("disk") )

        if config['disks']['graph']['show']:
            disk_canvas = Canvas(root, width=root.winfo_width()+toWidth(120),
                height=config['disks']['graph']['height']-2,
                background=config['window']['background_color'],
                highlightbackground=config['disks']['graph']['border_color'],
                highlightthickness=config['disks']['graph']['border_width'])
            disk_canvas.pack(side="top", anchor="w")
            disk_canvases.append(disk_canvas)

    if config['local_IP']['show']:
        locip = default_label(config['local_IP']['label'], config['local_IP']['color'])
        locip_label = default_label(f"    {config['local_IP']['show']}")

    if config['external_IP']['show']:
        extip = default_label(config['external_IP']['label'], config['external_IP']['color'])
        extip_label = default_label(f"    {config['external_IP']['show']}")

    if config['TCP']['show']:
        tcp_label = default_label("TCP ports", config['TCP']['color'])
    if config['UDP']['show']:
        udp_label = default_label("UDP ports", config['UDP']['color'])


    always_on_top = False
    button_pressed = False

    last_pos = config['window']['position']
    last_saved_pos = config['window']['position']

    if config['debug']:
        print(f"Initialized at {config['window']['position']} with size {config['window']['size']}")

    root.bind(f"<Button-{config['window']['mouse_button']}>", clickwin)
    root.bind(f"<B{config['window']['mouse_button']}-Motion>", dragwin)
    root.bind(f"<ButtonRelease-{config['window']['mouse_button']}>", save_coordinates)

except KeyError as key:
    print(f'Invalid config, {key} key is missing. Config will sets to default if user delete it by path: "{config.file}"')
    exit()

root.bind("<Key>", th_hotkeys)


update_window()

update_upline()
update_ram()
update_cpu()
update_disks()
update_lip()
update_eip()
update_tcp()
update_udp()


try:
    root.mainloop()
except KeyboardInterrupt:
    print('Stopped by user')