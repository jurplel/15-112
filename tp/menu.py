from tkinter import Text

import fpsgameutil
import ply_importer

import time, math

import numpy as np

def resetSizeVars(app):
    app.menuItemX = app.width/50
    app.menuItemY = app.height*0.75
    app.menuItemDY = app.height/20
    app.settingsMargin = max(app.width, app.height)/10

def startMenu(app):
    app.mode = "menu"
    app.menuItemWidthGuess = 200
    app.menuItems = ["start", "multiplayer", "quit"]
    resetSizeVars(app)

    app.highlightedMenuItem = None

    app.showingSettings = False

    app.fovTextBox = Text(app._root, width=10, height=1)

    # Adjust actual user-configurable settings just for this scene
    app.wireframe = True
    app.fov = 10

    # Initialize the bloat
    fpsgameutil.initFps(app)

    # Add textlogo mesh to drawables
    textlogo = ply_importer.importPly("res/logo.ply")
    textlogo.setColor(fpsgameutil.Color(255, 0, 0))
    app.drawables.append(textlogo)
    app.drawables[0].rotateY(-20)


    # Setup camera and lighting
    app.cam = np.array([0, 0, 10, 1], dtype=np.float64)
    app.light = np.array([-1, -0.5, -1, 0], dtype=np.float64)
    fpsgameutil.ddd.normVec(app.light)

    app.yaw = 180
    fpsgameutil.recalculateCamDir(app)
    


def menu_sizeChanged(app):
    fpsgameutil.fpsSizeChanged(app)
    resetSizeVars(app)

def menu_mouseMoved(app, event):
    app.highlightedMenuItem = None

    if event.x > app.menuItemX and event.x < app.menuItemX+app.menuItemWidthGuess:
        for i in range(len(app.menuItems)):
            if event.y > app.menuItemY+app.menuItemDY*i and event.y < app.menuItemY+app.menuItemDY*(i+1):
                app.highlightedMenuItem = i
                break

def menu_mouseReleased(app, event):
    if app.highlightedMenuItem != None:
        itemText = app.menuItems[app.highlightedMenuItem]
        if itemText == "start":
            app.changeMode(app, "game")
        elif itemText == "multiplayer":
            app.changeMode(app, "multiplayer")
        elif itemText == "options":
            app.showingSettings = True
        elif itemText == "quit":
            exit()

def menu_timerFired(app):
    deltaTime = time.time() - app.lastTimerTime

    # Keep on spinning
    theta = 6*deltaTime
    app.drawables[0].rotateY(theta)

    # Go up and down a little
    upDownStep = math.sin(time.time())*0.001

    app.drawables[0].translate(0, upDownStep, 0)
    app.lastTimerTime = time.time()

def menu_redrawAll(app, canvas):
    fpsgameutil.redraw3D(app, canvas)
    
    # menu items
    for i, menuItem in enumerate(app.menuItems):
        color = "DeepSkyBlue2" if i == app.highlightedMenuItem else "black"
        canvas.create_text(app.menuItemX, app.menuItemY+app.menuItemDY*i, 
                            text=menuItem, font="Ubuntu 24 italic", 
                            anchor="nw", fill=color)