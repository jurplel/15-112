from tkinter import Text

def resetSizeVars(app):
    app.menuItemX = app.width/50
    app.menuItemY = app.height/2
    app.menuItemDY = app.height/20
    app.settingsMargin = max(app.width, app.height)/10

def startMenu(app):
    app.mode = "menu"
    app.menuItemWidthGuess = 200
    app.menuItems = ["start", "quit"]
    resetSizeVars(app)

    app.highlightedMenuItem = None

    app.showingSettings = False

    app.fovTextBox = Text(app._root, width=10, height=1)

def menu_sizeChanged(app):
    resetSizeVars(app)
    # app.fovTextBox.place(x=app.width/2, y=app.height/2)

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
        elif itemText == "options":
            app.showingSettings = True
        elif itemText == "quit":
            exit()

def menu_redrawAll(app, canvas):
    # title
    canvas.create_text(app.width/2, app.height/5, text="fps112", font="Caveat 64 bold")

    # menu items
    for i, menuItem in enumerate(app.menuItems):
        color = "DeepSkyBlue2" if i == app.highlightedMenuItem else "black"
        canvas.create_text(app.menuItemX, app.menuItemY+app.menuItemDY*i, 
                            text=menuItem, font="Ubuntu 24 italic", 
                            anchor="nw", fill=color)

    # settings stuff
    # if not app.showingSettings:
    #     return

    # canvas.create_rectangle(app.settingsMargin, app.settingsMargin, app.width-app.settingsMargin, app.height-app.settingsMargin)
