# std
import sys
import re
import math
from xml.etree import ElementTree

# qt
from PySide2 import QtCore
from PySide2.QtWidgets import QMainWindow, QApplication, QLineEdit, QFileDialog, QListWidget
import qdarkstyle

# mine
from ui.main_window import Ui_MainWindow
import models

class ProfileScanner(QtCore.QThread):
    # Progress Signal
    updateProgress = QtCore.Signal(int)
    addItem = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.profile_filepath = ''

    # Overloaded, is run by calling it's start() function
    def run(self):
        tree = ElementTree.parse(self.profile_filepath)
        root = tree.getroot()

        ns_pattern = '^{.*}'
        ns_re = re.compile(ns_pattern)

        tag = ''
        print(len(root))

        val = 0
        for profileField in root:
            ns = ns_re.match(profileField.tag).group()
            fieldType = profileField.tag.replace(ns,'')

            """
            if profileField.tag != tag:
                print('tag: ', profileField.tag)
                print('namespace: ', ns)
                print('fieldType: ', profileField.tag.replace(ns,''))
                print('attribute: ', profileField.attrib)
            """

            # Get class
            model_class = models.classes_by_modelName.get(fieldType)
            if model_class:
                fields = {}
                for child in profileField:
                    tag = child.tag.replace(ns,'')
                    fields[tag] = child.text

                profile_field = model_class()

                #print(fields)
                profile_field.set_fields(fields)

                toggles = profile_field.get_toggles()
                if toggles:
                    for key, value in toggles.items():
                        self.addItem.emit(f'{str(profile_field)} --- {key}:{value}')
                else:
                    self.addItem.emit(f'{str(profile_field)}')
            #tag = profileField.tag
        #self.updateProgress.emit(999)
    


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        ui = self.ui
        ui.setupUi(self)
        ui.bar_loading.hide()

        ui.btn_source.clicked.connect(lambda: self.find_profile_file(ui.le_source, ui.list_source))
        ui.btn_target.clicked.connect(lambda: self.find_profile_file(ui.le_target, ui.list_target))

        self.scanner_worker = ProfileScanner()
        self.scanner_worker.addItem.connect(self.addItem)

    """
    def updateProgressBar(self, val: int):
        progress_bar = self.ui.bar_loading

        if val < 100:
            self.ui.btn_target.setEnabled(False)
            self.ui.btn_source.setEnabled(False)


        if not progress_bar.isVisible() and val < 100:
            progress_bar.setVisible(True)
        elif val == 999:
            progress_bar.hide()
            self.ui.btn_target.setEnabled(True)
            self.ui.btn_source.setEnabled(True)

        self.ui.bar_loading.setValue(val)
    """

    def addItem(self, newLabel: str):
        if self.list_target:
            self.list_target.addItem(newLabel)


    # Uses open file dialog to setup a filename
    def find_profile_file(self, le_target: QLineEdit, list_target: QListWidget):
        file_path, _filtro = QFileDialog.getOpenFileName(
            self,
            'Pick your Profile A',
            '',
            '*.xml *.profile'
        )

        if file_path != '' and le_target:
            le_target.setText(file_path)

            self.list_target = list_target
            self.scanner_worker.profile_filepath = file_path
            self.scanner_worker.start()

        return file_path


if __name__ == "__main__":
    app = QApplication([])
    
    # Setup Dark Theme
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside())

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
