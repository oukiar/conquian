
#!/usr/bin/python
# -*- coding: latin-1 -*-

import kivy

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.stencilview import StencilView
from kivy.uix.label import Label

class ListBase(StencilView):

    '''
    def _set_items_kwargs(self, value):
        print value
    items_kwargs=property(None, _set_items_kwargs)
    '''
    items_kwargs=[]
    
    '''
    Lista con los argumentos (en forma de diccionario) necesarios para
    crear cada elemento.
    '''   
    
    index_selector = 0
    '''
    Index of selected element on the view
    '''
    
    first_visible = 0
    '''
    Index of first visible element
    '''
    
    

    
    
    def _get_selected_index(self):
        return self.first_visible + self.index_selector
    def _set_selected_index(self, value):
        self.selected_index = value
        
    selected_index = property(_get_selected_index, _set_selected_index, doc='Elemento seleccionado')
    

    
    
    def __init__(self, **kwargs):
        super(ListBase, self).__init__(**kwargs)
        
        #parameters assign
        self.widget_cls = kwargs.get('widget_cls', Label)
        self.items_kwargs = kwargs.get('items_kwargs', [])
        self.items_kwargs_default = kwargs.get('items_kwargs_default', {})
        self.visible_elements_len = kwargs.get('visible_elements_len', 10)
        self.spacing = kwargs.get('spacing', 0)
            
    def next(self):
        self.move(1)
        
    def prev(self):
        self.move(-1)

    def move(self, direction):
        self.moving = True
        
        #self.getSelected().on_unselected()
            
        #move selector?
        if (self.index_selector+direction >= 0) and (self.index_selector+direction < self.visible_elements_len) and self.index_selector+direction < len(self.items_kwargs) and self.selector != None:
           
            
            #iniciar animacion de movimiento del selector (barra de seleccion)
            self.init_selector_animation(direction)
        #scroll list?
        elif self.first_visible+direction >= 0 and (self.first_visible+self.index_selector < len(self.items_kwargs)-1) :
            self.init_scroll_animation(direction)
            self.first_visible += direction
            
            #si no hay selector, debemos mover el selector al extremo adecuado de la lista
            if self.selector == None:
                if direction < 0:
                    self.index_selector = self.visible_elements_len - 1
                elif direccion > 0:
                    self.index_selector = 0
            
        #lower overflow?
        elif self.first_visible+self.index_selector + direction < 0:
            '''
            Maybe you want fire an event when this happen
            '''
            self.init_overflow_beginning()
            
            if len(self.items_kwargs) >= self.visible_elements_len:
                self.first_visible = len(self.items_kwargs)-self.visible_elements_len
                self.index_selector = self.visible_elements_len-1
            else:
                self.first_visible = 0
                self.index_selector = len(self.items_kwargs)-1
                
        #upper overflow?
        elif self.first_visible+self.index_selector + direction >= len(self.items_kwargs):  #maybe with only equal is sufficient
            '''
            Maybe you want fire an event when this happen too
            '''
            self.init_overflow_ending()
            self.first_visible = 0
            self.index_selector = 0
            
    def init_selector_animation(self, direction):
        pass
            
    def init_scroll_animation(self, direction):
        pass
    
    def init_overflow_beginning(self):
        pass
        
    def init_overflow_ending(self):
        pass

    def set_widget_kwargs(self, widget, **kwargs):
        for i in kwargs:
            setattr(widget, i, kwargs[i])
    
if __name__ == '__main__':
    
    class testApp(App):
        def build(self):
            return ListBase(title='Configurar joysticks')
    
    testApp().run()
