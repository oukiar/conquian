
'''
Las netgevars son "Variables" que  se actualizan automaticamente a
nivel cloud, usando la tecnologia disponible de sincronizacion.

El entorno de sesion y accesso a los datos es realizado on-the-fly.

Operaciones:
Extends o Create: Usado para crear o fabricar objetos de una determinada clase, pero con las bondades de Netget ngvars
Query o Search: Usado para hacer busqueda en base a condiciones prefedinidas con las funciones constraints

Neurons art & technology 2012-2015
'''


'''
Acerca de la sincronizacion inicial.

Se usara la solucion de php como backend inspirada en parse.
'''

'''

Seguridad: Algoritmo de encriptacion
    https://github.com/jedisct1/libsodium
    
    
'''

from kivy.properties import StringProperty, NumericProperty
from kivy.uix.widget import Widget
import json

from devslib.utils import Request   #for made http requests to any webserver

class NGVar(Widget):
    varname = StringProperty()
    vartype = StringProperty('Universal')
    data = StringProperty() #in json format
    objectId = NumericProperty(-1)
    appId = StringProperty()
    appKey = StringProperty()
    serverUrl = StringProperty('http://www.devsinc.com.mx/ngcloud/')   #the digital ocean netget server
    
        
    def save(self, **kwargs):
        
        callback = kwargs.pop('callback', self.res_save)
        
        datadict = kwargs.copy()
        datadict.update({'objectId':self.objectId,
                                'appId':self.appId,
                                'appkey':self.appKey,
                                'varname':self.varname
                                })
        
        #enviar peticion de creacion ... php backend por ahora
        Request(action=self.serverUrl + 'extends.php', 
                data=datadict, 
                callback=callback)
        
    def res_save(self, response):
        print response
    
    def get(self, **kwargs):
        
        callback = kwargs.pop('callback', self.res_get)
        
        datadict = kwargs.copy()
        datadict.update({'objectId':self.objectId,
                                'appId':self.appId,
                                'appkey':self.appKey,
                                'varname':self.varname
                                })
        
        #enviar peticion de search query
        Request(action=self.serverUrl + 'select.php', 
                data=datadict, 
                callback=callback)
                
    def res_get(self, response):
        print response
        
    def query(self, **kwargs):
        
        pass
        
        
class NGFile(Widget):
    '''
    NGFile representa un archivo netget que actualiza su contenido
    automaticamente en cloud del app y sesion donde sea creado.
    '''
    pass
    
class NGFactory(Widget):
    
    serverUrl = StringProperty('http://www.devsinc.com.mx/ngcloud/')
    
    def Connect(self):
        pass

    def Extends(self, name, **kwargs):
        return NGVar(varname=name, serverUrl=self.serverUrl, **kwargs)

    def Search(self, **kwargs):
        callback = kwargs.pop('callback', self.res_search)
        
        datadict = kwargs.copy()
        datadict.update({'collection':kwargs.get('collection'),
                                'conditions':json.dumps(kwargs.get('conditions', {})),
                                'like':kwargs.get('like', ''),
                                'cols':kwargs.get('cols', '*')
                                })
        
        #enviar peticion de search query
        Request(action=self.serverUrl + 'select.php', 
                data=datadict, 
                callback=callback)
                
    def res_search(self, response):
        print "Search response: ", response
        
    def Save(self, ngvar):
        ngvar.save()
        
    def Delete(self):
        pass

if __name__ == '__main__':
    
    factory = NGFactory()
    ngvar = factory.Extends('Users')
    
    print "Name: "
    name = raw_input()
    
    print "email: "
    email = raw_input()
    
    ngvar.save(Name=name, Email=email)
    
    print "Search using factory: ", factory.Search(collection="Users")
    #print "Thow ngvar object: ", ngvar.query()
    
    from kivy.base import runTouchApp
    
    runTouchApp(ngvar)
    
