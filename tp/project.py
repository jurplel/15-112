from cmu_112_graphics import *

from menu import *
from game import *
from multiplayer import *

from util import readFile

import json

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
    loadOptions(app)
    app._title = "fps112"
    app.changeMode = changeMode
    app.changeMode(app, "menu")
    


def loadOptions(app):
    # load options from config file
    try:
        config = json.loads(readFile("config.json"))
    except:
        config = dict()

    app.fov = config.get("fov", 90)
    app.wireframe = config.get("wireframe", False)
    app.drawFps = config.get("drawFps", True)
    app.drawCrosshair = config.get("drawCrosshair", True)
    app.hudMargin = config.get("hudMargin", 40)
    app.mpAddr = config.get("ip", "0.0.0.0")
    app.mpPort = config.get("port", 52021)


def main():
    width = 1280
    height = 720
    runApp(width=width, height=height)

if __name__ == '__main__':
    main()
