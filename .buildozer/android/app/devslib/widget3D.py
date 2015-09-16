#!/usr/bin/python
# -*- coding: latin-1 -*-


from kivy.core.window import Window
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

from kivy.core.image import Image as CoreImage
from kivy.properties import StringProperty, ListProperty, NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.clock import Clock

from kivy.graphics.transformation import Matrix

from kivy.graphics.opengl import *
from kivy.graphics import *


from kivy.graphics import Mesh
from functools import partial
from math import cos, sin, pi

#class Space3D(Widget):
class Widget3D(Widget):
    '''
    Works in 3D world ... the class can be named Space3D?
    
    Must be child of another widget, if you use this as Main widget a pygame parachute will ocurr
    
    Warning: Dont use as main widget, instead add as a child of standar Widget
    
    Note: Very Very experimental
    
    For the moment widgets must be created at the begin of the APP,
    future creations of Widget3D will raise a pygame exception, unknown reason
    
    '''

    r = NumericProperty(1)
    g = NumericProperty(1)
    b = NumericProperty(1)
    
    color3D = ReferenceListProperty(r, g, b)
    '''
    Color of this widget
    '''
        
    scale_x = NumericProperty(1)
    scale_y = NumericProperty(1)
    scale_z = NumericProperty(1)
    
    scale3D = ReferenceListProperty(scale_x, scale_y, scale_z)
    '''
    Scale this widget
    '''
    
    rotate_x = NumericProperty(0)
    rotate_y = NumericProperty(0)
    rotate_z = NumericProperty(0)
    
    rotate3D = ReferenceListProperty(rotate_x, rotate_y, rotate_z)
    '''
    Rotation in degrees
    '''
    
    pos_x = NumericProperty(0)
    pos_y = NumericProperty(0)
    pos_z = NumericProperty(-10)
    pos3D = ReferenceListProperty(pos_x, pos_y, pos_z)
    '''
    Position on 3D space, please be carefull because (0,0,0) is not visible by the observer (Z=-15 is good)
    '''
    
    def __init__(self, **kwargs):
        self.scale3D = kwargs.pop('scale3D', (1,1,1))   #real size by default
        self.rotate3D = kwargs.pop('rotate3D', (0,0,0))
        self.pos3D = kwargs.pop('pos3D', (0,0,-150))     #z = -15 is good for the observer (person front of the monitor-screen-display-etc)

        #
        self.canvas = RenderContext(compute_normal_mat=True)

        #
        with self.canvas.before:
            PushMatrix()    #save the current opengl state
            self.cb_setup = Callback(self.setup_gl_context)
            #translate
            self.translate = Translate(self.pos_x, self.pos_y, self.pos_z)
            #rotate
            self._rotatex = Rotate(angle=self.rotate_x, axis=(1, 0, 0) )
            self._rotatey = Rotate(angle=self.rotate_y, axis=(0, 1, 0) )
            self._rotatez = Rotate(angle=self.rotate_z, axis=(0, 0, 1) )
            #scale
            self.scale = Scale(self.scale_x, self.scale_y, self.scale_z)
                        
            self.cb_reset = Callback(self.reset_gl_context)
            
        with self.canvas:
            '''
            This widget have not canvas yet, please add your own canvas primitives in your derived class
            '''
            pass
            
        with self.canvas.after:
            
            PopMatrix() #restore the previous opengl state 
          
        #configure 3D
        self.setup3D()
        
        super(Widget3D, self).__init__(**kwargs)
        
    def setup3D(self):
        hasp =  float(Window.width) / float(Window.height)
        asp =  float(Window.height) / float(Window.width)
        #self.canvas['projection_mat'] = Matrix().view_clip(-asp, asp, -1, 1, 1, 100, 1)
        self.canvas['projection_mat'] = Matrix().view_clip(-hasp, hasp, -1, 1, 1, 4096, 1)
    
    def project2D(self):
        return Matrix().project(self.pos_x+self.pos[0],
                            self.pos_y+self.pos[1],
                            self.pos_z,
                            self.canvas['modelview_mat'],
                            self.canvas['projection_mat'],
                         0,
                         0,
                         Window.width,
                         Window.height)
    
    def collide_point3D(self, pointx, pointy):
        #print self.pos
    
        x, y, z = Matrix().project(self.pos_x+self.pos[0],
                            self.pos_y+self.pos[1],
                            self.pos_z,
                            self.canvas['modelview_mat'],
                            self.canvas['projection_mat'],
                            0,
                            0,
                            Window.width,
                            Window.height)
            
        w, h, z = Matrix().project(self.pos_x+self.pos[0]+self.width,
                            self.pos_y+self.pos[1]+self.height,
                            self.pos_z,
                            self.canvas['modelview_mat'],
                            self.canvas['projection_mat'],
                            0,
                            0,
                            Window.width,
                            Window.height)
                            
        #print x,y,w,h
    
        return Widget(pos=(x, y), size=(w-x, h-y)).collide_point(pointx, pointy)
    
    
    #This version lacks of herencia 3D ... I think
    def add_widget(self, w, position=0):
        
        #solo si tiene propiedad 3D
        if hasattr(w, 'pos_x'):
            
            #only position is accumulative ... be carefull        
            w.pos_x += self.pos_x
            w.pos_y += self.pos_y
            w.pos_z += self.pos_z
            
            #ahora tambien la rotacion es heredada
            w.rotate_x = self.rotate_x
            w.rotate_y = self.rotate_y
            w.rotate_z = self.rotate_z
            
            #la escala tambien debe ser la misma que la del padre
            w.scale_x = self.scale_x
            w.scale_y = self.scale_y
            w.scale_z = self.scale_z
        
        super(Widget3D, self).add_widget(w, position)
        
    def save_pos(self):
        '''
        Save the current 3D position of the object
        '''
        pass
    
    def to2d(self, w=None):
        '''
        Return the 2D coordinates transformed to 3D position
        '''
        
        if w == None:
            w = self
        
        ratio = float(Window.width)/Window.height
        
        xratiofix = float(self.width)/(Window.width/2)*ratio
        yratiofix = float(self.height)/(Window.height/2)
        
        self.pos_x=-1*ratio
        self.pos_y=-1
        self.pos_z=-1
        self.scale_x=1.0 / self.width * xratiofix
        self.scale_y=1.0 / self.height * yratiofix

    def on_rotate3D(self, w, val):
        '''
        Update rotation values for the canvas draws, ... bad performance here? (float/float)
        '''
        self.setup3D()
        self._rotatex.angle = val[0]
        self._rotatey.angle = val[1]
        self._rotatez.angle = val[2]
        
        for i in self.children:
            i.rotate3D = self.rotate3D
    
    def on_pos3D(self, w, val):
        self.translate.x = val[0]
        self.translate.y = val[1]
        self.translate.z = val[2]
        
        for i in self.children:
            i.pos3D = self.pos3D
        
    def on_scale3D(self, w, val):
        
        self.scale.x = val[0]
        self.scale.y = val[1]
        self.scale.z = val[2]
        
        #changue all out childreen scale too ... be carefull, this is equal on childs and parents
        for i in self.children:
            i.scale3D = self.scale3D
    
    '''       
    def on_opacity(self, w, val):
        for i in self.children:
            i.opacity = val
    '''
    
    def setup_gl_context(self, *args):
        glEnable(GL_DEPTH_TEST)

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)



