from tkinter import Tk, Label, Canvas, Frame
import sys, os
import psutil
import keyboard as kb

from utils import sysInfo, Config


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
    return x*config['size'][0]/125

def default_label(text: str = 'label'):
    global config
    label = Label(root, text=text, fg=config['text_color'], font=("Helvetica Bold", 12, "bold"))
    label.configure(background="black")
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
    if button_pressed and event.keysym == 'Escape':
        root.destroy()
    elif button_pressed and event.keysym == 'Tab':
        sys.exit(os.execl(sys.executable, sys.executable, *sys.argv))
    elif button_pressed and event.keysym == 'space':
        save_coordinates(True)

def save_coordinates(event):
    global config, _offsetx, _offsety, last_pos, last_saved_pos

    if config['auto_save_pos'] or event == True:
        _offsetx = root.winfo_pointerx() - root.winfo_rootx() 
        _offsety = root.winfo_pointery() - root.winfo_rooty()

        if last_saved_pos != [root.winfo_rootx(), root.winfo_rooty()]:
            config.change(position=[root.winfo_rootx(), root.winfo_rooty()])
            last_saved_pos = [root.winfo_rootx(), root.winfo_rooty()]

    if config['debug'] and last_pos != [root.winfo_rootx(), root.winfo_rooty()]:
        print(f'Moved to {[root.winfo_rootx(), root.winfo_rooty()]}')

    last_pos = [root.winfo_rootx(), root.winfo_rooty()]

def create_graph(canvas, percentage, color, y_position, height):
    width = int(( root.winfo_width() - toWidth(3) ) * percentage / 100)
    canvas.create_rectangle(0, y_position, width, y_position + height, fill=color, outline="")


def update_cpu(config: dict):
    cpu_percentage = psutil.cpu_percent()

    show = f"{cpu_percentage:.2f}" if cpu_percentage < 10 else f"{cpu_percentage:.1f}"
    cpu_label.config(text=f"CPU: {show if cpu_percentage < 100 else 99.9}%")
    cpu_canvas.delete("all")
    if config['graph_show']:
        create_graph(cpu_canvas, cpu_percentage, config['graph_color'], 0, config['graph_height'])

    cpu_start = False
    root.after(config['update_rate'] if not cpu_start else 10, update_cpu, config)

def update_ram(config: dict):
    ram_percentage = psutil.virtual_memory().percent

    show = f"{ram_percentage:.2f}" if ram_percentage < 10 else f"{ram_percentage:.1f}"
    ram_label.config(text=f"RAM: {show if ram_percentage < 100 else 99.9}%")
    ram_canvas.delete("all")
    if config['graph_show']:
        create_graph(ram_canvas, ram_percentage, config['graph_color'], 0, config['graph_height'])

    ram_start = False
    root.after(config['update_rate'] if not ram_start else 10, update_ram, config)

def update_disks(config: dict):
    disk_info = sysInfo.get_disks()

    for i, disk in enumerate(disk_info):
        used = (disk['total'] - disk['free'])// (1024 ** 3)
        total = disk['total'] // (1024 ** 3)

        disk_labels[i].config(text=f"{disk['root']}\\ {used} / {total} GB")
        disk_canvases[i].delete("all")

        if config['graph_show']:
            create_graph(disk_canvases[i], used/total*100, config['graph_color'], 0, config['graph_height'])

    disks_start = False
    root.after(config['update_rate'] if not disks_start else 10, update_disks, config)

def update_nets(config: dict):
    if config['show_local_IP']:
        locip_label.config(text=f"    {sysInfo.get_local_ip()}")
    if config['show_external_IP']:
        extip_label.config(text=f"    {sysInfo.get_external_ip()}")

    if config['show_tcp_connections']:
        tcp_label.config(text=f"TCP: {sysInfo.get_tcp_connections()} conns")
    if config['show_udp_connections']:
        udp_label.config(text=f"UDP: {sysInfo.get_udp_connections()} conns")

    nets_start = False
    root.after(config['update_rate'] if not nets_start else 10, update_nets, config)


root = Tk()
root.overrideredirect(1)
root.configure(background="black")
root.wm_attributes("-transparentcolor", "black")


