#!/usr/bin/python
# -*- coding: latin-1 -*-

from kivy.core.window import Window
from kivy.uix.stencilview import StencilView
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock

from kivy.animation import Animation

from kivy.properties import NumericProperty, ObjectProperty, StringProperty


from kivy.graphics import Color, Line, Rectangle

import hashlib
import os

from threading import Thread

def find_get_attr(iterable, find_attr, find_value):
    '''
    Usefull?
    '''
    for i in iterable:
        if getattr(i, find_attr) == find_value:
            return i
            
def get_max(iterable):
    '''
    Devuelve el maximo del valor entero del atrubito en un diccionario
    '''
    nmax = 0
    for i in iterable:

        '''
        if getattr(i, find_attr) == find_value:
            return i
        '''

        if nmax < iterable[i]:
            nmax = iterable[i]
    return nmax
        
def get_hash(text):
    cryptor = hashlib.sha512()
    if cryptor != None:
        cryptor.update(text)
        return cryptor.hexdigest()
        
def get_img_file(path):
    
    if os.path.isfile(os.path.join(path, 'cover_256x256.jpg')):
        return os.path.join(path, 'cover_256x256.jpg')
    elif os.path.isfile(os.path.join(path, 'cover_128x128.jpg')):
        return os.path.join(path, 'cover_128x128.jpg')
    elif os.path.isfile(os.path.join(path, 'cover.jpg')):
        return os.path.join(path, 'cover.jpg')
    
    try:
        for i in os.listdir(path):
            filename, ext = os.path.splitext(i)
            if ext.upper() in ['.JPG', '.PNG']:
                return os.path.join(path, i)
    except:
        pass
                
    return 'no_cover.png'
        
def getfullfilename(path, filename):
    '''
    Obtiene el nombre completo con extencion 
    '''
    for i in os.listdir(path):
        if filename == os.path.splitext( i )[0]:
            return i
            
    return filename
    

def timout_parent_remove(dt, widget, val):
    print (dt, widget, val)
    
    
def remove_smooth(widget):
    anim = Animation(opacity=0, duration=1)
    anim.bind(on_complete=timout_parent_remove)
    anim.start(widget)

class ngDialog(FloatLayout):
    
    content = ObjectProperty()
    title = StringProperty()
    
    def __init__(self, **kwargs):
        
        
        self.quad_separation = 4
        
        self.box = BoxLayout(orientation='vertical')
                
        if 'title' in kwargs:
            self.title = kwargs.pop('title')

        if hasattr(self, 'title') == False:
            self.title = 'No title'
            
        self.lb_title = Label(size_hint_y=None, height=50, font_size=32)
        
        self.separator = ProgressBar(value=100, max=100, size_hint_y=None, height=20)
        
        if 'content' in kwargs:
            self.content = kwargs.pop('content')
            
        
        self.box.add_widget(self.lb_title)
        self.box.add_widget(self.separator)
        
        if hasattr(self, 'content'):
            if self.content != None:
                self.box.add_widget(self.content)
        
        super(ngDialog, self).__init__(**kwargs)
        
        if 'center' in kwargs:
            self.center = kwargs.get('center')
            
        self.draw_background()
        
        self.box.size = self.size
        self.box.pos = self.pos
        
        self.add_widget(self.box)
        
        if 'center' not in kwargs and 'pos' not in kwargs:
            self.center = Window.center
        
    def on_title(self, w, val):
        self.lb_title.text = val
            
    def draw_background(self):
        if self.canvas == None:
            return
        
        self.canvas.before.clear()        

        with self.canvas.before:
            
            Color(.3, .3, .3)
            
            Rectangle(pos=self.pos, size=self.size)
            
            Color(.23, .68, .85)
            Line(rectangle=(self.x-self.quad_separation, 
                                self.y-self.quad_separation, 
                                self.width+self.quad_separation*2, 
                                self.height+self.quad_separation*2),
                cap=None,
                joint='round',
                close=True,
                width=4)
        
        
    def dismiss(self, w=None):
        if self.parent != None:
            self.parent.remove_widget(self)
            
    def open(self):
        pass
        
    
    def on_pos(self, w, val):            
        #super(ngDialog, self).on_pos(val)
        self.draw_background()
        
        if hasattr(self, 'box'):
            self.box.pos = val
            
    def on_size(self, w, val):            
        self.draw_background()
        
        if hasattr(self, 'box'):
            self.box.size = val
            
    def on_content(self, w, val):
        if self.content != None:
            self.box.remove_widget(self.content)
            
        self.box.add_widget(val)

