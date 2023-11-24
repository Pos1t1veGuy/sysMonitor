from tkinter import Tk, Label, Canvas, Frame
import sys, os
from utils import sysInfo, Config


def default_label(text: str = 'label'):
    label = Label(root, text=text, fg="white", font=("Helvetica Bold", 12, "bold"))
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

def hotkeys(event):
    global debug
    if button_pressed and event.keysym == 'Escape':
        root.destroy()
    elif button_pressed and event.keysym == 'Tab':
        sys.exit(os.execl(sys.executable, sys.executable, *sys.argv))
    elif button_pressed and event.keysym == 'space':
        save_coordinates(True)

def save_coordinates(event):
    global config, _offsetx, _offsety, last_pos, last_saved_pos

    if config['save_pos'] or event == True:
        _offsetx = root.winfo_pointerx() - root.winfo_rootx() 
        _offsety = root.winfo_pointery() - root.winfo_rooty()

        if last_saved_pos != [root.winfo_rootx(), root.winfo_rooty()]:
            config.change(position=[root.winfo_rootx(), root.winfo_rooty()])
            last_saved_pos = [root.winfo_rootx(), root.winfo_rooty()]

    if debug and last_pos != [root.winfo_rootx(), root.winfo_rooty()]:
        print(f'Moved to {[root.winfo_rootx(), root.winfo_rooty()]}')

    last_pos = [root.winfo_rootx(), root.winfo_rooty()]

def create_graph(canvas, percentage, color, y_position, height):
    width = int((root.winfo_width()-99) * percentage / 100)
    canvas.create_rectangle(0, y_position, width, y_position + height, fill=color, outline="")


def update_cpuram():
    ram_percentage = info.get_ram()
    cpu_percentage = info.get_cpu()

    ram_label.config(text=f"RAM: {ram_percentage}%")
    cpu_label.config(text=f"CPU: {cpu_percentage}%")

    ram_canvas.delete("all")
    create_graph(ram_canvas, ram_percentage, "gray", 0, 16)

    cpu_canvas.delete("all")
    create_graph(cpu_canvas, cpu_percentage, "gray", 0, 16)

    root.after(info.cpuram_update_rate, update_cpuram)

def update_disks():
    disk_info = info.get_disks()

    for i, disk in enumerate(disk_info):
        used = (disk['total'] - disk['free'])// (1024 ** 3)
        total = disk['total'] // (1024 ** 3)

        disk_labels[i].config(text=f"{disk['root']}\\ {used} / {total} GB")

        disk_canvases[i].delete("all")
        create_graph(disk_canvases[i], used/total*100, "yellow", 0, 5)

    root.after(info.disks_update_rate, update_disks)

def update_nets():
    locip_label.config(text=f"    {info.get_local_ip()}")
    extip_label.config(text=f"    {info.get_external_ip()}")

    tcp_label.config(text=f"TCP: {info.get_tcp_connections()} conns")
    udp_label.config(text=f"UDP: {info.get_udp_connections()} conns")

    root.after(info.nets_update_rate, update_nets)


root = Tk()
root.overrideredirect(1)
root.attributes("-topmost", True)
root.configure(background="black")
#root.attributes('-alpha', 0.4)
root.wm_attributes("-transparentcolor", "black")
root.wm_attributes("-topmost", 1)

back_frame = Frame(root)
back_frame.pack(side="bottom", fill="both", expand=True)

label = Label(back_frame, text="TEXT")
label.place(x=0, y=0)


info = sysInfo()
config = Config("config.json", default={
    'position': [0,0],
    'size': "220x280",
    'save_pos': True
}, debug=True)


ram_label = default_label("RAM load percentage")
ram_canvas = Canvas(root, width=root.winfo_width()+120, height=14, background="black")
ram_canvas.pack(side="top", anchor="w")
create_graph(ram_canvas, 50, "white", 0, 19)

cpu_label = default_label("CPU load percentage")
cpu_canvas = Canvas(root, width=root.winfo_width()+120, height=14, background="black")
cpu_canvas.pack(side="top", anchor="w")
create_graph(cpu_canvas, 50, "white", 0, 19)

disk_labels = []
disk_canvases = []
for i in range(len(info.get_disks())):
    disk_labels.append( default_label("disk") )
    disk_canvas = Canvas(root, width=root.winfo_width()+120, height=3, background="black")
    disk_canvas.pack(side="top", anchor="w")
    disk_canvases.append(disk_canvas)

locip = default_label("locIP:")
locip_label = default_label("    local IP")

extip = default_label("extIP:")
extip_label = default_label("    external IP")

tcp_label = default_label("TCP ports")
udp_label = default_label("UDP ports")


debug = True

x2, xr2 = 0, True
x1, xr1 = 0, True
button_pressed = False

last_pos = config['position']
last_saved_pos = config['position']

if debug:
    print(f"Initialized at {config['position']} with size {config['size']}")


root.geometry(config['size'])
root.geometry(f"+{config['position'][0]}+{config['position'][1]}")

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