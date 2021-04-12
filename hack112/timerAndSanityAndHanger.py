import time

from PySide2.QtCore import QObject, Slot

class TimeElapsed(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start=9
        self.initial = time.time()
        self.isNight = True

    @Slot(result=float)
    def returnRaw(self):
        return time.time() - self.initial
    
    @Slot(result=list)
    def returnInGameTime(self):
        #will return hours and minutes here for in game
        currTime = self.returnRaw()
        timeHrs = currTime/20+self.start
        if timeHrs>=12:
            self.start=-3

        if(timeHrs >= 7):
            self.isNight = False
        timeMins = (timeHrs-int(timeHrs))*60
        return [int(timeHrs), int(timeMins)]
    
    @Slot(result=str)
    def returnGameTimeString(self):
        gt = self.returnInGameTime()
        timeHrs = gt[0]
        timeMins = gt[1]
        return f'{timeHrs:02}:{timeMins:02}'

    @Slot(result=bool)
    def getIsNight(self):
        return self.isNight

#starts as a percentage
class Sanity(QObject):
    def __init__(self, orig = 100, parent=None):
        super().__init__(parent)
        self.sanity = orig
        self.isInsane = False
    
    @Slot(int)
    def decreaseSanity(self, amt):
        self.sanity -= amt
        if(self.sanity <= 0):
            self.sanity = 0
        if(self.sanity < 10):
            self.isInsane = True
    
    @Slot(int)
    def increaseSanity(self, amt):
        self.sanity += amt
        if(self.sanity >= 100):
            self.sanity = 100
        if(self.sanity > 10):
            self.isInsane = False

    @Slot(result=int)
    def getSanity(self):
        return self.sanity
    
class Hanger(QObject):
    def __init__(self, orig = 100, parent=None):
        super().__init__(parent)
        self.hanger = orig
        self.isHangry = False
    
    @Slot(int)
    def decreaseHanger(self, amt):
        self.hanger -= amt
        if(self.hanger <= 0):
            self.hanger = 0
        if(self.hanger < 10):
            self.isHangry = True
    
    @Slot(int)
    def increaseHanger(self, amt):
        self.hanger += amt
        if(self.hanger >= 100):
            self.hanger = 100
        if(self.hanger > 10):
            self.isHangry = False

    @Slot(result=int)
    def getHanger(self):
        return self.hanger

class PhysicalHealth(QObject):
    def __init__(self, orig = 100, parent=None):
        super().__init__(parent)
        self.health = orig
        self.isDying = False
    
    @Slot(int)
    def decreaseHealth(self, amt):
        self.health -= amt
        if(self.health <= 0):
            self.health = 0
        if(self.health < 10):
            self.isDying = True
    
    @Slot(int)
    def increaseHealth(self, amt):
        self.health += amt
        if(self.health >= 100):
            self.health = 100
        if(self.health > 10):
            self.isDying = False

    @Slot(result=int)
    def getHealth(self):
        return self.health