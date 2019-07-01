from PySide2.QtWidgets import QListWidget
from PySide2.QtGui import QMouseEvent
from PySide2.QtCore import Qt
from pprint import pprint


class UiListWidget(QListWidget):

    def __init__(self, *args):
        return super().__init__(*args)

    def mouseReleaseEvent(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)

        print(event)
        print(event.buttons())
        print(event.button())
