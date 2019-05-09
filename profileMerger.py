# std
import sys
import re
import math
from xml.etree import ElementTree
from pprint import pprint
from copy import copy, deepcopy

# qt
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2.QtWidgets import QMainWindow, QApplication, QLineEdit, QFileDialog, QListWidget, QListWidgetItem
import qdarkstyle

# mine
from ui.main_window import Ui_MainWindow
import models

# Brushes
brush_b_enabled = QtGui.QBrush(QtGui.QColor(0, 69, 0))
brush_b_enabled.setStyle(QtCore.Qt.SolidPattern)

brush_b_disabled = QtGui.QBrush(QtGui.QColor(69, 0, 0))
brush_b_disabled.setStyle(QtCore.Qt.SolidPattern)

brush_b_removed = QtGui.QBrush(QtGui.QColor(71, 71, 71))
brush_b_removed.setStyle(QtCore.Qt.BDiagPattern)
brush_f_removed = QtGui.QBrush(QtGui.QColor(170, 170, 170))
brush_f_removed.setStyle(QtCore.Qt.SolidPattern)
#


class GlobalVars:
    ITEM_ENABLED = True
    ITEM_DISABLED = False
    ITEM_NOTOGGLE = 'no'

    SOURCE_NAMESPACE = ''
    TARGET_NAMESPACE = ''

    FROM_SOURCE = 'source'
    FROM_TARGET = 'targe'
    FROM_MERGE = 'merge'

    PROPERTIES_SOURCE = {}
    PROPERTIES_TARGET = {}
    PROPERTIES_MERGED = {}

    SOURCE_MERGED = False
    TARGET_MERGED = False


class ProfileItem(QListWidgetItem):
    def __init__(self,id:str, _property:str, item_data:dict, from_profile:str, item_enabled, *args, **kwargs):
        super().__init__()
        self.id = id
        self.property = _property
        self.setText(_property)
        self.item_data = item_data
        self.item_enabled = item_enabled
        self.from_profile = from_profile

    @property
    def item_enabled(self):
        return self.__item_enabled
    @item_enabled.setter
    def item_enabled(self, value: bool):
        self.__item_enabled = value
        if value != GlobalVars.ITEM_NOTOGGLE:
            if value:
                self.setBackground(brush_b_enabled)
            else:
                self.setBackground(brush_b_disabled)

    def compareObject(self, other):
        return self.id == other.id

    def getCopy(self):
        return ProfileItem (
            self.id,
            self.property,
            self.item_data,
            self.from_profile,
            self.item_enabled
        )

    def __eq__(self, other):
        if other == None:
            return self.id == None
        return self.id == other.id and self.property == other.property

    def __str__(self):
        return f'<ProfileItem: {self.property}>'

