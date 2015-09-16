#!/usr/bin/python
# -*- coding: latin-1 -*-

import os

from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.animation import Animation, AnimationTransition
from kivy.core.image import Image as CoreImage
from kivy.properties import NumericProperty, ListProperty, StringProperty

from kivy.uix.button import Button
from kivy.uix.label import Label

from kivy.clock import Clock


from widget3D import Widget3D, Image3D, rotatingPoints
import utils

Window.set_icon("ojbxproicon.png")

class Label3D(Widget3D):
    text = StringProperty()
    def __init__(self, **kwargs):
        text = kwargs.pop("text", "")
        super(Label3D, self).__init__(**kwargs)
        self.label = Label()
        self.add_widget(self.label)
        self.text = text
        
    def on_text(self, w, val):
        self.label.text = val

class CoverItem(Widget3D):
    
    def __init__(self, **kwargs):
        
        super(CoverItem, self).__init__(**kwargs)
        
        self.bg = Image3D(source='cover.png', size_hint=(None,None) )
        
        self.image = Image3D(size_hint=(None,None), x=.4, size=(83.4, 91))
        #self.points = rotatingPoints(scale3D=(2, 2, 1))
        
        #self.title = Button(text='hello', size_hint=(None,None), height=40, width=150, x=-75, y=40, font_size=20, background_normal="barra_play.png")
        self.title = Label3D(text='hello', pos_z=-800, size_hint=(None,None) )
        self.title.pos_z = -1000
        print "POS3D: ", self.title.pos3D
        self.add_widget(self.title)
        
        self.add_widget(self.bg)
        
    def set_texture(self, texture):
        if texture != None and texture != False:
            if self.image not in self.children:
                self.add_widget(self.image)
            
            self.image.texture = texture
            '''
            #if self.points in self.children:
            #    self.remove_widget(self.points)
        else:
            self.add_widget(self.points)
            self.remove_widget(self.image)
            '''
            
    def on_opacity(self, w, val):
        self.image.opacity = val
        #self.points.opacity = val
        
        super(CoverItem, self).on_opacity(w, val)

