# std
import sys
import re
import math
from xml.etree import ElementTree
from pprint import pprint

# qt
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2.QtWidgets import QMainWindow, QApplication, QLineEdit, QFileDialog, QListWidget, QListWidgetItem
import qdarkstyle

# mine
from ui.main_window import Ui_MainWindow
import models


brush_b_enabled = QtGui.QBrush(QtGui.QColor(0, 85, 0))
brush_b_enabled.setStyle(QtCore.Qt.SolidPattern)

brush_b_disabled = QtGui.QBrush(QtGui.QColor(170, 0, 0))
brush_b_disabled.setStyle(QtCore.Qt.SolidPattern)

brush_b_removed = QtGui.QBrush(QtGui.QColor(71, 71, 71))
brush_b_removed.setStyle(QtCore.Qt.BDiagPattern)
brush_f_removed = QtGui.QBrush(QtGui.QColor(170, 170, 170))
brush_f_removed.setStyle(QtCore.Qt.SolidPattern)


profiles_source = []
profiles_target = []
profiles_merged = []

class ProfileItem(QListWidgetItem):
    def __init__(self,id:str, item_data:dict, item_enabled=False, *args, **kwargs):
        super().__init__()
        self.id = id
        self.setText(id)
        self.item_data = item_data
        self.item_enabled = item_enabled

    @property
    def item_enabled(self):
        return self.__item_enabled
    @item_enabled.setter
    def item_enabled(self, value: bool):
        self.__item_enabled = value
        if value:
            self.setBackground(brush_b_enabled)
        else:
            self.setBackground(brush_b_disabled)


class ProfileScanner(QtCore.QThread):
    # Progress Signal
    updateProgress = QtCore.Signal(int)
    addItem = QtCore.Signal(dict)

    def __init__(self, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.profile_filepath = ''

    # Overloaded, is run by calling its start() function
    def run(self):
        tree = ElementTree.parse(self.profile_filepath)
        root = tree.getroot()

        ns_pattern = '^{.*}'
        ns_re = re.compile(ns_pattern)

        tag = ''
        print(len(root))

        val = 0
        index = 0
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

                profile_field.set_fields(fields)

                toggles = profile_field.get_toggles()
                if toggles:
                    for key, value in toggles.items():
                        label = f'{str(profile_field)} --- {key}:{value}'
                        item = ProfileItem(label, {'data':'hola'}, value)
                        self.addItem.emit({
                            'label': label,
                            'obj': profile_field,
                            'item': item,
                            'index': index
                        })
                        index += 1
                else:
                    label = f'{str(profile_field)}'
                    self.addItem.emit({
                        'label': label,
                        'obj': profile_field,
                        'index': index
                    })
                    index +=1
            #tag = profileField.tag
        #self.updateProgress.emit(999)
    


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        ui = self.ui
        ui.setupUi(self)
        #ui.bar_loading.hide()
        
        self.ui.list_source.item(0).setBackground(brush_b_enabled)
        self.ui.list_source.item(1).setBackground(brush_b_disabled)
        self.ui.list_source.item(3).setBackground(brush_b_removed)
        self.ui.list_source.item(3).setForeground(brush_f_removed)
        

        ui.btn_source.clicked.connect(lambda: self.find_profile_file(ui.le_source, ui.list_source))
        ui.btn_target.clicked.connect(lambda: self.find_profile_file(ui.le_target, ui.list_target))

        ui.btn_start.clicked.connect(lambda: pprint(profiles_source[0]))

        ui.list_source.itemClicked.connect(self.itemClicked)

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

    def itemClicked(self, value:QListWidgetItem):
        pprint(value.__dict__)

    def addItem(self, newItem: dict):
        if self.list_target:
            if not newItem.get('item'):
                self.list_target.addItem(newItem['label'])
            else:
                self.list_target.addItem(newItem['item'])

            if self.list_target == self.ui.list_source:
                profiles_source.append(newItem)
            elif self.list_target == self.ui.list_target:
                profiles_target.append(newItem)
            if self.list_target == self.ui.list_merged:
                profiles_merged.append(newItem)


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

            list_target.clear()
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
