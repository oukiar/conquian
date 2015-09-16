
from kivy.uix.boxlayout import BoxLayout


class ChatMsg(BoxLayout):
    pass

class Chat(BoxLayout):

    def postMessage(self, msgtext):
        print msgtext.text

        msg = ChatMessages()
        msg.Message = msgtext.text
        #msg.PUser = self.user
        msg.save()

        print self.messages.add_widget(ChatMsg(text=msgtext.text) )

        msgtext.text = ""
        msgtext.focus = True


#parse stuff
try:
    ChatMessages = Object.factory("ChatMessages")
except:
    from parse_rest.connection import register, ParseBatcher
    from parse_rest.datatypes import Object
    from parse_rest.user import User

    #parse initialization
    register("D75yTmAfqHv8Zblpvq3vQ8Nb68RTq8yCJhynyIt1", "ce28KxuesyTf2X3pxzkyHj2QZfSuWRwo9c2NjuQv")

    ChatMessages = Object.factory("ChatMessages")


if __name__ == "__main__":
    from kivy.app import App

    class ChatApp(App):
        def build(self):
            return Chat()

    app = ChatApp()
    app.run()

