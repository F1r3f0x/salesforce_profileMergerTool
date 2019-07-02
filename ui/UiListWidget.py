from PySide2.QtWidgets import QListWidget
from PySide2.QtGui import QMouseEvent
from PySide2.QtCore import Qt
from pprint import pprint


class UiListWidget(QListWidget):

    def __init__(self, *args):
        return super().__init__(*args)

    def mouseReleaseEvent(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)

        if event.button() == Qt.RightButton:
            clickedItem = self.itemAt(event.pos())
            if clickedItem:
                clickedItem.setSelected(False)
                if clickedItem.toggle_value is not None:
                    clickedItem.toggle_value = not clickedItem.toggle_value

