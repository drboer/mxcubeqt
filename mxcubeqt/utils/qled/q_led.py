#pylint: skip-file

from mxcubeqt.utils import qt_import
from mxcubeqt.utils.qled.qled_resources import *


class QLed(qt_import.QWidget):
    def __init__(self, *args):

        qt_import.QWidget.__init__(self, *args)
        self.value = False

        self.username = None
        self.message = None

        self.on_color = "green"
        self.off_color = "grey"

        self.shape = "circle"

        self.shapes = ["circle", "square", "triang", "round"]
        self.colors = ["red", "green", "yellow", "grey", "orange", "purple", "blue"]
        self.renderer = qt_import.QSvgRenderer()
        self.setOff()

    def setUserName(self, name):
        self.username = name
        self._update()

    def setFixedSize(self, width, height):
        self.setFixedWidth(width)
        self.setFixedHeight(height)

    def setMessage(self, msg):
        self.message = msg
        self._update()

    def paintEvent(self, ev):
        painter = qt_import.QPainter(self)
        painter.setRenderHint(qt_import.QPainter.Antialiasing, True)

        self.filename = ":/resources/%s_%s.svg" % (self.shape, self.color)

        self.renderer.load(self.filename)
        self.renderer.render(painter)

    def setOnColor(self, color):
        self.on_color = color

    def setOffColor(self, color):
        self.off_color = color

    def setShape(self, shape):
        self.shape = shape

    def setOn(self):
        self.setState(True)

    def setOff(self):
        self.setState(False)

    def setState(self, value):
        self.value = value
        if self.value:
            self.color = self.on_color
            self.message = "On"
        else:
            self.color = self.off_color
            self.message = "Off"
        self._update()

    def toggle(self, value):
        self.value != value
        self._update()

    def setShape(self, shape):
        self.shape = shape
        self._update()

    def setColor(self, color):
        self.shape = shape
        self._update()

    def setShapeAndColor(self, shape, color):
        self.shape = shape
        self.color = color
        self._update()

    def _update(self):
        if self.username:
            _msg = self.username
        else:
            _msg = ""

        if self.message:
            _msg += ". " + self.message
        self.setToolTip(_msg)

        self.repaint()


if __name__ == "__main__":
    app = qt_import.QApplication([])
    win = qt_import.QMainWindow()
    wid = QLed()
    wid.setOn()
    win.setCentralWidget(wid)
    win.show()
    app.exec_()
