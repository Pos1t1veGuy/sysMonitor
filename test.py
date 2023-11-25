import keyboard
from tkinter import Tk, Label

def on_key_event(e):
    if keyboard.is_pressed('shift+z'):
        print('shift+z pressed')

# Регистрируем обработчик событий клавиаZтуры
keyboard.hook(on_key_event)

# Создаем окно Tkinter (пример)
root = Tk()
label = Label(root, text="Hello, Tkinter!")
label.pack()

# Запускаем главный цикл Tkinter
root.mainloop()
