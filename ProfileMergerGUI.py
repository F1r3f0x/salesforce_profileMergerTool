# -*- coding: utf-8 -*-
""" SF Profile Merger - GUI.

This module contains all the GUI functionality for SF Profile Merger

Copyright: Patricio Labin Correa - 2019

@F1r3f0x
"""

# std
import sys
import re
from xml.etree import ElementTree
from xml.dom import minidom
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
import utils

# Brushes
brush_f_normal = QtGui.QBrush(QtGui.QColor(255, 255, 255))
brush_f_normal.setStyle(QtCore.Qt.SolidPattern)
brush_b_normal = QtGui.QBrush(QtGui.QColor(0, 0, 0))
brush_b_normal.setStyle(QtCore.Qt.NoBrush)

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
    """Global Variables.

    Attributes:
        SOURCE_MERGED (bool): Is the source file merged?
        TARGET_MERGED (bool): Is the target file merged?
        FROM_SOURCE (str): Is from source
        FROM_TARGET (str): Is from target
        FROM_MERGED (str): Is from merged
    """
    SOURCE_MERGED = False
    TARGET_MERGED = False

    FROM_SOURCE = 'source'
    FROM_TARGET = 'target'
    FROM_MERGED = 'merged'

    class Source:
        NAMESPACE = None
        PROPERTIES = {}

    class Target:
        NAMESPACE = None
        PROPERTIES = {}

    class Merged:
        NAMESPACE = None
        PROPERTIES = {}

    class Items:
        source = {}
        target = {}
        merged = {}


class UiProfileItem(QListWidgetItem):
    """Profile Field as a QListWidgetItem.

    It contains styling to signal its status and a reference to the field type object

    Args:
        model_ref (models.ProfileFieldType): Reference to the field type.
        disabled (bool): Ignore the object at merge.
        toggle_name (str): Boolean value name
        toggle_value (bool): Boolean value of the toogle

    Attributes:
        id (str): Field type Id, it's used to group the field properties
        model_ref (models.ProfileFieldType): Reference to the field type.
        item_disabled (bool): Ignore the object at merge.
        toggle_name (str): Boolean value name
        toggle_value (bool): Boolean value of the toogle

    """
    def __init__(
        self, model_ref: models.ProfileFieldType, disabled=False,
        toggle_name=None, toggle_value=None
    ):
        super().__init__()
        self.id = str(model_ref)
        self.model_ref = model_ref
        self.model_ref.model_disabled = disabled
        self.toggle_name = toggle_name
        self.__toggle_value = toggle_value

        if toggle_name is not None:
            self.model_ref.toggles[toggle_name] = toggle_value

        self.__refresh_view()

    @property
    def item_label(self):
        return self.__item_label

    @property
    def toggle_value(self):
        return self.__toggle_value

    @toggle_value.setter
    def toggle_value(self, value: bool):
        if self.toggle_name is not None:
            self.model_ref.toggles[self.toggle_name] = value
        elif type(self.model_ref) is models.ProfileSingleValue:
            self.model_ref.value = value

        self.__toggle_value = value
        self.__refresh_view()

    @property
    def item_disabled(self):
        return self.model_ref.model_disabled

    @item_disabled.setter
    def item_disabled(self, value):
        self.model_ref.model_disabled = value

        self.__refresh_view()

    def __refresh_view(self):
        """
            Refreshes the styling and the label for the item.
        """
        if self.toggle_name is not None:
            self.__item_label = f'{self.id} -- {self.toggle_name}: {self.toggle_value}'
        elif type(self.model_ref) is models.ProfileSingleValue:
            self.__item_label = f'{self.id} -- {self.model_ref.value}'
        else:
            self.__item_label = self.id

        self.setText(self.__item_label)

        if self.toggle_value is not None:
            if self.toggle_value:
                self.setBackground(brush_b_enabled)
            else:
                self.setBackground(brush_b_disabled)

        if self.item_disabled:
            self.setBackground(brush_b_removed)
            self.setForeground(brush_f_removed)
        else:
            self.setForeground(brush_f_normal)
            if self.toggle_value is None:
                self.setBackground(brush_b_normal)

    def __str__(self):
        return f'<UiProfileItem: {self.text()}>'


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
        if (GlobalVars.SOURCE_MERGED and GlobalVars.TARGET_MERGED and
                len(GlobalVars.Merged.PROPERTIES) > 0):
            GlobalVars.SOURCE_MERGED, GlobalVars.TARGET_MERGED = False, False

            if self.from_profile == GlobalVars.FROM_SOURCE:
                properties_rescan = GlobalVars.Target.PROPERTIES
            else:
                properties_rescan = GlobalVars.Source.PROPERTIES

            GlobalVars.Merged.PROPERTIES = {}
            for key, value in properties_rescan.items():
                GlobalVars.Merged.PROPERTIES[key] = value

            if (len(GlobalVars.Source.PROPERTIES) > 0
                    and self.from_profile == GlobalVars.FROM_SOURCE):
                GlobalVars.Source.PROPERTIES = {}
            if (len(GlobalVars.Target.PROPERTIES) > 0
                    and self.from_profile == GlobalVars.FROM_TARGET):
                GlobalVars.Target.PROPERTIES = {}

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

            namespace_value = namespace.replace('{', '')
            namespace_value = namespace_value.replace('}', '')

            if self.from_profile == GlobalVars.FROM_SOURCE and not GlobalVars.Source.NAMESPACE:
                GlobalVars.Source.NAMESPACE = namespace_value
            if self.from_profile == GlobalVars.FROM_TARGET and not GlobalVars.Target.NAMESPACE:
                GlobalVars.Target.NAMESPACE = namespace_value

            field_type_name = prof_field_element.tag.replace(namespace, '')

            # TODO: create exception and handle if not found
            model_class = models.classes_by_modelName.get(field_type_name)

            if model_class:
                # Read metadata from xml
                fields = {}
                for field_child in prof_field_element:
                    tag = field_child.tag.replace(namespace, '')
                    fields[tag] = field_child.text

                profile_field = None
                if model_class is models.ProfileSingleValue:
                    if field_type_name == 'custom':
                        profile_field = model_class(
                            field_type_name, prof_field_element.text, is_boolean=True
                        )
                    else:
                        profile_field = model_class(field_type_name, prof_field_element.text)
                else:
                    # transfer to model
                    profile_field = model_class()
                    profile_field.fields = fields

                _id = str(profile_field)

                GlobalVars.Merged.PROPERTIES[_id] = profile_field
                fields_dict[_id] = profile_field

                if self.from_profile == GlobalVars.FROM_SOURCE:
                    GlobalVars.Source.PROPERTIES[_id] = profile_field
                if self.from_profile == GlobalVars.FROM_TARGET:
                    GlobalVars.Target.PROPERTIES[_id] = profile_field

        GlobalVars.SOURCE_MERGED = len(GlobalVars.Source.PROPERTIES) > 0
        GlobalVars.TARGET_MERGED = len(GlobalVars.Target.PROPERTIES) > 0

        self.addItems.emit({
            'from': self.from_profile,  # with love from
            'items': fields_dict
        })


class ProfileMergerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        ui = self.ui
        ui.setupUi(self)

        # Properties
        self.lastItem = None

        # Fill filter cmb
        self.ui.cmb_filter.clear()
        self.ui.cmb_filter.addItem('All')
        for model_name in models.classes_by_modelName.keys():
            self.ui.cmb_filter.addItem(model_name)
            
        # Clear listwidgets
        self.ui.list_source.clear()
        self.ui.list_target.clear()
        self.ui.list_merged.clear()

        # Connect buttons
        self.ui.btn_source.clicked.connect(
            lambda: self.find_profile_file(ui.le_source, GlobalVars.FROM_SOURCE, ui.list_source)
        )
        self.ui.btn_target.clicked.connect(
            lambda: self.find_profile_file(ui.le_target, GlobalVars.FROM_TARGET, ui.list_target)
        )
        self.ui.list_source.itemClicked.connect(self.item_clicked)
        self.ui.list_target.itemClicked.connect(self.item_clicked)
        self.ui.list_merged.itemClicked.connect(self.merged_item_clicked)
        self.ui.list_source.verticalScrollBar().valueChanged.connect(self.syncScroll)
        self.ui.list_target.verticalScrollBar().valueChanged.connect(self.syncScroll)
        self.ui.list_merged.verticalScrollBar().valueChanged.connect(self.syncScroll)
        self.ui.btn_start.clicked.connect(self.startBtnClicked)

        # Worker Instance
        self.scanner_worker = ProfileScanner()
        self.scanner_worker.addItems.connect(self.addItems)

        # QoL Stuff
        self.setWindowState(QtCore.Qt.WindowMaximized)

    def startBtnClicked(self):
        file_path, _filter = QFileDialog.getSaveFileName(
            self,
            'Save your Profile file',
            '',
            '*.xml *.profile'
        )

        if file_path != '':
            xml_root = ElementTree.Element(
                'Profile', attrib={'xmlns': 'http://soap.sforce.com/2006/04/metadata'}
            )

            for model_field in GlobalVars.Merged.PROPERTIES.values():
                if not model_field.model_disabled:
                    if type(model_field) is not models.ProfileSingleValue:
                        c = ElementTree.SubElement(xml_root, model_field.model_name)
                        if model_field.fields:
                            for field, value in model_field.fields.items():
                                if value is not None and value != '':
                                    if type(value) is bool:
                                        value = str(value).lower()
                                    ElementTree.SubElement(c, field).text = value
                    else:
                        field = model_field.model_name
                        value = model_field.value
                        if value is not None and value != '':
                            if type(value) is bool:
                                value = str(value).lower()
                            c = ElementTree.SubElement(xml_root, model_field.model_name)
                            c.text = value

            xml_str = ElementTree.tostring(xml_root, 'utf-8')
            reparsed = minidom.parseString(xml_str)
            xml_str = reparsed.toprettyxml(indent="    ", encoding='UTF-8').decode('utf-8').rstrip()

            with open(file_path, 'w', encoding='utf-8') as file_pointer:
                file_pointer.write(xml_str)

            msgbox = QMessageBox()
            msgbox.setWindowTitle('Merging Results')
            msgbox.setText('DONE!\t\t\t\t')
            msgbox.exec_()

    def item_clicked(self, item_clicked: QListWidgetItem):
        if type(item_clicked) is UiProfileItem:
            row = None
            if item_clicked.listWidget() is self.ui.list_source:
                row = self.ui.list_source.row(item_clicked)
            elif item_clicked.listWidget() is self.ui.list_target:
                row = self.ui.list_target.row(item_clicked)
            else:
                # what in the fuck are you doing here
                return

            merged_item = self.ui.list_merged.item(row)
            merged_item.item_disabled = False
            if hasattr(item_clicked, 'toggle_value'):
                if item_clicked.toggle_value is not None:
                    merged_item.toggle_value = item_clicked.toggle_value
            else:
                merged_item.item_disabled = True

        item_clicked.setSelected(False)

    def merged_item_clicked(self, item_clicked: QListWidgetItem):
        disabled = item_clicked.item_disabled
        if hasattr(item_clicked, 'item_disabled'):
            merged = GlobalVars.Items.merged[item_clicked.id]
            if type(merged) is list:
                for item in merged:
                    item.item_disabled = not disabled
            else:
                item_clicked.item_disabled = not disabled
        item_clicked.setSelected(False)

    def addItems(self, package: dict):
        if self.list_target:
            merged_dict = GlobalVars.Merged.PROPERTIES

            # Fill merged list
            self.ui.list_merged.clear()
            self.ui.list_source.clear()
            self.ui.list_target.clear()
            for key in sorted(merged_dict.keys()):
                model_obj = merged_dict[key]
                model_name = str(model_obj)

                if model_obj.toggles is not None:
                        item_group = []
                        for toggle_name, toggle_value in model_obj.toggles.items():
                            if toggle_value is not None:
                                toggle_value = utils.str_to_bool(toggle_value)
                                item = UiProfileItem(
                                    model_obj, toggle_name=toggle_name, toggle_value=toggle_value
                                )
                                item_group.append(item)
                                ProfileMergerUI.replicate_item(
                                    GlobalVars.Target.PROPERTIES, self.ui.list_target, key,
                                    toggle_name
                                )
                                ProfileMergerUI.replicate_item(
                                    GlobalVars.Source.PROPERTIES, self.ui.list_source, key,
                                    toggle_name
                                )
                        GlobalVars.Items.merged[model_name] = item_group
                        for item in item_group:
                            self.ui.list_merged.addItem(item)
                    else:
                        item = UiProfileItem(model_obj)
                    if type(model_obj.value) is bool:
                        item.toggle_value = model_obj.value
                    GlobalVars.Items.merged[model_name] = item
                    self.ui.list_merged.addItem(item)

                    ProfileMergerUI.replicate_item(
                        GlobalVars.Target.PROPERTIES, self.ui.list_target, key
                    )
                    ProfileMergerUI.replicate_item(
                        GlobalVars.Source.PROPERTIES, self.ui.list_source, key
                    )

            print(f'SOURCE: {len(GlobalVars.Source.PROPERTIES.keys())}')
            print(f'TARGET: {len(GlobalVars.Target.PROPERTIES.keys())}')
            print(f'MERGED: {len(GlobalVars.Merged.PROPERTIES.keys())}')

    def syncScroll(self, value):
        self.ui.list_source.verticalScrollBar().setValue(value)
        self.ui.list_target.verticalScrollBar().setValue(value)
        self.ui.list_merged.verticalScrollBar().setValue(value)

    # Uses open file dialog to setup a filepath
    def find_profile_file(self, le_target: QLineEdit, from_profile: str, list_target: QListWidget):
        file_path, _filter = QFileDialog.getOpenFileName(
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
            if from_profile == GlobalVars.FROM_SOURCE:
                self.ui.lbl_source_2.setText(file_name)
            if from_profile == GlobalVars.FROM_TARGET:
                self.ui.lbl_target_2.setText(file_name)

        return file_path

    def replicate_item(global_dict, ui_list, key, toggle_name=None):
        if global_dict.get(key):
            model_obj = global_dict[key]
            if toggle_name is not None:
                # Get the value from the item, not the merged list
                toggle_value = model_obj.toggles[toggle_name]

                item = UiProfileItem(
                    model_obj, toggle_name=toggle_name, toggle_value=toggle_value
                )
            elif type(model_obj) is models.ProfileSingleValue and type(model_obj.value) is bool:
                item = UiProfileItem(
                    model_obj, toggle_value=model_obj.value
                )

            else:
                item = UiProfileItem(model_obj)

            # global_dict[item.text()] = item

            ui_list.addItem(item)
        else:
            ui_list.addItem('')


if __name__ == "__main__":
    app = QApplication([])

    # Setup Style
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside())

    window = ProfileMergerUI()
    window.show()
    sys.exit(app.exec_())
