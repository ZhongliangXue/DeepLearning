import tkinter as tk

window = tk.Tk()
window.title('输入文本的文本框')

#窗口的尺寸
window.geometry('600x400')

def insert_point():
    var = e.get()
    t.insert("insert",var)

def insert_end():
    var = e.get()
    t.insert('end',var)

b1 = tk.Button(window,text="insert point",width=15,height=2,command=insert_point)
b1.pack()

b2 = tk.Entry(window,show="")
b2.pack()

e = tk.Entry(window,show="*")
e.pack()

t = tk.Text(window,height=2)
t.pack()

window.mainloop()