class Edit3D(FloatLayout):
    def __init__(self, **kwargs):
        super(Edit3D, self).__init__(**kwargs)
    
        self.lb_command = Label(text='Command: ')
        #self.add_widget(self.lb_command)
    
        self.options3D = BoxLayout(size_hint=(None,None), width=300)
    
        self.btn_x = ToggleButton(text='X')
        self.btn_y = ToggleButton(text='Y')
        self.btn_z = ToggleButton(text='Z')
        self.btn_w = ToggleButton(text='W')
        self.btn_h = ToggleButton(text='H')
    
        self.options3D.add_widget(self.btn_x)
        self.options3D.add_widget(self.btn_y)
        self.options3D.add_widget(self.btn_z)
        self.options3D.add_widget(self.btn_w)
        self.options3D.add_widget(self.btn_h)
    
        self.add_widget(self.options3D)
    
    def on_touch_down(self, touch):
        super(Edit3D, self).on_touch_down(touch)

        self.lasttouch = touch.pos


    def on_touch_move(self, touch):
        
        diff = float(self.lasttouch[1]) - float(touch.pos[1])
        
        #print diff
        
        for i in self.children:
            
            if i in [self.options3D]:
                continue
            
            if self.btn_x.state == 'down':
                i.pos_x += diff*.01
                    
            if self.btn_y.state == 'down':
                i.pos_y += diff*.01
                            
            if self.btn_z.state == 'down':
                i.pos_z += diff*.01
                                    
        super(Edit3D, self).on_touch_move(touch)


