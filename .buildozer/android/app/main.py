
'''
Faltantes:

Lista de partidas activas y en progreso


'''

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.popup import Popup
from kivy.uix.bubble import Bubble

import os
from datetime import date, datetime, time, timedelta

import json

from devslib.widget3D import Widget3D, Image3D, rotatingPoints

from devslib.utils import *

from devslib.listbox import ListBox

from functools import partial

#parse stuff
from parse_rest.connection import register, ParseBatcher
from parse_rest.datatypes import Object
from parse_rest.user import User

from kivy.core.window import Window

Window.set_icon("oros.png")

#parse initialization
register("D75yTmAfqHv8Zblpvq3vQ8Nb68RTq8yCJhynyIt1", "ce28KxuesyTf2X3pxzkyHj2QZfSuWRwo9c2NjuQv")

Partidas = Object.factory("Partidas")
Chat = Object.factory("Chat")

from threading import Thread
from time import sleep

'''
Partidas:
- Un usuario solo puede crear una partida en un determinado momento
-
'''

class PartidasThread(Thread):
     def __init__(self, **kwargs):
         self.callback = kwargs.pop('callback')
         self.stop = False
         super(PartidasThread, self).__init__()

     def run(self):
         while self.stop == False:
             sleep(5)
             print 'Obteniendo partidas'
             partidas = Partidas.Query.all()
             Clock.schedule_once(partial(self.callback, partidas), 0)


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

class Login(AnchorLayout):
    nickname = ObjectProperty()
    message = ObjectProperty()

class Principal(BoxLayout):
    lst_partidas = ObjectProperty()

class Game(BoxLayout):
    pass

class ChatMsg(Label):
    pass

class GameItem(Bubble):
    def do_action(self):
        print self.btn_action.text

class GameSelector(BoxLayout):
    def init_game(self):
        #search games
        print Partidas.Query.all().filter(Status_eq="Ready")


    
class CreateGame(Popup):
    def do_game(self):

        nick = "nobody" + str(len(User.Query.all())).zfill(4)
        app.root.user = User.signup(nick, "012345679", nickname=nick)
        self.dismiss()
        
        
        self.partida = Partidas()
        self.partida.Creator = app.root.user
        self.partida.Gametag = self.gametag.text
        self.partida.Status = "Ready"
        self.partida.save()

        '''
        #remove old timeoff games waiting
        now = datetime.now()
        lastmins = now - timedelta(minutes=3)
        
        print "Now: ", now
        print "Mins: ", lastmins

        partidas = Partidas.Query.filter(createdAt__lte=lastmins)
        
        print partidas
        
        batcher = ParseBatcher()
        batcher.batch_delete(partidas)
        '''

        #crear selector de juego
        app.root.games = GameSelector()
        app.root.add_widget(app.root.games)

        app.root.gamelist = Partidas.Query.all().order_by("-createdAt")

        #games list
        for i in app.root.gamelist:
            game = GameItem()


            game.by.text = i.Creator.nickname
            game.gametag.text = i.Gametag


            if i.Creator.nickname == nick:
                game.btn_action.text = "Cancel game"

            app.root.games.gamelist.add_widget(game)



class Lobby(BoxLayout):
    def crear_juego(self):
        app.root.remove_widget(app.root.lobby)
        
        CreateGame().open()
        

class Conquian(FloatLayout):
    
    '''
    Los dispositivos pueden estar en estado
    de espera, solicitando partida,
    
    Los dispositivos pueden mandarse requests de
    solicitud de partida.
    
    
    
    '''
    
    state = StringProperty()
    nick = StringProperty()
    login = ObjectProperty()

    
    def __init__(self, **kwargs):
        super(Conquian, self).__init__(**kwargs)

        self.puntos = 0
        
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


    def hide_controls(self):
        self.remove_widget(self.lay_cards)
        
        self.remove_widget(self.lay_main)
        self.remove_widget(self.lay_up)
        self.remove_widget(self.lay_rightbottom)

    def do_login(self):
        print 'login'


        try:
            self.user = User.signup(self.login.nickname.text, "12345", nickname=self.login.nickname.text)
            self.remove_widget(self.login)

            self.main = Lobby()
            self.add_widget(self.main)

            print "Loged"

            self.getpartidas = PartidasThread(callback=self.actualizar_partidas)
            self.getpartidas.start()

        except:
            self.login.message.text = 'Nickname already in use'
            print "Algo salio mal"

    def postMessage(self, msgtext):
        print msgtext.text

        msg = Chat()
        msg.Message = msgtext.text
        msg.PUser = self.user
        msg.save()

        print self.main.chat.messages.add_widget(ChatMsg(text=msgtext.text) )

        msgtext.text = ""
        msgtext.focus = True

    def crear_partida(self):

        mypartidas = Partidas.Query.filter(Creator__in=[self.user])

        if len(mypartidas) > 0:
            print "Ya hay partida creada"
            return

        partida = Partidas()
        partida.Creator = self.user
        partida.save()

        #self.actualizar_partidas()

    def actualizar_partidas(self, partidas, dt):
        self.main.lst_partidas.clear()

        #print partidas

        #partidas = Partidas.Query.all()

        for i in partidas:
            print i
            label = Label(text=i.Creator.nickname, height=40)
            self.main.lst_partidas.add_widget(label)



if __name__ == '__main__':
    #from kivy.base import runTouchApp


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
    
    #runTouchApp(Conquian() )

    from kivy.app import App


    class ConquianApp(App):
        def build(self):
            return Conquian()

    app = ConquianApp()
    app.run()
    #app.root.getpartidas.stop = True
    
