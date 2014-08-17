import kivy
kivy.require('1.8.0')

from kivy.app import Widget, App
from kivy.uix.gridlayout import GridLayout

class Cell(GridLayout):
    pass

class GridCommand(GridLayout):
    pass

class GridCommandApp(App):
    def build(self):
        return GridCommand()

if __name__ == "__main__":
    GridCommandApp().run()
