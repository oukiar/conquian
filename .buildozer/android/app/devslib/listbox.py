#!/usr/bin/python
# -*- coding: latin-1 -*-

'''
IMPORTANT: Now the code only is stable with orientation='vertical'

horizontal orientation can be broke

'''

import kivy

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock

from listbase import ListBase

from kivy.graphics import Color
from kivy.graphics.vertex_instructions import Line, BorderImage, Rectangle


#Default selector
class Selector(Widget):
    '''
    Most basic selector
    '''
    def __init__(self, **kwargs):
        super(Selector, self).__init__(size_hint=(None,None), **kwargs)

                    
    def on_pos(self, wid, val):
        self.update_canvas()
                
    def on_size(self, wid, val):
        self.update_canvas()
                
    def update_canvas(self):
        if self.canvas == None:
            return
                
        self.canvas.clear()
        
        with self.canvas:
            Color(1,0,0)
            Line(rectangle=(self.x, self.y, self.width, self.height),
                cap=None,
                joint='round',
                close=True,
                width=2)
                
    def fade_in(self, duration):
        pass
        
    def fade_out(self, duration):
        pass
        
class ListItem(BoxLayout):
    
    def on_unselected(self):
        pass
        
    def on_selected(self):
        pass

class ListBox(ListBase):
    
    '''
    Generic Listbox with items of the same widget class
    
    The class widget_cls must have a __init__ without dependencies
    of kwargs (must have void defaults) and must inititalize correctly.
    
    '''
    
    def __init__(self, **kwargs):
        
        super(ListBox, self).__init__(**kwargs)
        
        self.orientation = kwargs.get('orientation', 'vertical')
        self.transition_duration = kwargs.get('transition_duration', 0.1)
        self.overflow_duration = kwargs.get('overflow_duration', 0.3)
        self.spacing = kwargs.get('spacing', 0)
        self.updown_sync = kwargs.get('updown_sync', False)
        
        
        if self.updown_sync:
            self.downkey = kwargs.get('downkey', False)
            self.upkey = kwargs.get('upkey', False)
        
        self.calc_size_and_positions()
            
        self.frontal_items = []
        self.create_gui()
        self.set_positions()

        #selector
        self.selector = kwargs.get('selector', Selector(size=self.child_size))
       
        if self.selector != None:
            self.add_widget(self.selector, len(self.children))
            self.selector.size = self.child_size
            
            self.fix_selector_pos()
        
        self.update()
            
        #fix for continuous movement without complications
        self.moving = False
        
        #bandera que indica si debemos esperar a que se levante la tecla 'arriba', para no hacer overflow en lista tracklist
        self.waitingdownarrow = True
        self.candownarrow = False
        
        self.waitinguparrow = True
        self.canuparrow = False
        
        
        #self.bind(pos=self.pos_and_size_change)
        #self.bind(size=self.pos_and_size_change)
        
    def on_touch_down(self, touch):

        if hasattr(touch, 'button'):
                        
            if touch.button == 'scrolldown':
                self.move(-1)
            elif touch.button == 'scrollup':
                self.move(1)
                
        super(ListBox, self).on_touch_down(touch)
        
        
    def add_item(self, **kwargs):
        self.items_kwargs.append(kwargs)
        self.update()   #cuello de botella?

        
    def pos_and_size_change(self):
        
        if not hasattr(self, 'orientation'):
            return
        
        self.calc_size_and_positions()
        self.set_positions()
        self.fix_selector_pos()
        
    def create_gui(self):        
        #create frontal visible elements
        for i in range(0, self.visible_elements_len):
            #create
            widget = self.widget_cls(size=self.child_size, size_hint=(None,None), **self.items_kwargs_default)
            
            #store in an array
            self.frontal_items.append(widget)
            #add as child
            self.add_widget(widget)
           
        #right-down centinel
        self.next_centinel = self.widget_cls(size=self.child_size, size_hint=(None,None), **self.items_kwargs_default)
        self.add_widget(self.next_centinel, index=len(self.children)-1)

        #left-up centinel
        self.prev_centinel = self.widget_cls(size=self.child_size, size_hint=(None,None), **self.items_kwargs_default)
        self.add_widget(self.prev_centinel, index=len(self.children)-1)
            
    def reset(self):
        self.items_kwargs = []
        self.first_visible = 0
        self.index_selector = 0
        #self.fix_selector_pos()
            
    def update(self):
        
        if self.canvas == None:
            return
        
        #show valid items
        for i in range(0, self.visible_elements_len):
            if self.first_visible + i < len(self.items_kwargs):
                self.frontal_items[i].opacity = 1.0
                self.set_widget_kwargs(self.frontal_items[i], **self.items_kwargs[self.first_visible+i] )
            else:
                self.frontal_items[i].opacity = 0.0
            
        if self.first_visible + self.visible_elements_len < len(self.items_kwargs):
            self.set_widget_kwargs(self.next_centinel, **self.items_kwargs[self.first_visible+self.visible_elements_len] )

        self.next_centinel.opacity = 0.0
              
        if self.first_visible > 0:
            self.set_widget_kwargs(self.prev_centinel, **self.items_kwargs[self.first_visible-1] )

        self.prev_centinel.opacity = 0.0
        
        #Clock.schedule_once(self.fix_selector_pos, 0)
            
            
    def calc_size_and_positions(self):
        #calc the widget size (depend of the orientation)
        if self.orientation == 'horizontal':
            width = (self.width - self.spacing*(self.visible_elements_len-1)) / self.visible_elements_len
            self.child_size = (width, self.height)
            self.woffset = self.child_size[0] + self.spacing
            self.hoffset = 0
            self.init_pos=self.pos
        else:
            height = (self.height - self.spacing*(self.visible_elements_len-1)) / self.visible_elements_len
            self.child_size = (self.width, height)
            self.woffset = 0
            #debido a que iniciaremos desde la cima, el offset es negativo
            self.hoffset = -(self.child_size[1] + self.spacing)
            self.init_pos=(self.x, self.y+self.height+self.hoffset)
            
    def set_positions(self):
        
        for i in range(0, self.visible_elements_len):
            self.frontal_items[i].pos = (self.init_pos[0]+i*self.woffset, self.init_pos[1]+i*self.hoffset)
            self.frontal_items[i].size = self.child_size
            
        self.prev_centinel.pos = self.frontal_items[0].pos
        self.prev_centinel.size = self.child_size
        self.next_centinel.pos = self.frontal_items[self.visible_elements_len-1].pos
        self.next_centinel.size = self.child_size
        


    def fix_selector_pos(self, dt=None):
        if self.selector != None:
            '''
            selector_target = self.frontal_items[self.index_selector]
            
            self.selector.pos, self.selector.size = self.to_center(selector_target.pos, 
                                                                    selector_target.size, 
                                                                    selector_target.texture_size)
            Animation.cancel_all(self.selector, 'opacity')
            self.selector.opacity = 1
            '''
            
            #----------

            #posicionar el selector de manera bonita
            nextitem = self.frontal_items[self.index_selector]
            #pos, size = self.to_center(nextitem.pos, nextitem.size, nextitem.texture_size)
            pos, size = (nextitem.pos, nextitem.size)
            Animation(opacity=1, size=size, pos=pos, duration=self.overflow_duration).start(self.selector)

    def to_center(self, pos, size, centered_size):
        
        #fix to text size
        newsize = (centered_size[0]+40, size[1])
        
        #center the position
        centerfix = (size[0]/2) - (newsize[0]/2)
        
        #posicion
        pos = (pos[0] + centerfix, pos[1])
        
        return (pos, newsize)  
        
    def prev(self):
        
        #checar si estamos en el primer elemento
        if self.is_in_first():
                        
            if self.waitinguparrow == False:   
                                                            
                #esperar a que se libere la tecla
                Clock.unschedule(self.checkuparrow)
                Clock.schedule_once(self.checkuparrow, .1)
                
                self.waitinguparrow = True
                self.canuparrow = False
                
            elif self.canuparrow:
                super(ListBox, self).prev()
                
        else:
            self.waitinguparrow = False
            super(ListBox, self).prev()


    def checkuparrow(self, dt):
        pressed_keys = pygame.key.get_pressed()
            
        #esperar a que sea liberada la tecla
        if pressed_keys[self.upkey]:
            
            Clock.schedule_once(self.checkuparrow, .1)
        else:
            self.canuparrow = True
            
    def next(self):

        #checar si estamos en el ultimo elemento
        if self.is_in_last():
                        
            if self.waitingdownarrow == False:   
                                                            
                #esperar a que se libere la tecla
                Clock.unschedule(self.checkdownarrow)
                Clock.schedule_once(self.checkdownarrow, .1)
                
                self.waitingdownarrow = True
                self.candownarrow = False
                
            elif self.candownarrow:
                super(ListBox, self).next()
                
        else:
            self.waitingdownarrow = False
            super(ListBox, self).next()
                
        
    def checkdownarrow(self, dt):
        pressed_keys = pygame.key.get_pressed()
            
        #esperar a que sea liberada la tecla
        if pressed_keys[self.downkey]:
            
            Clock.schedule_once(self.checkdownarrow, .1)
        else:
            self.candownarrow = True

    def move(self, direction):
        if self.moving == False:
            super(ListBox, self).move(direction)

    '''----------------ANIMATIONS----------------'''
    def init_selector_animation(self, direction):
        
        self.direction = direction
        
        #lanzar evento de deseleccion del elemento actual        
        if hasattr(self.frontal_items[self.index_selector], 'on_unselected'):
            self.frontal_items[self.index_selector].on_unselected()
            
        if self.selector != None:
            #calcular la posicion y tamaño adecuados del selector
            nextitem = self.frontal_items[self.index_selector+direction]
            #pos, size = self.to_center(nextitem.pos, nextitem.size, nextitem.texture_size)
            pos, size = (nextitem.pos, nextitem.size)
            
            #anim = Animation(duration=self.transition_duration, pos=pos, size=size)
            anim = Animation(duration=self.transition_duration, pos=pos)
            anim.start(self.selector)
        
        Clock.schedule_once(self.end_selector_animation, self.transition_duration)
        
    def end_selector_animation(self, df):
        self.index_selector += self.direction
        self.changed()
        self.moving = False
        
        selected = self.getSelected()
        if hasattr(selected, 'on_selected'):
            selected.on_selected()
        
    def init_scroll_animation(self, direction):
                
        #establecer los indices correctos dependiendo de la direccion del movimiento
        if direction == -1: #left
            fix_begin = 0
            self.fade_out(self.frontal_items[self.visible_elements_len-1], 
                            self.transition_duration)
            self.fade_in(self.prev_centinel, self.transition_duration)
            
            nextitem = self.prev_centinel
            
        else:               #right
            fix_begin = 1
            self.fade_out(self.frontal_items[0], 
                            self.transition_duration)
            self.fade_in(self.next_centinel, self.transition_duration)
            
            nextitem = self.next_centinel
            
        #move items
        for i in range(fix_begin, fix_begin + self.visible_elements_len-1):
            anim = Animation(y=self.frontal_items[i-direction].y, duration=self.transition_duration)
            anim.start(self.frontal_items[i])
            
        
        '''
        #fix selector size
        if self.selector != None:
            #calcular la posicion y tamaño adecuados del selector
            #pos, size = self.to_center(nextitem.pos, nextitem.size, nextitem.texture_size)
            pos, size = (nextitem.pos, nextitem.size)
            
            #anim = Animation(duration=self.transition_duration, pos=pos, size=size)
            anim = Animation(duration=self.transition_duration, pos=pos)
            anim.start(self.selector)
        '''
        
            
        #self.prev_centinel.pos = self.frontal_items[0].pos
        #self.prev_centinel.size = self.frontal_items[0].size
        #self.next_centinel.pos = self.frontal_items[self.visible_elements_len-1].pos
        #self.next_centinel.size = self.frontal_items[self.visible_elements_len-1].size
            
        Clock.schedule_once(self.end_scroll_animation, self.transition_duration)
        
            
    def end_scroll_animation(self, df):
        self.remove_animations()
        self.update()
        self.set_positions()
        self.changed()
        self.moving = False
        
        #self.getSelected().on_selected()
        selected = self.getSelected()
        if hasattr(selected, 'on_selected'):
            selected.on_selected()
            
            
    def is_in_first(self):
        if self.getSelectedIndex() == 0:
            return True
        return False
        
    def is_in_last(self):
        if self.getSelectedIndex() == self.count()-1:
            return True
        return False
        
    def count(self):
        return len(self.items_kwargs)
        
    def init_overflow_beginning(self):
        self.init_overflow()

    def init_overflow_ending(self):
        self.init_overflow()
        
    def init_overflow(self):
        for it in self.frontal_items:
            self.fade_out(it, self.overflow_duration)
            
        Clock.schedule_once(self.end_init_overflow, self.overflow_duration)
        
        #mover barra
        if self.index_selector == 0:
            nextitem = self.frontal_items[self.visible_elements_len-1]
        
        else:
            nextitem = self.frontal_items[0]
            
        #pos, size = self.to_center(nextitem.pos, nextitem.size, nextitem.texture_size)

        if self.selector != None:
            Animation(y=nextitem.y, opacity=0, duration=self.overflow_duration).start(self.selector)
            
        
    def end_init_overflow(self, dt):
        self.update()
        #self.fix_selector_pos()
        
        '''
        #barra de seleccion
        if self.index_selector == 0:
            nextitem = self.frontal_items[self.visible_elements_len-1]        
        else:
            nextitem = self.frontal_items[0]
        '''
        
        
        for i in range(0, len(self.frontal_items) ):
            if self.first_visible + i < len(self.items_kwargs):
                self.fade_in(self.frontal_items[i], self.transition_duration)
        
        Clock.schedule_once(self.end_overflow, self.transition_duration)
        
    def end_overflow(self, dt):
        self.changed()
        self.moving = False
        
        self.fix_selector_pos()
        
        #self.getSelected().on_selected()
        selected = self.getSelected()
        if hasattr(selected, 'on_selected'):
            selected.on_selected()
        
    def remove_animations(self):
        for i in range(0, self.visible_elements_len):
            Animation.cancel_all(self.frontal_items[i], 'pos')
            Animation.cancel_all(self.frontal_items[i], 'y')
            Animation.cancel_all(self.frontal_items[i], 'opacity')
            
        Animation.cancel_all(self.prev_centinel, 'pos')
        Animation.cancel_all(self.next_centinel, 'pos')
        Animation.cancel_all(self.prev_centinel, 'y')
        Animation.cancel_all(self.next_centinel, 'y')
        Animation.cancel_all(self.prev_centinel, 'opacity')
        Animation.cancel_all(self.next_centinel, 'opacity')
        
    def getSelected(self):
        return self.frontal_items[self.index_selector]
        
    def getSelectedIndex(self):
        return self.first_visible + self.index_selector
        
    def set_element(self, index, **kwargs):
        #valid index?
        if index >=0 and index < len(self.items_kwargs):
            self.items_kwargs[index] = kwargs
            #is visible index?
            if index >= self.first_visible and index < self.first_visible + self.visible_elements_len-1:
                #update visible index
                visible_index = self.first_visible + index  #calc visible index
                #self.set_widget_kwargs(self.frontal_items[visible_index], **kwargs)
                
                self.update()
        
    
    def changed(self):
        '''
        Evento lanzado al momento de terminar de mover los elementos
        '''
        pass
        


    def fade_in(self, widget=None, duration=0.1):
        anim = Animation(opacity=1.0, duration=duration)
        if widget == None:
            anim.start(self)
        else:
            anim.start(widget)
        
    def fade_out(self, widget=None, duration=0.1):
        anim = Animation(opacity=0.0, duration=duration)
        if widget == None:
            anim.start(self)
        else:
            anim.start(widget)
            
    def on_pos(self, w, val):
        print 'New listbox pos', val
        self.pos_and_size_change()
        
    def on_size(self, w, val):
        print 'New listbox size', val
        self.pos_and_size_change()