class MessageBox(Popup):
    def __init__(self, **kwargs):
        super(MessageBox, self).__init__(**kwargs)
        lay = BoxLayout()
        
        self.btn_aceptar = Button(text='Aceptar')
        
        self.btn_cancelar = Button(text='Cancelar')
        self.btn_cancelar.bind(on_press=self.dismiss)
        
        lay.add_widget(self.btn_aceptar)
        lay.add_widget(self.btn_cancelar)
        
        self.content = lay
        
class MessageBoxTime(Popup):
    def __init__(self, **kwargs):
        
        msg = kwargs.get('msg', '')
        duration = kwargs.get('duration', 3)
        
        layout = BoxLayout(orientation='vertical')
        self.txt = Label(text=msg, size_hint_y=None, height=50)
        layout.add_widget(self.txt)
        
        super(MessageBoxTime, self).__init__(content=layout, 
                                            #size=(Window.width*.8, Window.height*.2),
                                            #size_hint=(None, None),
                                            #opacity=.6,
                                            **kwargs)
        
        if duration != -1:
            Clock.schedule_once(self.time_close, duration)
        
    def time_close(self, dt):
        self.dismiss()
        
class LabelShadow(StencilView):
    
    text = StringProperty('')
    font_size = NumericProperty(16)
    
    def __init__(self, **kwargs):
        
        self.color = kwargs.pop('shadowcolor', (0, 0, 0, 1) )
        self.shadowcolor = kwargs.pop('color', (1, 1, 1, 1) )
        self.text = kwargs.pop('text', '')
        self.font_size = kwargs.pop('font_size', 16)
        self.texthalign = kwargs.pop('texthalign', 'center')
        
        kwargs.pop('pos', '')
        kwargs.pop('color', '')
        
        self.label = Label(text=self.text, font_size=self.font_size, color=self.color, **kwargs)
        self.shadow = Label(text=self.text, font_size=self.font_size, color=self.shadowcolor, **kwargs)
        
        super(LabelShadow, self).__init__(**kwargs)
        
        
        
        
        self.add_widget(self.label)
        self.add_widget(self.shadow)
        
        #self.label.pos[0] = -1000
        
        
        if self.texthalign == 'left':
            self.label.bind(size=self.fixLabelText )
            self.shadow.bind(size=self.fixLabelText )
        
    def fixLabelText(self, w, val):
        '''
        Trickly fix for align text to left in a label
        '''
        w.text_size = val
    
    def on_text(self, w, val):
        if hasattr(self, 'label'):
            self.label.text = val
            
        if hasattr(self, 'shadow'):
            self.shadow.text = val
        
    def on_pos(self, w, val):
        if hasattr(self, 'label'):
            self.label.pos = val
            
        if hasattr(self, 'shadow'):
            self.shadow.pos = (val[0]-1, val[1]+1)
            
    def on_size(self, w, val):
        if hasattr(self, 'label'):
            self.label.size = val
            
        if hasattr(self, 'shadow'):
            self.shadow.size = val
            
    def on_font_size(self, w, val):
        if hasattr(self, 'label'):
            self.label.font_size = val
            
        if hasattr(self, 'shadow'):
            self.shadow.font_size = val
        