class ZoomLayout3D(Widget3D):
    '''
    Layout that lets you make zoom in the scene
    
    By the moment, only change the scale of them childrens
    '''
    def __init__(self, **kwargs):
        super(ZoomLayout3D, self).__init__(**kwargs)
        
    def add_widget(self, widget, index=0):
        super(ZoomLayout3D, self).add_widget(widget, index)
        
    def on_touch_down(self, touch):

        if touch.button == 'scrolldown':
            print('Zoom in')
            
            for i in self.children:
                i.scale_x +=.1
                i.scale_y +=.1
            
        elif touch.button == 'scrollup':
            print('Zoom out')
            
            for i in self.children:
                i.scale_x -=.1
                i.scale_y -=.1
            
        super(ZoomLayout3D, self).on_touch_down(touch)
        
class Slider3D(Widget3D):
    pass

class Pivot3D(Widget3D):
    pass
    
class LoginLogo(Widget3D):
    def __init__(self, **kwargs):
        super(LoginLogo, self).__init__(**kwargs)
        
        with self.canvas:
            Line(circle=(0, 0, 1))
            
            Mesh( vertices=[0,0, 1, 1], indices=[], mode='points' )
            #Color(0,0,0)
            #Line(circle=(0, 0, .5))
        
class Image3D(Widget3D):
    texture = ObjectProperty()
    source = StringProperty()
    
    def __init__(self, **kwargs):
        
        self.backupcenter = (0,0)
        
        super(Image3D, self).__init__(**kwargs)
        
        self.source = kwargs.get('source', '')
            
        self.center = (0,0)

            
    def on_texture(self, text, val):
        self.canvas.clear()
        with self.canvas:
            Rectangle(texture=val, pos=self.pos, size=self.size)

    def on_source(self, w, val):
        
        if self.source != '':            
            self.texture = CoreImage(self.source).texture


    def on_size(self, w, val):
        self.center = self.backupcenter
        
        self.canvas.clear()
        with self.canvas:
            Rectangle(texture=self.texture, pos=self.pos, size=val)



    def on_pos(self, w, val):
        
        self.canvas.clear()
        with self.canvas:
            Rectangle(texture=self.texture, pos=val, size=self.size)


class Video3D(Widget3D):
    
    def __init__(self, **kwargs):
        super(Video3D, self).__init__(**kwargs)
        self.source = kwargs.get('source', None)
        
        if self.source != None:
            self._video = Video(source=self.source)
            
            self.add_widget(self._video)
       
class rotatingImage(Image3D):
    def __init__(self, **kwargs):
        super(rotatingImage, self).__init__(**kwargs)
        self.reanimate(None, 0)   
        
    def reanimate(self, w, val):
        self.rotate_z = 0
        
        anim = Animation(rotate_z=360, duration=60)
        
        anim.bind(on_complete=self.reanimate)
        anim.start(self)
        