if __name__ == '__main__':
    
     
    from kivy.core.window import Window
    from kivy.uix.popup import Popup
    
    class testApp(App):
        
        def __init__(self, **kwargs):
            super(testApp, self).__init__(**kwargs)
            self._keyboard = Window.request_keyboard(
                self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_keyboard_down)

        def _keyboard_closed(self):
            print ('My keyboard have been closed!')
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)
            self._keyboard = None

        def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
            print ('The key', keycode, 'have been pressed')
            print (' - text is %r' % text)
            print (' - modifiers are %r' % modifiers)

            # Keycode is composed of an integer + a string
            # If we hit escape, release the keyboard
            if keycode[1] == 'escape':
                keyboard.release()
                
                
            if keycode[0] == 273:   #UP
                self.lst_base.prev()
            if keycode[0] == 276:   #LEFT
                self.lst_base.prev()
            if keycode[0] == 274:   #DOWN
                self.lst_base.next()
            if keycode[0] == 275:   #RIGHT
                self.lst_base.next()


            # Return True to accept the key. Otherwise, it will be used by
            # the system.
            return True
        
        def build(self):
            kwparameters = [{'text':str(i)} for i in xrange(12)]
            
            kwparameters.append({'text':'0123456789012345670012345678901234567890123456789012345676585464901234567890123456700123456789012345678901234567890123456765854649847800'})
            
            self.lst_base = ListBox(spacing=2, 
                                    #size=(600,400), 
                                    #size_hint=(None,None),
                                    #pos=(50,100), 
                                    visible_elements_len=10,
                                    orientation='vertical',
                                    items_kwargs=kwparameters)
                                    
            return Popup(title='ListBox', content=self.lst_base)
    
    testApp().run()
    
