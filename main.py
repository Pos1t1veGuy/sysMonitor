from tkinter import Tk, Label, Canvas
from random import randint

import sys, os
import json
import subprocess as sb
import psutil


def get_disks():
    partitions = psutil.disk_partitions()
    disk_info = []

    for partition in partitions:
        usage = psutil.disk_usage(partition.mountpoint)
        disk_info.append({
            'root': partition.device,
            'total': usage.total,
            'free': usage.free
        })

    return disk_info

def get_ram():
    global x1, xr1
    if x1 >= 100:
        xr1 = False
    elif x1 <= 0:
        xr1 = True
    if xr1:
        x1+=1
    else:
        x1-=1
    return x1
    #return randint(0,100)

def get_cpu():
    global x2, xr2
    if x2 >= 100:
        xr2 = False
    elif x2 <= 0:
        xr2 = True
    if xr2:
        x2+=1
    else:
        x2-=1
    return x2
    #return randint(0,100)

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
    if button_pressed and event.keysym == 'space':
        save_coordinates(True)

def save_coordinates(event):
    global config, _offsetx, _offsety, last_pos
    if read_config()['save_pos'] or event == True:
        _offsetx = root.winfo_pointerx() - root.winfo_rootx() 
        _offsety = root.winfo_pointery() - root.winfo_rooty()

        if last_pos != [root.winfo_rootx(), root.winfo_rooty()]:
            change_config(position=[root.winfo_rootx(), root.winfo_rooty()])
            if debug:
                print(f'Moved to {[root.winfo_rootx(), root.winfo_rooty()]} and saved to config')
    else:
        if debug and last_pos != [root.winfo_rootx(), root.winfo_rooty()]:
            print(f'Moved to {[root.winfo_rootx(), root.winfo_rooty()]}')
    last_pos = [root.winfo_rootx(), root.winfo_rooty()]

def create_graph(canvas, percentage, color, y_position, height):
    width = int((root.winfo_width()-99) * percentage / 100)
    canvas.create_rectangle(0, y_position, width, y_position + height, fill=color, outline="")

def update_cpuram():
    ram_percentage = get_ram()
    cpu_percentage = get_cpu()

    ram_label.config(text=f"RAM: {ram_percentage}%")
    cpu_label.config(text=f"CPU: {cpu_percentage}%")

    ram_canvas.delete("all")
    create_graph(ram_canvas, ram_percentage, "gray", 0, 16)

    cpu_canvas.delete("all")
    create_graph(cpu_canvas, cpu_percentage, "gray", 0, 16)

    root.after(100, update_cpuram)

def update_disks():
    disk_info = get_disks()

    for i, disk in enumerate(disk_info):
        used = (disk['total'] - disk['free'])// (1024 ** 3)
        total = disk['total'] // (1024 ** 3)

        disk_labels[i].config(text=f"{disk['root']}\\ {used} / {total} GB")

        disk_canvases[i].delete("all")
        create_graph(disk_canvases[i], used/total*100, "yellow", 0, 5)

    root.after(1000, update_disks)

def update_nets():
    disk_info = get_disks()

    for i, disk in enumerate(disk_info):
        used = (disk['total'] - disk['free'])// (1024 ** 3)
        total = disk['total'] // (1024 ** 3)

        disk_labels[i].config(text=f"{disk['root']}\\ {used} / {total} GB")

        disk_canvases[i].delete("all")
        create_graph(disk_canvases[i], used/total*100, "yellow", 0, 5)

    root.after(1000, update_nets)


root = Tk()
root.overrideredirect(1)
root.attributes("-topmost", True)
root.configure(background="black")
#root.attributes('-alpha', 0.4)
root.wm_attributes("-transparentcolor", "black")
root.wm_attributes("-topmost", 1)


ram_label = Label(root, text="RAM: x/x 100%", fg="white", font=("Helvetica Bold", 12, "bold"))
ram_label.configure(background="black")
ram_label.pack(side="top", anchor="w")

ram_canvas = Canvas(root, width=root.winfo_width()+120, height=14, background="black")
ram_canvas.pack(side="top", anchor="w")

create_graph(ram_canvas, 50, "white", 0, 19)

cpu_label = Label(root, text="CPU: 100%", fg="white", font=("Helvetica Bold", 12, "bold"))
cpu_label.configure(background="black")
cpu_label.pack(side="top", anchor="w")

cpu_canvas = Canvas(root, width=root.winfo_width()+120, height=14, background="black")
cpu_canvas.pack(side="top", anchor="w")

create_graph(cpu_canvas, 80, "white", 0, 19)


disk_labels = []
disk_canvases = []

for i in range(len(psutil.disk_partitions())):
    disk_label = Label(root, text="", fg="white", font=("Helvetica Bold", 12, "bold"))
    disk_label.configure(background="black")
    disk_label.pack(side="top", anchor="w")
    disk_labels.append(disk_label)

    disk_canvas = Canvas(root, width=root.winfo_width()+120, height=3, background="black")
    disk_canvas.pack(side="top", anchor="w")
    disk_canvases.append(disk_canvas)

locip = Label(root, text="locIP:", fg="white", font=("Helvetica Bold", 12, "bold"))
locip.configure(background="black")
locip.pack(side="top", anchor="w")
locip_label = Label(root, text="    192.186.xx.xx", fg="white", font=("Helvetica Bold", 12, "bold"))
locip_label.configure(background="black")
locip_label.pack(side="top", anchor="w")

extip = Label(root, text="extIP:", fg="white", font=("Helvetica Bold", 12, "bold"))
extip.configure(background="black")
extip.pack(side="top", anchor="w")
extip_label = Label(root, text="    xx.xx.xx.xx", fg="white", font=("Helvetica Bold", 12, "bold"))
extip_label.configure(background="black")
extip_label.pack(side="top", anchor="w")

tcp_label = Label(root, text="TCP: xxx conns", fg="white", font=("Helvetica Bold", 12, "bold"))
tcp_label.configure(background="black")
tcp_label.pack(side="top", anchor="w")

udp_label = Label(root, text="UDP: xxx conns", fg="white", font=("Helvetica Bold", 12, "bold"))
udp_label.configure(background="black")
udp_label.pack(side="top", anchor="w")


config = "config.json"
main_cfg = {
    'position': [0,0],
    'size': "220x280",
    'save_pos': True
}
debug = True

x2, xr2 = 0, True
x1, xr1 = 0, True
button_pressed = False

init_config()
cfg = read_config()
last_pos = cfg['position']

root.geometry(cfg['size'])
root.geometry(f"+{cfg['position'][0]}+{cfg['position'][1]}")

if debug:
    print(f"Initialized at {cfg['position']} with size {cfg['size']}")

root.bind('<Button-2>', clickwin)
root.bind('<B2-Motion>', dragwin)
root.bind('<ButtonRelease-2>', save_coordinates)

root.bind('<Escape>', hotkeys)
root.bind('<Tab>', hotkeys)
root.bind('<space>', hotkeys)

update_cpuram()
update_disks()
update_nets()

root.mainloop()