class ProfileScanner(QtCore.QThread):
    # Progress Signal
    updateProgress = QtCore.Signal(int)
    addItems = QtCore.Signal(dict)

    def __init__(self, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.profile_filepath = ''
        self.from_profile = ''

    # Overloaded, is run by calling its start() function
    def run(self):
        # Reset tables
        if GlobalVars.SOURCE_MERGED and GlobalVars.TARGET_MERGED and len(GlobalVars.PROPERTIES_MERGED) > 0:
            GlobalVars.SOURCE_MERGED = False
            GlobalVars.TARGET_MERGED = False

            properties_rescan = GlobalVars.PROPERTIES_TARGET if self.from_profile == GlobalVars.FROM_SOURCE else GlobalVars.PROPERTIES_SOURCE

            GlobalVars.PROPERTIES_MERGED = {}
            for key, value in properties_rescan.items():
                GlobalVars.PROPERTIES_MERGED[key] = value

            if len(GlobalVars.PROPERTIES_SOURCE) > 0 and self.from_profile == GlobalVars.FROM_SOURCE:
                GlobalVars.PROPERTIES_SOURCE = {}
            if len(GlobalVars.PROPERTIES_TARGET) > 0 and self.from_profile == GlobalVars.FROM_TARGET:
                GlobalVars.PROPERTIES_TARGET = {}
            

        # Loop through profile XML
        tree = ElementTree.parse(self.profile_filepath)
        root = tree.getroot()

        # This regex is for removing the namespace prefix of the tag
        namespace_pattern = '^{.*}'
        namespace_regex = re.compile(namespace_pattern)

        tag = ''
        index = 0
        fields_dict = {}
        for profileField in root:
            namespace = namespace_regex.match(profileField.tag).group()

            if self.from_profile == GlobalVars.FROM_SOURCE and not GlobalVars.SOURCE_NAMESPACE:
                GlobalVars.SOURCE_NAMESPACE = namespace
            if self.from_profile == GlobalVars.FROM_TARGET and not GlobalVars.TARGET_NAMESPACE:
                GlobalVars.TARGET_NAMESPACE = namespace

            fieldType = profileField.tag.replace(namespace, '')

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
                    tag = child.tag.replace(namespace, '')
                    fields[tag] = child.text

                profile_field = model_class()

                profile_field.set_fields(fields)

                toggles = profile_field.get_toggles()
                _id = str(profile_field)
                item = None
                if toggles:
                    for key, value in toggles.items():
                        full_property = f'{str(profile_field)} --- {key}'
                        fields_dict[full_property] = ProfileItem(_id, full_property, {'data': profile_field.get_fields()}, self.from_profile, value)
                else:
                    fields_dict[_id] = ProfileItem(_id, _id, {'data': profile_field.get_fields()}, self.from_profile, GlobalVars.ITEM_NOTOGGLE)

        if len(fields_dict) > 0:
            # Fill global lists
            for key, value in fields_dict.items():
                GlobalVars.PROPERTIES_MERGED[key] = value
                if self.from_profile == GlobalVars.FROM_SOURCE:
                    GlobalVars.PROPERTIES_SOURCE[key] = value
                if self.from_profile == GlobalVars.FROM_TARGET:
                    GlobalVars.PROPERTIES_TARGET[key] = value

            # Set flags
            GlobalVars.SOURCE_MERGED = len(GlobalVars.PROPERTIES_SOURCE) > 0
            GlobalVars.TARGET_MERGED = len(GlobalVars.PROPERTIES_TARGET) > 0

            self.addItems.emit( {
                'from': self.from_profile, # with love from
                'items': fields_dict
            })


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        ui = self.ui
        ui.setupUi(self)

        # fill filter cmb
        self.ui.cmb_filter.clear()
        self.ui.cmb_filter.addItem('All')
        for model_name in models.classes_by_modelName.keys():
            self.ui.cmb_filter.addItem(model_name)

        #ui.bar_loading.hide()
        
        self.ui.list_source.item(0).setBackground(brush_b_enabled)
        self.ui.list_source.item(1).setBackground(brush_b_disabled)
        self.ui.list_source.item(3).setBackground(brush_b_removed)
        self.ui.list_source.item(3).setForeground(brush_f_removed)

        self.ui.list_source.clear()
        
        self.ui.btn_source.clicked.connect(lambda: self.find_profile_file(ui.le_source, GlobalVars.FROM_SOURCE, ui.list_source))
        self.ui.btn_target.clicked.connect(lambda: self.find_profile_file(ui.le_target, GlobalVars.FROM_TARGET ,ui.list_target))

        self.ui.btn_start.clicked.connect(lambda: pprint(profile_list_source[0]))

        self.lastItem = None
        self.ui.list_source.itemClicked.connect(self.itemClicked)
        self.ui.list_target.itemClicked.connect(self.itemClicked)


        self.scanner_worker = ProfileScanner()
        self.scanner_worker.addItems.connect(self.addItems)

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

        if self.lastItem == None:
            self.lastItem = value

        pprint(self.lastItem.property)
        pprint(value.property)
        pprint(self.lastItem == value)

        self.lastItem = value


    def addItems(self, package: dict):
        if self.list_target:
            merged_dict = GlobalVars.PROPERTIES_MERGED

            new_items = package['items']
            list_from = package['from']

            # Fill merged list
            self.ui.list_merged.clear()
            for value in sorted(merged_dict.values()):
                self.ui.list_merged.addItem(value.getCopy())

            # Compare to merged and fill
            self.ui.list_source.clear()
            self.ui.list_target.clear()
            for key in sorted(merged_dict.keys()):
                item_target = GlobalVars.PROPERTIES_TARGET.get(key)
                item_source = GlobalVars.PROPERTIES_SOURCE.get(key)

                if item_target:
                    self.ui.list_target.addItem(item_target.getCopy())
                else:
                    self.ui.list_target.addItem('')

                if item_source:
                    self.ui.list_source.addItem(item_source.getCopy())
                else:
                    self.ui.list_source.addItem('')


    # Uses open file dialog to setup a filename
    def find_profile_file(self, le_target: QLineEdit, from_profile: str, list_target: QListWidget):
        file_path, _filtro = QFileDialog.getOpenFileName(
            self,
            'Pick your Profile file',
            '',
            '*.xml *.profile'
        )

        if file_path != '' and le_target:
            le_target.setText(file_path)

            list_target.clear()
            self.list_target = list_target
            self.scanner_worker.profile_filepath = file_path
            self.scanner_worker.from_profile = from_profile
            self.scanner_worker.start()

        return file_path


if __name__ == "__main__":
    app = QApplication([])
    
    # Setup Style
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside())

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
