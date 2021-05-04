#IMPORTS
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.uix.behaviors import ToggleButtonBehavior
import os
import time
import datetime
from kivy.uix.popup import Popup
from kivy.core.audio import SoundLoader
from kivy.core.audio import Sound
from kivy_garden.zbarcam import ZBarCam
from time import strftime
from  kivy.event import EventDispatcher
from pyzbar.pyzbar import ZBarSymbol
import multiprocessing
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.base import runTouchApp

#MainApp KVLANG
alarm = """
<Home@Screen>:
    BoxLayout:
        orientation: 'vertical'
        MyClock:
            font_size: 50
            text: self.current_time
        Button:
            background_color: (128,0,0,.6)
            background_down: '(0, 0, .3, 1)'
            text: 'Set Alarm'
            on_press: root.manager.current = 'alarm_page'
<AlarmPage@Screen>:
    GridLayout:
        rows: 4
        Button:
            text: 'Alarm 1'
            on_release: root.manager.current = 'edit1_page'  
                                
        Button:
            text: 'Alarm 2'
            on_release: root.manager.current = 'edit2_page'
               
        Button:
            text: 'QR Code Scanner'
            on_release: root.manager.current = 'qrAPP' 
   
<AlarmEdit>:
    BoxLayout:
        orientation: 'vertical'
        GridLayout:
            cols: 4  
            Label:
                text: 'Set Time (00:00):'
            TextInput:
                id: alarmtime
                text: root.alarm_time
            ToggleButton:
                text: 'AM'
                group:'am/pm'
                state: root.alarm_am_state
                on_state: root.alarm_am_state = self.state
            ToggleButton:
                text: 'PM'
                group:'am/pm'
                state: root.alarm_pm_state
                on_state: root.alarm_pm_state = self.state
        Button:
            text: "Set Alarm"
            on_press: 
                root.set_alarm()
                root.manager.current = 'home_page'
BoxLayout:
    ScreenManager:
        id: sm
        Home:
            name: 'home_page'
        AlarmPage:
            name: 'alarm_page'
        AlarmEdit:
            name: 'edit1_page'
        AlarmEdit:
            name: 'edit2_page'  
    """

#QR_App KVLANG
QR = """
#:import ZBarCam kivy_garden.zbarcam.ZBarCam
#:import ZBarSymbol pyzbar.pyzbar.ZBarSymbol
<Reader>
    BoxLayout:
        orientation: 'vertical'
        ZBarCam:
            id: zbarcam
            # optional, by default checks all types
            code_types: ZBarSymbol.QRCODE, ZBarSymbol.EAN13
        TextInput:
            id: decode
            text: ', '.join([str(symbol.data) for symbol in zbarcam.symbols])
            on_text: root.kill_alarm()
BoxLayout:
    ScreenManager:
        id: sm
        Reader:
            name: 'QRcode_reader'
"""

#CLOCK
class MyClock(Label):
    current_time = StringProperty(strftime("%I:%M:%S %p"))

    def __init__(self, **kwargs):
        Clock.schedule_interval(self.update_time, 1)
        super().__init__(**kwargs)

    def update_time(self, dt):
        self.current_time = strftime("%I:%M:%S %p")
        app = App.get_running_app()
        t1 = app.root.ids.sm.get_screen('edit1_page').alarm(self.current_time)

#KILL ALARM WITH QR CODE
class Reader(Screen): 
    def close(self): 
         App.get_running_app().stop()
         Window.close()

    def kill_alarm(self):
         QRcode = self.ids.decode.text
         if QRcode:
             self.close()

#ALARM 
class AlarmEdit(Screen):  
    alarm_time = StringProperty()
    alarm_am_state = StringProperty('down') 
    alarm_pm_state = StringProperty('normal')
    def alarm(self, current_time):
            am_pm = {'down': 'AM', 'normal': 'PM'}[self.alarm_am_state]
            a_time = f'{self.alarm_time}:00 {am_pm}'
            if a_time[1] == ':':  # if the : is the second char,a leading zero is missing, insert it.
                a_time = '0' + a_time
            print(f'a: {a_time} ct: {current_time}')  # test to watch the time
            if a_time == current_time:
                popup = Popup(title='Alarm 1', content=Label(text=self.alarm_time), size_hint=(None, None), size=(400, 400))
                b = multiprocessing.Process(target=open_child)
                start = b.start()
                popup.on_open:(start)
                popup.open()
                      
    #SET ALARM                  
    def set_alarm(self):
        self.alarm_time = self.ids.alarmtime.text
        with open("alarm1_details.txt", "w") as f:
            f.write(f"{self.ids.alarmtime.text},{self.alarm_am_state},{self.alarm_pm_state}")

#GET ALARM TIME          
def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if os.path.isfile("alarm1_details.txt"):
         with open("alarm1_details.txt", "r") as f:
            d = f.read().split(",")
        self.alarm_time = d[0]
        self.alarm_am_state = d[1]
        self.alarm_pm_state = d[2]

#AM/PM BUTTONS
class MyButton(ToggleButtonBehavior, Label, Image):
    def __init__(self, **kwargs):
        super(MyButton, self).__init__(**kwargs)
        self.source = 'atlas://data/images/defaulttheme/checkbox_off'

    def on_state(self, widget, value):
        if value == 'down':
            self.source = 'atlas://data/images/defaulttheme/checkbox_on'
        else:
            self.source = 'atlas://data/images/defaulttheme/checkbox_off'

#RUN APP
def open_parent():
    MainApp().run()

def open_child():
    sound = SoundLoader.load('C:/Users/labservices/Downloads/earthgang-up.mp3')
    sound.loop = True
    sound.play()
    QR_App().run()

class MainApp(App):
    def build(self):
        return Builder.load_string(alarm)

class QR_App(App):
        def build(self):
            return Builder.load_string(QR)

if __name__ == "__main__":
    a = multiprocessing.Process(target=open_parent)
    a.start()
    b = multiprocessing.Process(target=open_child)
    runTouchApp()
