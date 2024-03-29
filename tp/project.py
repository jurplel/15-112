# Entry point--holds appstarted, loads config options, and manages mode switches

from cmu_112_graphics import *

from menu import *
from game import *
from multiplayer import *

from util import readFile

import json

def changeMode(app, mode):
    loadOptions(app)
    app.mode = mode
    pygame.mixer.music.fadeout(1000)
    if app.mode == "game":
        startGame(app)
    elif app.mode == "multiplayer":
        startMultiplayer(app)
    elif app.mode == "menu":
        startMenu(app)

def appStarted(app):
    loadOptions(app)
    pygame.mixer.init()
    pygame.mixer.music.set_volume(app.musicVolume)
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
    app.musicVolume = config.get("musicVolume", 40)
    app.effectVolume = config.get("effectVolume", 40)
    app.turnSpeed = config.get("turnSpeed", 12)


def main():
    width = 1280
    height = 720
    runApp(width=width, height=height)

if __name__ == '__main__':
    main()