config = Config("config.json", default={
    'debug': True,
    'auto_save_pos': False,
    'always_on_top': False,
    'transparency': 0.8,

    'position': [1213, 306],
    'size': [130, 300],
    'text_color': 'white',

    'up_line_color': 'white',
    'up_line_height': 7,

    'hotkeys': {
        'set_active_window': 'f2',
        'close_window': 'f3',
    },

    'mouse_button': 2,
    'close_key': 'Escape',
    'restart_key': 'Tab',
    'save_pos_key': 'space',

    'CPU': {
        'update_rate': 300,
        'graph_height': 16,
        'graph_color': "gray",
        'graph_show': True,
        'text_show': True,
    },
    'RAM': {
        'update_rate': 300,
        'graph_height': 16,
        'graph_color': "gray",
        'graph_show': True,
        'text_show': True,
    },
    'disks': {
        'update_rate': 3000,
        'graph_height': 5,
        'graph_color': "yellow",
        'graph_show': True,
        'text_show': True,
    },
    'nets': {
        'update_rate': 5000,
        'show_local_IP': True,
        'show_external_IP': True,
        'show_tcp_connections': True,
        'show_udp_connections': True,
    },
})


Frame(root, height=config['up_line_height'], background=config['up_line_color']).pack(fill="x")


if config['CPU']['text_show']:
    cpu_label = default_label("CPU load")
    cpu_canvas = Canvas(root, width=root.winfo_width()+toWidth(120), height=config['RAM']['graph_height']-2, background="black")
    cpu_canvas.pack(side="top", anchor="w")
if config['CPU']['graph_show']:
    create_graph(cpu_canvas, 50, "white", 0, 19)

if config['RAM']['text_show']:
    ram_label = default_label("RAM load")
    ram_canvas = Canvas(root, width=root.winfo_width()+toWidth(120), height=config['RAM']['graph_height']-2, background="black")
    ram_canvas.pack(side="top", anchor="w")
if config['RAM']['graph_show']:
    create_graph(ram_canvas, 50, "white", 0, 19)

disk_labels = []
disk_canvases = []
for i in range(len(sysInfo.get_disks())):
    if config['disks']['text_show']:
        disk_labels.append( default_label("disk") )

    if config['disks']['graph_show']:
        disk_canvas = Canvas(root, width=root.winfo_width()+toWidth(120), height=config['disks']['graph_height']-2, background="black")
        disk_canvas.pack(side="top", anchor="w")
        disk_canvases.append(disk_canvas)

if config['nets']['show_local_IP']:
    locip = default_label("locIP:")
    locip_label = default_label("    local IP")

if config['nets']['show_external_IP']:
    extip = default_label("extIP:")
    extip_label = default_label("    external IP")

if config['nets']['show_tcp_connections']:
    tcp_label = default_label("TCP ports")
if config['nets']['show_udp_connections']:
    udp_label = default_label("UDP ports")


always_on_top = False
button_pressed = False

last_pos = config['position']
last_saved_pos = config['position']

cpu_start = True
ram_start = True
disks_start = True
nets_start = True

if config['debug']:
    print(f"Initialized at {config['position']} with size {config['size']}")

if config['always_on_top']:
    root.wm_attributes("-topmost", 1)
    always_on_top = True

root.attributes('-alpha', config['transparency'])


root.geometry(f"{config['size'][0]}x{config['size'][1]}")
root.geometry(f"+{config['position'][0]}+{config['position'][1]}")

root.bind(f'<Button-{config["mouse_button"]}>', clickwin)
root.bind(f'<B{config["mouse_button"]}-Motion>', dragwin)
root.bind(f'<ButtonRelease-{config["mouse_button"]}>', save_coordinates)

root.bind(f'<{config["close_key"]}>', th_hotkeys)
root.bind(f'<{config["restart_key"]}>', th_hotkeys)

root.bind(f'<{config["save_pos_key"]}>', th_hotkeys)


update_ram(config['RAM'])
update_cpu(config['CPU'])
update_disks(config['disks'])
update_nets(config['nets'])


root.mainloop()