# stub
from Tkinter import *
from tkSimpleDialog import *

def MyDialog(Prompt = '', defValue = 'Adapt'):
    top = Tk()
    top.update()

    A = askstring('',Prompt,
                  parent=top,initialvalue=defValue)

    top.destroy()
    return A

if __name__=="__main__":
    d = MyDialog()
    print d