# This Python file uses the following encoding: utf-8
import sys
from PySide2.QtWidgets import QMainWindow, QApplication
import qdarkstyle
from ui.main_window import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #self.ui.bar_loading.hide()

if __name__ == "__main__":
    app = QApplication([])
    
    # Setup Dark Theme
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside())

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
