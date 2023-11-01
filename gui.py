from tkinter import *
from tkinter import ttk
from monsters import monsters


def onClick():
    monsterInfo.set(monsters[int(id.get())])


root = Tk()
root.title("Gui for monsters")
id = StringVar()
monsterInfo = StringVar(root, "no selected")
frm = ttk.Frame(root, padding=10)
frm.grid()
ttk.Label(frm, textvariable=monsterInfo).grid(column=0, row=0)
ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
ttk.Entry(frm, textvariable=id).grid(column=0, row=1)
ttk.Button(frm, text="Monster", command=onClick).grid(column=1, row=1)
root.mainloop()