class CoverFlow(Widget3D):
    
    path = StringProperty()
    index = NumericProperty(0)
    
    side_ncovers = NumericProperty(0)
    '''
    Covers by side
    '''
    
    visible_covers = NumericProperty(0)
    '''
    Total visible covers
    '''
    
    center_separation = NumericProperty(4)
    
    cover_separation = NumericProperty(3)
    
    cover_rotation = NumericProperty(90)
    
    side_ncovers = NumericProperty(3)
    
    scale_side_covers = NumericProperty(.5)
    
    threshold_move = NumericProperty(50)
    
    def __init__(self, **kwargs):
        
        super(CoverFlow, self).__init__(**kwargs)
        
        self.net = kwargs.get('net', None)
        
        self.path = kwargs.get('path', '')
        self.side_ncovers = kwargs.get('ncovers', 3)
        
        #if number of covers change, we must recreate front covers
        self.bind(side_ncovers=self.on_recreategui)
        
        self.visible_covers = (self.side_ncovers*2) + 1
        self.move_duration = kwargs.get('move_duration', .2)
        self.direction = 0
        self.move_threshold = 20    #pixels
        
        
        self.touch_move_duration = .1
        
        self.canceling_move = False
        
        self.covers = []
        self.cache = {}
        self.cache_direction = 1
        self.cache_side_length = 10
        
        self.center_separation = kwargs.get('center_separation', 4)
        self.bind(center_separation=self.on_recalculate)
        
        self.cover_separation = kwargs.get('cover_separation', 3)
        self.bind(cover_separation=self.on_recalculate)
        
        self.cover_rotation = kwargs.get('cover_rotation', 90)
        self.bind(cover_rotation=self.on_recalculate)
        
        self.scale_side_covers = kwargs.get('scale_side_covers', .5)
        self.bind(scale_side_covers=self.on_recalculate)
        
        #default image cover
        self.default = CoreImage('cover.png')
        
        
        self.create_covers()

        #listar las imagenes que se encuentran dentro de los directorios
        self.get_covers()
                
        #self.assign_covers()
        
        self.reset_positions()
        
        self.carousell = False
        #self.init_carousell()
        
        #no abortar carga de portadas inicialmente
        self.abortloader = False
        
        #cargador asincrono de portadas
        #Clock.schedule_once(self.async_loader, .3)
        
        
    def on_recreategui(self, w, val):
        for i in self.covers:
            self.remove_widget(i)
            
        self.covers = []
        
        self.create_covers()
        
        self.reset_positions()
        self.assign_covers()
        
    def on_recalculate(self, w, val):
        #usefull?
        self.reset_positions()
        
    def create_covers(self):
       
        ic = 0
        covers={}

        #izquierda
        for i in range(-self.side_ncovers, 0, 1):
            #covers[ic] = Image3D(source='cover.png')
            covers[ic] = CoverItem()
            self.add_widget(covers[ic])
            ic+=1
        
        ic=self.visible_covers - 1
        
        #derecha
        for i in range(self.side_ncovers, 0, -1):
            #covers[ic] = Image3D(source='cover.png')
            covers[ic] = CoverItem()
            self.add_widget(covers[ic])
            ic-=1
            
        #central of covers
        ic = self.side_ncovers
        #central
        #covers[ic] = Image3D(source='cover.png')
        covers[ic] = CoverItem()
        
        self.add_widget(covers[ic])
        
        #sort the covers
        for i in sorted(covers):
            self.covers.append(covers[i])
            
        #self.centinel = Image3D(source='cover.png' )
        self.centinel = CoverItem()
        
    def on_scale3D(self, w, val):
        self.calculate_coords()
                
    def calculate_coords(self):
        '''
        
        '''
        ic = 0
        self.covers_positions=[]
        
        
        #calc relative scale of side covers
        sx, sy, sz = (self.scale_x * self.scale_side_covers,
                     self.scale_y * self.scale_side_covers,
                     self.scale_z * self.scale_side_covers )

        #izquierda
        for i in range(-self.side_ncovers, 0, 1):
            self.covers[ic].pos_x = i * self.cover_separation - self.center_separation
            self.covers[ic].rotate_y = self.cover_rotation
            self.covers[ic].scale3D = (sx, sy, sz)
            ic+=1
        
        ic=self.visible_covers -1
        
        #derecha
        for i in range(self.side_ncovers, 0, -1):
            #print 'debug here: ', ic
            self.covers[ic].pos_x = i * self.cover_separation + self.center_separation
            self.covers[ic].rotate_y = -self.cover_rotation
            self.covers[ic].scale3D = (sx, sy, sz)
            ic-=1
            
        #central of covers
        ic = self.side_ncovers
        #central
        self.covers[ic].pos_x = 0
        self.covers[ic].rotate_y = 0        
        self.covers[ic].scale3D = self.scale3D        
        
        #sort the covers
        for i in self.covers:
            #save the original pos, rotation and scale
            self.covers_positions.append( (i.pos_x, 
                                            i.rotate_y, 
                                            (i.scale_x, i.scale_y)  
                                           )
                                         )
        
    def assign_covers(self):
        #print "Asignando covers, index: " + str(self.index)
        
        #indice del cover de la izquierda
        self.curcover = self.index-self.side_ncovers
        
        for i in self.covers:
            Animation.cancel_all(i, 'opacity')
            #i.texture = self.get_cover_from_cache(self.curcover)
            i.set_texture(self.get_cover_from_cache(self.curcover))
            i.opacity = 1
            self.curcover += 1
            if self.curcover == len(self.lst_covers):
                self.curcover = 0
                
    def reset_positions(self):        
        
        self.calculate_coords()
        
        for i in self.covers:
            Animation.cancel_all(i, 'pos_x', 'rotate_y', 'scale_x', 'scale_y')
            
            xtrans, yrot, scale3d = self.covers_positions[self.covers.index(i)]
            
            i.pos_x = xtrans
            i.rotate_y = yrot
            i.scale_x = scale3d[0]
            i.scale_y = scale3d[1]
            
            print "Z: ", i.title.pos_z
      
    def get_cover_from_cache(self, index, load=True):
        '''
        Obtiene una imagen desde cache, retorna False
        si la imagen aun no ha sido cargada en cache
        '''
        
        if index >= len(self.lst_covers):
            index = index - len(self.lst_covers)
            
        
        if index < len(self.lst_covers):
            cover = self.lst_covers[index]

            if cover in self.cache:
                return self.cache[cover]
            
            
            if load:   
                self.cache[cover] = CoreImage(cover).texture
                return self.cache[cover]
            
            
            return False
                
    def get_covers(self):
        '''
        Get a list of covers that exists into each directory of the path
        '''
        
        print 'Listando desde coverflow: ', self.path
        
        self.lst_covers = []
        for i in sorted(os.listdir(self.path)):
        
            if i[0] == '.':
                continue
            
            fullpath = os.path.join(self.path, i)
            
            if os.path.isdir(fullpath):
                self.lst_covers.append(utils.get_img_file( fullpath ))


        
    def async_loader(self, dt):
        '''
        Encargado de cargar las portadas siempre y cuando no haya
        movimiento del usuario
        
        ESTA FUNCION CARGA SOLAMENTE UNA PORTADA CADA VEZ QUE ES
        EJECUTADA POR LA TEMPORIZACION
        '''
        
        
        #siempre se inicia la carga en la portada central
        
        #indices para ir recorriendo todas las portadas a cargar
        sup = self.index + self.side_ncovers
        inf = sup - 1
        
        #banderas para saber que indices siguen siendo validos
        #para cargar portadas (sin overflow)
        bsup = True
        binf = True
        
        #print 'Entrando con index ', sup
        
        while bsup or binf:
            #cargar superior
            if sup < len(self.lst_covers):
                #try get a cover without load in cache
                if self.get_cover_from_cache(sup, False) == False:
                    print('Loading to cache: ', sup)
                    
                    cover = self.get_cover_from_cache(sup)
                    
                    #si es una portada visible, mostrar fluidamente
                    if sup < (self.index + (self.side_ncovers*2)+1):
                        ncover = sup - self.index
                        
                        print 'R Mostrando: ', ncover
                        
                        Animation.cancel_all(self.covers[ncover], 'opacity')
                        self.covers[ncover].set_texture(cover)
                        self.covers[ncover].opacity = 0
                        
                        Animation(opacity=1, duration=.4).start(self.covers[ncover])
                    
                    Clock.schedule_once(self.async_loader, .3)
                    
                    return
                    
                sup += 1
            else:
                bsup = False
            
            #cargar inferior
            if inf >= 0:
                #try get a cover without load in cache
                if self.get_cover_from_cache(inf, False) == False:
                    print('Loading to cache: ', inf)
                    cover = self.get_cover_from_cache(inf)
                    
                    #si es una portada visible, mostrar fluidamente
                    if inf >= self.index:
                        ncover = inf - self.index
                        
                        print 'L Mostrando: ', ncover
                        
                        Animation.cancel_all(self.covers[ncover], 'opacity')
                        self.covers[ncover].set_texture(cover)
                        self.covers[ncover].opacity = 0
                        
                        Animation(opacity=1, duration=.4).start(self.covers[ncover])
                    
                    Clock.schedule_once(self.async_loader, .3)
                    
                    return
                
                inf -= 1
            else:
                binf = False
                
            #print 'Sup ', sup
            #print 'Inf ', inf
        
        return
        
        #derecha
        i = self.index
        cache_counter = 0
        while True:
            #try get a cover without load in cache
            if self.get_cover_from_cache(i, False) == False:
                print('Loading to cache: ', i)
                self.get_cover_from_cache(i)
                return
                
            i += self.cache_direction
            cache_counter += 1
            
            if cache_counter >= self.cache_side_length:
                return
            
            if i < 0:
                i = len(self.lst_covers)-1
            elif i >= len(self.lst_covers):
                i = 0
                        
        #izquierda
        i = self.index
        cache_counter = 0
        while True:
            #try get a cover without load in cache
            if self.get_cover_from_cache(i, False) == False:
                print('Loading to cache: ', i)
                self.get_cover_from_cache(i)
                return
                
            i -= 1
            cache_counter += 1
            
            if cache_counter >= self.cache_side_length:
                return
            
            if i < 0:
                i = len(self.lst_covers)-1
                
    def cancel_movement(self):
        '''
        Restaura las posiciones de manera fluida
        '''
        
        self.canceling_move = True
        
        Clock.unschedule(self.end_move)
        
        for i in self.covers:
            Animation.cancel_all(i, 'pos_x', 'rotate_y', 'scale_x', 'scale_y', 'opacity')
        
            xtrans, yrot, scale3d = self.covers_positions[self.covers.index(i)]

            #enabled smoth transition
            Animation(pos_x=xtrans, 
                        rotate_y=yrot,
                        scale_x=scale3d[0],
                        scale_y=scale3d[1],
                        opacity=1,
                        duration=self.move_duration
                        ).start(i)
                        
        #centinel reset
        Animation.cancel_all(self.centinel, 'opacity')
        self.centinel.opacity = 1
        
        self.direction = 0
        Clock.schedule_once(self.end_cancel_movement, self.move_duration)
        
        
    def end_cancel_movement(self, dt):
        self.canceling_move = False
   
    def move_to_left(self):
        if self.direction == 1:
            self.cancel_movement()
        else:
            self.move(-1, self.move_duration)
        
    def move_to_right(self):
        if self.direction == -1:
            self.cancel_movement()
        else:
            self.move(1, self.move_duration)
            
    def move(self, direction, duration, launch_move_end=True):
        
        #abortar carga de portada (hasta superar el tiempo de iddle)
        Clock.unschedule(self.async_loader)
        Clock.schedule_once(self.async_loader, .3)
        
        
        if self.direction != 0 or self.canceling_move:
            return
        
        if direction > 0:  #movimiento a la derecha?
            fixbegin = 0
            fixend = self.visible_covers-1
            centinel_covers_index = 0
            centinel_cache_index = self.index - self.side_ncovers - 1
            #percent of movement
            #percent_movement = 1-direction      #useful on touch events (to make a smooth motion between prev and current cover position)
            percent_movement = 0      
            direction = 1
            hide_index = self.visible_covers - 1

        elif direction < 0:  #movimiento a la izquierda?
            fixbegin = 1
            fixend = self.visible_covers
            centinel_covers_index = self.visible_covers-1
            centinel_cache_index = self.index + self.side_ncovers + 1
            #percent of movement
            #percent_movement = 1+direction
            percent_movement = 0
            direction = -1
            hide_index = 0
        else:
            return
        
        for i in range(fixbegin, fixend):
            
            xtrans_diff = self.covers_positions[i][0] - self.covers_positions[i+direction][0]
            yrot_diff = self.covers_positions[i][1] - self.covers_positions[i+direction][1]
            
            anim = Animation(
                        pos_x=self.covers[i+direction].pos_x, # + xtrans_diff*percent_movement,
                        rotate_y=self.covers[i+direction].rotate_y, # + yrot_diff*percent_movement,
                        scale_x=self.covers[i+direction].scale_x,
                        scale_y=self.covers[i+direction].scale_y,
                        transition=AnimationTransition.in_out_sine,
                        duration=duration
                        )
                        
            
            anim.start(self.covers[i])
            
        #fade out correpondiente cover
        Animation(opacity=0, duration=duration).start(self.covers[hide_index])
        
        self.centinel.pos3D = self.covers[centinel_covers_index].pos3D
        
        self.centinel.rotate_y = self.covers[centinel_covers_index].rotate_y
        self.centinel.rotate_x = 0
        self.centinel.rotate_z = 0
        self.centinel.scale3D = self.covers[centinel_covers_index].scale3D
        self.centinel.set_texture( self.get_cover_from_cache(centinel_cache_index) )
        self.centinel.opacity = 0
        
        #we use the super of coverflow because we dont want the add_widget of widget3D (we already have translated 3dposition)
        if not self.centinel in self.children:
            super(Widget3D, self).add_widget(self.centinel, len(self.children))
        
        Animation(opacity=1, duration=duration).start(self.centinel)
        
        #make the movement at the end?
        if launch_move_end:
            #remember the direction ... important, only save direction if final movement would make
            self.direction = direction
            
            Clock.schedule_once(self.end_move, duration+.05)
    
    def on_opacity(self, w, val):
        for i in self.children:
            i.opacity = val
    
        
    def end_move(self, dt):
                
        #izquierda
        if self.direction == -1:
                
            if self.index < len(self.lst_covers)-1:
                self.index += 1
            
            else:
                self.index = 0
                
        #derecha ... los albums se mueven a la derecha, el index decrementa
        elif self.direction == 1:
            if self.index == 0:
                self.index = len(self.lst_covers)-1
                #print 'index', self.index
                
            elif self.index > 0:
                self.index -= 1
            else:
                self.index = len(self.lst_covers)-1

    def on_index(self, w, val):
        '''
        Ejecutado al cambiar la portada central (seleccionada)
        '''
        #print 'on_index', val
        self.direction = 0  #no movement
        self.remove_widget(self.centinel)
        
        
        self.reset_positions()
        self.assign_covers()  
        
    def on_path(self, w, val):
        
        if not hasattr(self, 'covers'):
            return
        
        self.cache = {}
        self.get_covers()
        self.assign_covers()
        
    def init_carousell(self, dt=None):
        self.carousell = True
        self.move(1, self.move_duration*3)
        Clock.schedule_once(self.init_carousell, self.move_duration*5)
     
    def cancel_carousell(self):
        self.carousell = False
        Clock.unschedule(self.init_carousell)

    
class CoverFlowApp(FloatLayout):
    def __init__(self, **kwargs):
        super(CoverFlowApp, self).__init__(**kwargs)
        
        #self.coverflow_2 = CoverFlow(ncovers=2, path='covers', pos3D=(0,4,-15), cover_rotation=45)
        #self.coverflow_2 = CoverFlow(ncovers=2, path='/Volumes/HDD/REPERTORIO/TODOS', pos3D=(0,4,-2), cover_rotation=45)
        self.coverflow_2 = CoverFlow(ncovers=2, path='/home/pi/REPERTORIO/TODOS', pos3D=(0,4,-2), cover_rotation=45)
        
        self.add_widget(self.coverflow_2)
        
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print('The key', keycode, 'have been pressed')
        print(' - text is %r' % text)
        print(' - modifiers are %r' % modifiers)

        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        if keycode[1] == 'escape':
            keyboard.release()
            
        if keycode[1] == 'left':
            self.coverflow_2.move_to_left()
            
        if keycode[1] == 'right':
            self.coverflow_2.move_to_right()
            
        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True
        


if __name__ == '__main__':
    from kivy.base import runTouchApp
    
    runTouchApp(CoverFlowApp() )