class rotatingPoints(Widget3D):
    '''
    Example of make 3D points animation (based on 3Drendering and canvas/mesh examples)
    '''
    
    
    r = NumericProperty(1)
    g = NumericProperty(1)
    b = NumericProperty(1)
    
    color3D = ReferenceListProperty(r, g, b)
    '''
    Color of this widget
    '''
    
    def __init__(self, **kwargs):
        
        
        super(rotatingPoints, self).__init__(size_hint=(None,None), 
                                                size=(10,10), 
                                                pos=(-5, -5), 
                                                pos3D=kwargs.pop('pos3D', (0,0,-15)),
                                                rotate3D=(0,0,0),
                                                **kwargs)
        
        self.color3D = kwargs.get('color', (1, 1, 1))
        
        #you only need draw in 3D
        with self.canvas:
            self.color = Color(self.r, self.g, self.b)
            self.mesh = self.build_mesh()
            
        self.reanimate(None, 0)
            
    def build_mesh(self):
        vertices = []
        indices = []
        step = 20
        istep = (pi * 2) / float(step)
        xpos = 0
        ypos = 0
        for i in range(step):
            x = xpos + cos(istep * i) * 1
            y = ypos + sin(istep * i) * 1
            #vertices.extend([x, y, 0, 0])
            vertices.extend([x, y])
            indices.append(i)
            
            #return Point(points=vertices, pointsize=2)
        #return Line(points=vertices)
        return Mesh(vertices=vertices, indices=indices, mode='points', pointsize=8)
        
        
        
    def reanimate(self, w, val):
        self.rotate_y = 0
        self.rotate_z = 0
        
        #anim = Animation(rotate_z=360, duration=3)
        anim = Animation(rotate_y=360, rotate_z=360, duration=3)
        
        anim.bind(on_complete=self.reanimate)
        anim.start(self)
        
class Circle(Widget3D):
    '''
    Circle without PI
    
    x = sqrt ( r² - y² )
    y = sqrt ( r² - x² )
    '''
    
    def __init__(**kwargs):
        super(Circle, self).__init__(**kwargs)
        
        self.radius = 5
        

class Loading(Image3D):
    def __init__(self, **kwargs):
        super(Loading, self).__init__(size_hint=(None, None), **kwargs)
        #self.center = (0,0)
        self.pos_z = -100
        self.reanimate()
        
    def reanimate(self, anim=None, w=None):
        self.rotate_z = 0
        self.anim = Animation(rotate_z=360, duration=3)
        self.anim.bind(on_complete=self.reanimate)
        self.anim.start(self)
    
if __name__ == '__main__':
    from kivy.base import runTouchApp
    from kivy.uix.video import Video
    import sys
    
    #runTouchApp( Widget3D( pos3D=(0,0,-15), rotate3D=(0,45,0) ) )
    #runTouchApp( rotatingPoints( pos3D=(0,0,-15), rotate3D=(0,0,0) ) )
    
    lay = Edit3D()
    #lay.add_widget(Image3D(source='default.png', pos3D=(0,0,-10)))
    #lay.add_widget(Button(text='bnada'))
    
    rp = Image3D(source='cover.png')
    #rp.to2d()
    
    lay.add_widget(rp)
    
    
    #lay.add_widget(rotatingImage(source='cover.png', pos3D=(17.5,-6,-20)) )
    
    #lay.add_widget(LoginLogo( pos3D=(0,0,-5) ) )
    
    #lay_zoom = ZoomLayout3D()
    
    #lay_zoom.add_widget(rotatingImage(source='netget_logo.png') )
    #lay_zoom.add_widget(Video3D(source=sys.argv[1]) )
    
    #lay.add_widget(lay_zoom)
    
    runTouchApp(lay)
    
