from cmu_112_graphics import *

from menu import *
from game import *

def changeMode(app, mode):
    app.mode = mode
    if app.mode == "game":
        startGame(app)
    elif app.mode == "menu":
        startMenu(app)

def appStarted(app):
    pygame.mixer.init()
    app._title = "fps112"
    app.changeMode = changeMode
    app.changeMode(app, "menu")

def main():
    width = 1280
    height = 720
    runApp(width=width, height=height)

if __name__ == '__main__':
    main()
