# This Python file uses the following encoding: utf-8
import sys
import os

from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine

from q_and_a import QAndA
from timerAndSanityAndHanger import TimeElapsed, Sanity, Hanger, PhysicalHealth


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    qAndAObj = QAndA()
    timeElapsed = TimeElapsed()
    sanity = Sanity()
    hanger = Hanger()
    physicalHealth = PhysicalHealth()

    engine.rootContext().setContextProperty("qanda", qAndAObj)
    engine.rootContext().setContextProperty("timeElapsed", timeElapsed)
    engine.rootContext().setContextProperty("sanity", sanity)
    engine.rootContext().setContextProperty("hanger", hanger)
    engine.rootContext().setContextProperty("physicalHealth", physicalHealth)

    engine.load(os.path.join(os.path.dirname(__file__), "main.qml"))


    sys.exit(app.exec_())