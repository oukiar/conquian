
'''
Faltantes:

Lista de partidas activas y en progreso


'''

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.popup import Popup


import os


import json

from widget3D import Widget3D, Image3D, rotatingPoints

from utils import *

from listbox import ListBox

class CrearPartida(Popup):
    
    def __init__(self, **kwargs):
        super(CrearPartida, self).__init__(title='Creando nueva partida', size_hint=(None, None), size=(500,200), **kwargs)
        
        self.content = BoxLayout(orientation='vertical')
        
        self.content.add_widget(Label(text='Estas creando una nueva partida, por favor introduce tu apuesta', size_hint_y=None, height=60) )

        #APUESTA
        self.txt_apuesta = TextInput(text='5')
        self.content.add_widget(self.txt_apuesta)

        #ACEPTAR
        self.btn_aceptar = Button(text='Aceptar')
        self.content.add_widget(self.btn_aceptar)


class Conquian(FloatLayout):
    
    '''
    Los dispositivos pueden estar en estado
    de espera, solicitando partida,
    
    Los dispositivos pueden mandarse requests de
    solicitud de partida.
    
    
    
    '''
    
    state = StringProperty()
    nick = StringProperty()

    
    def __init__(self, **kwargs):
        super(Conquian, self).__init__(**kwargs)
        

        self.puntos = 0
        
        #cargar id de dispositivo
        try:
            self.devID = open('devID').read()
        except:
            self.devID = '-1'
            
        self.server = 'http://www.devsinc.com.mx'
        
        
        Request(action=self.server + '/conquian/signin.php', 
                    callback=self.on_sign, 
                    data=urllib.urlencode({'devID':self.devID})
                    )
        
        
    def on_sign(self, res):
        
        print 'Sign response: ', res
        
        self.res = res
        Clock.schedule_once(self.on_res, 0)
        
        
        
        
    def on_res(self, dt):
        
        self.points = rotatingPoints()
        self.add_widget(self.points)
        
        if 'SIGNUP_OK' in self.res:
            p = alert('Welcome', 'Bienvenido al conquian online')
            p.bind(on_dismiss=self.create_gui)
            
            self.devID = self.res.split(' ')[1]
            self.puntos = 100
            
            
            #guardar id de dispositivo
            open('devID', 'w').write(self.devID)
            
            
            self.nick = 'conquianplayer' + self.devID
            
            
        elif 'SIGNIN_OK' in self.res:
            
            self.create_gui()
            
            tkns = self.res.split(' ')
            
            self.nick = tkns[1]
            self.puntos = int(tkns[2])
            self.txt_puntos.text = 'Puntos: ' + str(self.puntos)
            
        
    def on_nick(self, w, val):
        if hasattr(self, 'nickname'):
            self.nickname.text = val
            
            #update nick in the server
            self.save_nickname()
            
            
    def create_gui(self, w=None):
        
        #layout superior
        self.lay_up = AnchorLayout(anchor_x='center', 
                                    anchor_y='top',
                                    padding=5)

        self.nickname = ngTextInput(size_hint=(None,None), 
                                        size=(300,50), 
                                        pos=(500,100),
                                        text=self.nick)
        self.nickname.bind(on_enter=self.on_nickenter)
        self.lay_up.add_widget(self.nickname)

        self.add_widget(self.lay_up)
        
        #layout inferior derecha
        self.lay_rightbottom = AnchorLayout(anchor_x='right', 
                                    anchor_y='bottom',
                                    padding=0)
        
        self.txt_puntos = Label(text='Puntos: ',
                                        size_hint=(None,None), 
                                        size=(300,50))
        self.lay_rightbottom.add_widget(self.txt_puntos)
        
        self.add_widget(self.lay_rightbottom)
        
        #layoutprincipal, aqui va el chat y lo que vaya del otro lado que no sean las cartas
        self.lay_main = BoxLayout()
        self.add_widget(self.lay_main)
        
        #listbox con gente conectada
        self.people = ListBox(size_hint_x=.35, widget_cls=Button)
        self.lay_main.add_widget(self.people )
        
        #CREAR PARTIDA
        self.btn_crearpartida = Button(size_hint=(None,None), 
                                        size=(200,60), 
                                        text='Crear partida')
        self.btn_crearpartida.center = (Window.center[0], 70)
        self.btn_crearpartida.bind(on_press=self.on_crearpartida)
        self.lay_main.add_widget(self.btn_crearpartida)
        
        #JUGAR
        self.btn_jugar = Button(size_hint=(None,None), 
                                        size=(200,60), 
                                        text='Jugar')
        self.btn_jugar.center = (Window.center[0], 140)
        self.btn_jugar.bind(on_press=self.on_jugar)
        self.lay_main.add_widget(self.btn_jugar)
        
        #obtener la lista de dispositivos para jugar
        Request(action=self.server + '/conquian/get_devices.php', 
                    callback=self.on_devices, 
                    data=urllib.urlencode({'devID':self.devID})
                    )
        
        #crear tarjetas
        self.create_cards()
        
        
    def on_devices(self, val):
        print '---------DEVICES'
        print val
        
        self.devices = json.loads(val)
        
        for dev in sorted(self.devices):
            print dev
            print self.devices[dev]['devID']
            print self.devices[dev]['lu']
            
            self.people.add_item(text=dev)
        
    def on_nickenter(self, w):
        print 'enter'
        
    def save_nickname(self):
        pass
        
    def create_cards(self, dt=None):
        #guardaremos las cartas en un diccionario
        self.cards = {}
        
        self.scartas = sorted(os.listdir('cartas'))
        self.curcarta = 0
        
        #meter todas las cartas en un layout para poder mostrarlas y ocultarlas
        self.lay_cards = FloatLayout()
        
        self.add_widget(self.lay_cards)
        
        Clock.schedule_once(self.next_card, .3)
        
    def next_card(self, dt):
                
        i = self.scartas[self.curcarta]
                
        self.cards[i] = {'file': i, 'image':Image3D(source=os.path.join('cartas', i))}
        
        #smoth show
        fade_in(self.cards[i]['image'])
                
        self.lay_cards.add_widget(self.cards[i]['image'])
    
        if self.curcarta < len(self.scartas)-1:
            self.curcarta += 1
            Clock.schedule_once(self.next_card, .3)
        
        
    def on_jugar(self, w):
        
        #ocultar controles
        self.hide_controls()
                
        self.lb_centered = Label(text='Solicitando unirse al juego')
        self.add_widget(self.lb_centered)

        #hacer peticion de juego
        Request(action=self.server + '/conquian/start_game.php', 
                    callback=self.res_jugar, 
                    data=urllib.urlencode({'devID':self.devID})
                    )
                    
    def res_jugar(self, res):
        print res
        
        r = json.loads(res)
        
        #guardar el numero de partida
        self.npartida = str(r['partID'])
        
        self.lb_centered.text += '\nPartida numero: ' + self.npartida
        
        if r['player1ID'] != '0' and r['player1ID'] != self.devID:
            self.lb_centered.text += '\nJugador 1: ' + r['player1ID']
            
        elif r['player2ID'] != '0' and r['player2ID'] != self.devID:
            self.lb_centered.text += '\nJugador 2: ' + r['player2ID']
            
        elif r['player3ID'] != '0' and r['player3ID'] != self.devID:
            self.lb_centered.text += '\nJugador 3: ' + r['player3ID']
            
        elif r['player4ID'] != '0' and r['player4ID'] != self.devID:
            self.lb_centered.text += '\nJugador 4: ' + r['player4ID']
        
        self.btn_iniciarpartida = Button(text='Iniciar partida', 
                                        size_int=(None,None), 
                                        size=(300,80),
                                        )
        
                    
    def on_crearpartida(self, w):
        self.pop_crearpartida = CrearPartida()
        self.pop_crearpartida.btn_aceptar.bind(on_press=self.on_realcrearpartida)
        self.pop_crearpartida.open()
        
        #hacer el request al servidor
        Request(action=self.server + '/conquian/create_game.php', 
                    callback=self.res_crearpartida, 
                    data=urllib.urlencode({'devID':self.devID,
                                            'apuesta':self.pop_crearpartida.txt_apuesta.text})
                    )
                    
    def on_realcrearpartida(self, w):
    
        #ocultar controles
        self.hide_controls()
                
        self.lb_centered = Label(text='Creando partida')
        self.add_widget(self.lb_centered)
        
        #cerrar dialogo de crear partida
        self.pop_crearpartida.dismiss()

        #hacer el request al servidor
        Request(action=self.server + '/conquian/create_game.php', 
                    callback=self.res_crearpartida, 
                    data=urllib.urlencode({'devID':self.devID,
                                            'apuesta':self.pop_crearpartida.txt_apuesta.text})
                    )
                    
    def res_crearpartida(self, res):
                
        self.lb_centered.text += '\nPartida numero: ' + res + '\nEsperando jugadores'
        
        #guardar el numero de partida
        self.npartida = int(res)
        

    def hide_controls(self):
        self.remove_widget(self.lay_cards)
        
        self.remove_widget(self.lay_main)
        self.remove_widget(self.lay_up)
        self.remove_widget(self.lay_rightbottom)

if __name__ == '__main__':
    from kivy.base import runTouchApp


    '''
    from PIL import Image

    for carta in os.listdir('cartas'):
        
        print carta
        
        img = Image.open(os.path.join('cartas', carta) )
        img2 = img.resize((326,512), Image.ANTIALIAS)
        
        if img2.mode != "RGB":
            img2 = img2.convert("RGB")
        
        img2.save(os.path.join('cartas', carta) )
    '''
    
    runTouchApp(Conquian() )
    