class LabelItem(BoxLayout):
    def __init__(self, **kwargs):
        super(LabelItem, self).__init__(**kwargs)
        self.caption = kwargs.get('caption', 'Caption')
        self.widgetposition = kwargs.get('widgetposition', 'right')
        self.texthalign = kwargs.get('texthalign', 'left')
        
        self.lb_caption = Label(text=self.caption, size_hint_x=None, width=200)
        self.item = kwargs.get('itemtype')(**kwargs.get('item_kwargs', {}))
        
        if self.widgetposition == 'right':
            self.add_widget(self.lb_caption)
            self.add_widget(self.item)
        elif self.widgetposition == 'left':
            self.add_widget(self.item)
            self.add_widget(self.lb_caption)


class st(StencilView):
    def __init__(self, **kwargs):
        super(st, self).__init__(**kwargs)
        self.add_widget(Label(text='hola') )
        
'''
Esta clase fue extraida del archivo netget.py del proyecto netget,
dicha parte del codigo es generica.
'''
class ngTextInput(TextInput):
    '''
    Derivacion de texinput para lograr la funcionalidad de la tecla
    TAB en los controles focusables.
    
    '''
    def __init__(self, **kwargs):
        
        self.register_event_type('on_enter')
        
        super(ngTextInput, self).__init__(**kwargs)
        
    #checar TAB
    def _keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[1] == 'tab':
            if self.on_tab():
                return True
                            
        elif keycode[1] == 'enter':
            #self.on_enter(self)
            self.dispatch('on_enter')
            return True
            
        super(ngTextInput, self)._keyboard_on_key_down(window, keycode, text, modifiers)

    def on_tab(self):
        if self.parent != None:
            first_focusable = None
            found = False
            for i in reversed(self.parent.children):
                if first_focusable == None and isinstance(i, (ngTextInput, TextInput, Button) ):
                    #print 'first focusable', i
                    first_focusable = i
                
                if found == False:                      
                    if i == self:
                        found = True
                        #is the last item?
                        if i == self.parent.children[0] and first_focusable != None:
                            first_focusable.focus = True
                            return True
                else:
                    if isinstance(i, (ngTextInput, TextInput, Button) ):

                        #focuse next
                        i.focus = True

                        return True  
                        
    def on_enter(self):
        pass
        
try:
    import urllib, urllib2
        
    class Request(Thread):
        def __init__(self, **kwargs):
            
            self.callback = kwargs.pop('callback')
            self.action = kwargs.pop('action')
            self.data = urllib.urlencode(kwargs.pop('data') )
            
            
            #super(Request, self).__init__(**kwargs)
            Thread.__init__(self)
            
            
            self.start()
            
        def run(self):
            '''
            br = mechanize.Browser()
            
            response = br.open(mechanize.Request(self.action,
                                        data=self.data)
                                        )
                                    
            
            res = response.read()
            
            self.callback(res)
            '''
            print "Requesting url: ", self.action
            
            req = urllib2.Request(self.action, self.data)
            response = urllib2.urlopen(req)
            self.res = response.read()
            
            #this call is for that when we call the callball, we want to make it from the main thread (the gui thread)
            Clock.schedule_once(self.real_callback, 0)
            
        def real_callback(self, dt):
            self.callback(self.res)
            
except:
    pass
    
def alert(title, msg):
    '''
    Alert function
    '''
    return Popup(title=title, content=Label(text=msg)).open()
    
def fade_in(widget, parentremove=False):
    widget.opacity = 0
    Animation(opacity=1, duration=.3).start(widget)
    
def fade_out(widget):
    widget.opacity = 1
    anim = Animation(opacity=0, duration=.3)
    anim.bind(on_complete=on_parentremove)
    anim.start(widget)
    
def on_parentremove(widget, w):
    w.parent.remove_widget(w)
    
    
class ImageButton(ButtonBehavior, Image):
    pass

if __name__ == '__main__':
    from kivy.base import runTouchApp
    
    box = BoxLayout()
    box.add_widget(ngDialog(title='uno', content=Button(text='ok')) )
    box.add_widget(ngDialog(title='dos', content=LabelShadow(text='cancel')) )
    runTouchApp(box)
    
    
    #runTouchApp(LabelShadow(text='hola') ) 
    
    
