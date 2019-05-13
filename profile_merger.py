# std
import sys
import re
from xml.etree import ElementTree
from pprint import pprint

# qt
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2.QtWidgets import QMainWindow, QApplication, QLineEdit, QFileDialog
from PySide2.QtWidgets import QListWidget, QListWidgetItem, QMessageBox
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


class GlobalVar:
    ITEM_ENABLED = True
    ITEM_DISABLED = False
    ITEM_NOTOGGLE = 'no'

    SOURCE_MERGED = False
    TARGET_MERGED = False

    FROM_SOURCE = 'source'
    FROM_TARGET = 'target'
    FROM_MERGED = 'merged'

    class Source:
        NAMESPACE = ''
        PROPERTIES = {}

    class Target:
        NAMESPACE = ''
        PROPERTIES = {}

    class Merged:
        NAMESPACE = ''
        PROPERTIES = {}


class ProfileItem(QListWidgetItem):
    def __init__(self, id: str, _property: str, item_data: dict, from_profile: str, item_enabled):
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
        if value != GlobalVar.ITEM_NOTOGGLE:
            if value:
                self.setBackground(brush_b_enabled)
            else:
                self.setBackground(brush_b_disabled)

    def compare_field_type(self, other):
        return self.id == other.id

    @property
    def copy(self):
        return ProfileItem(
            self.id,
            self.property,
            self.item_data,
            self.from_profile,
            self.item_enabled
        )

    def __eq__(self, other):
        if other is None:
            return self.id is None
        return self.id == other.id and self.property == other.property

    def __str__(self):
        return f'<ProfileItem: {self.property}>'


