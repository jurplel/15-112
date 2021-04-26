from dataclasses import dataclass

def setMenuItemPos(app):
    app.menuItemX = app.width/50
    app.menuItemY = app.height/2
    app.menuItemDY = app.height/20

def startMenu(app):
    app.mode = "menu"
    app.menuItemWidthGuess = 100
    app.menuItems = ["start", "options", "quit"]
    setMenuItemPos(app)

    app.highlightedMenuItem = None

def menu_sizeChanged(app):
    setMenuItemPos(app)

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

def menu_redrawAll(app, canvas):
    # title
    canvas.create_text(app.width/2, app.height/5, text="fps112", font="Caveat 64 bold")

    # menu items
    for i, menuItem in enumerate(app.menuItems):
        color = "DeepSkyBlue2" if i == app.highlightedMenuItem else "black"
        canvas.create_text(app.menuItemX, app.menuItemY+app.menuItemDY*i, 
                            text=menuItem, font="Ubuntu 24 italic", 
                            anchor="nw", fill=color)