
from Tkinter import *

#http://www.blog.pythonlibrary.org/2012/07/26/tkinter-how-to-show-hide-a-window/


class FloatWindow():
    def __init__(self):
        self.root = Tk()
        self.root.overrideredirect(1)
        print "Window ID: ", self.get_windowid()
        
    def get_windowid(self):
        return self.root.winfo_id()
        
    def move(self, x, y, w, h):
        
        self.root.geometry('%dx%d+%d+%d' % ( w, h, x, y ))
        
        self.show()
        
    def show(self):
        self.root.deiconify()
        self.root.update()
        
    def hide(self):
        self.root.withdraw()

if __name__ == '__main__':

    win = FloatWindow()

    raw_input()
    
    win.hide()
    
    raw_input()
    
    win.show()
    
    raw_input()
    
    win.root.geometry('%dx%d+%d+%d' % ( 800, 600, 100, 100 ))
    
    raw_input()