class ProfileScanner(QtCore.QThread):
    updateProgress = QtCore.Signal(int)
    addItems = QtCore.Signal(dict)

    def __init__(self):
        QtCore.QThread.__init__(self)
        self.profile_filepath = ''
        self.from_profile = ''

    # Overloaded, is run by calling its start() function
    def run(self):
        # Reset tables
        if GlobalVar.SOURCE_MERGED and GlobalVar.TARGET_MERGED and len(GlobalVar.Merged.PROPERTIES) > 0:
            GlobalVar.SOURCE_MERGED, GlobalVar.TARGET_MERGED = False, False

            properties_rescan = GlobalVar.Target.PROPERTIES if self.from_profile == GlobalVar.FROM_SOURCE else GlobalVar.Source.PROPERTIES

            GlobalVar.Merged.PROPERTIES = {}
            for key, value in properties_rescan.items():
                GlobalVar.Merged.PROPERTIES[key] = value

            if len(GlobalVar.Source.PROPERTIES) > 0 and self.from_profile == GlobalVar.FROM_SOURCE:
                GlobalVar.Source.PROPERTIES = {}
            if len(GlobalVar.Target.PROPERTIES) > 0 and self.from_profile == GlobalVar.FROM_TARGET:
                GlobalVar.Target.PROPERTIES = {}

        # Loop through profile XML
        tree = ElementTree.parse(self.profile_filepath)
        tree_root = tree.getroot()

        # This regex is for removing the namespace prefix of the tag
        namespace_pattern = '^{.*}'
        namespace_regex = re.compile(namespace_pattern)

        tag, fields_dict = '', {}

        # Create ProfileItems with the profile
        for prof_field_element in tree_root:
            namespace = namespace_regex.match(prof_field_element.tag).group()

            if self.from_profile == GlobalVar.FROM_SOURCE and not GlobalVar.Source.NAMESPACE:
                GlobalVar.Source.NAMESPACE = namespace
            if self.from_profile == GlobalVar.FROM_TARGET and not GlobalVar.Target.NAMESPACE:
                GlobalVar.Target.NAMESPACE = namespace

            field_type_name = prof_field_element.tag.replace(namespace, '')

            """
                if prof_field_element.tag != tag:
                    print('tag: ', prof_field_element.tag)
                    print('namespace: ', ns)
                    print('field_type_name: ', prof_field_element.tag.replace(ns,''))
                print('attribute: ', prof_field_element.attrib)
            """

            model_class_name = models.classes_by_modelName.get(field_type_name)  # TODO: create exception if not found
            if model_class_name:
                fields = {}
                for field_child in prof_field_element:
                    tag = field_child.tag.replace(namespace, '')
                    fields[tag] = field_child.text
                profile_field = model_class_name()
                profile_field.fields = fields

                toggles, _id = profile_field.toggles, str(profile_field)
                if toggles:
                    for key, value in toggles.items():
                        full_property = f'{str(profile_field)} --- {key}'
                        fields_dict[full_property] = ProfileItem(
                            _id, full_property, {'data': profile_field.fields},
                            self.from_profile, value
                        )
                else:
                    fields_dict[_id] = ProfileItem(
                        _id, _id, {'data': profile_field.fields}, self.from_profile,
                        GlobalVar.ITEM_NOTOGGLE
                    )

        # Fill global lists
        if len(fields_dict) > 0:
            for key, value in fields_dict.items():
                GlobalVar.Merged.PROPERTIES[key] = value
                if self.from_profile == GlobalVar.FROM_SOURCE:
                    GlobalVar.Source.PROPERTIES[key] = value
                if self.from_profile == GlobalVar.FROM_TARGET:
                    GlobalVar.Target.PROPERTIES[key] = value
            GlobalVar.SOURCE_MERGED, GlobalVar.TARGET_MERGED = len(GlobalVar.Source.PROPERTIES) > 0, len(GlobalVar.Target.PROPERTIES) > 0

            self.addItems.emit({
                'from': self.from_profile,  # with love from
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

        # ui.bar_loading.hide()

        self.ui.list_source.clear()

        self.ui.btn_source.clicked.connect(
            lambda: self.find_profile_file(ui.le_source, GlobalVar.FROM_SOURCE, ui.list_source)
        )
        self.ui.btn_target.clicked.connect(
            lambda: self.find_profile_file(ui.le_target, GlobalVar.FROM_TARGET, ui.list_target)
        )

        # self.ui.btn_start.clicked.connect(lambda: pprint(profile_list_source[0]))

        self.lastItem = None
        self.ui.list_source.itemDoubleClicked.connect(self.sourceDblClicked)
        self.ui.list_target.itemDoubleClicked.connect(self.targetDblClicked)
        self.ui.list_merged.itemDoubleClicked.connect(self.mergedDblClicked)

        self.ui.list_source.verticalScrollBar().valueChanged.connect(self.syncScroll)
        self.ui.list_target.verticalScrollBar().valueChanged.connect(self.syncScroll)
        self.ui.list_merged.verticalScrollBar().valueChanged.connect(self.syncScroll)

        # self.ui.list_source.currentRowChanged.connect(self.syncRow)
        # self.ui.list_target.currentRowChanged.connect(self.syncRow)
        # self.ui.list_merged.currentRowChanged.connect(self.syncRow)

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

    def sourceDblClicked(self, value: QListWidgetItem):
        try:
            msgBox = QMessageBox()
            msgBox.setText(value.property)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Ok)
            msgBox.exec_()
        except Exception:
            pass

    def targetDblClicked(self, value: QListWidgetItem):
        """
            if self.lastItem == None:
                self.lastItem = value

            pprint(self.lastItem.property)
            pprint(value.property)
            pprint(self.lastItem == value)

            self.lastItem = value
        """
        print('target', value)

    def mergedDblClicked(self, value: QListWidgetItem):
        print('merged', value)

    def addItems(self, package: dict):
        if self.list_target:
            merged_dict = GlobalVar.Merged.PROPERTIES

            # new_items = package['items']
            # list_from = package['from']

            # Fill merged list
            self.ui.list_merged.clear()
            for value in sorted(merged_dict.values()):
                self.ui.list_merged.addItem(value.copy)

            # Compare to merged and fill
            self.ui.list_source.clear()
            self.ui.list_target.clear()
            for key in sorted(merged_dict.keys()):
                item_target = GlobalVar.Target.PROPERTIES.get(key)
                item_source = GlobalVar.Source.PROPERTIES.get(key)

                if item_target:
                    self.ui.list_target.addItem(item_target.copy)
                else:
                    self.ui.list_target.addItem('')

                if item_source:
                    self.ui.list_source.addItem(item_source.copy)
                else:
                    self.ui.list_source.addItem('')

    def syncScroll(self, value):
        self.ui.list_source.verticalScrollBar().setValue(value)
        self.ui.list_target.verticalScrollBar().setValue(value)
        self.ui.list_merged.verticalScrollBar().setValue(value)

    def syncRow(self, value):
        self.ui.list_source.setCurrentRow(value)
        self.ui.list_target.setCurrentRow(value)
        self.ui.list_merged.setCurrentRow(value)

    # Uses open file dialog to setup a filepath
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

            file_name = file_path.split('/')[-1].replace('.profile', '')
            if from_profile == GlobalVar.FROM_SOURCE:
                self.ui.lbl_source_2.setText(file_name)
            if from_profile == GlobalVar.FROM_TARGET:
                self.ui.lbl_target_2.setText(file_name)

        return file_path


if __name__ == "__main__":
    app = QApplication([])

    # Setup Style
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside())

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
