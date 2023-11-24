import tkinter as tk

root = tk.Tk()

# Создаем первый Label (нижний)
label1 = tk.Label(root, text="Нижний Label", bg="lightblue")
label1.place(x=50, y=50)

# Создаем второй Label (верхний)
label2 = tk.Label(root, text="Верхний Label", bg="lightgreen")
label2.place(x=50, y=40)

root.mainloop()
