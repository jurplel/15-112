from cmu_112_graphics import *

from menu import *
from game import *
from multiplayer import *

def changeMode(app, mode):
    app.mode = mode
    if app.mode == "game":
        startGame(app)
    elif app.mode == "multiplayer":
        startMultiplayer(app)
    elif app.mode == "menu":
        startMenu(app)

def appStarted(app):
    pygame.mixer.init()
    pygame.mixer.music.set_volume(0.4)
    app._title = "fps112"
    app.changeMode = changeMode
    app.changeMode(app, "menu")

def main():
    width = 1280
    height = 720
    runApp(width=width, height=height)

if __name__ == '__main__':
    main()
