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
from PySide2.QtWidgets import QMainWindow, QApplication, QLineEdit, QFileDialog
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem, QMessageBox
import qdarkstyle

# mine
from ui import Ui_MainWindow, UiProfileItem
import models
import utils


class GlobalVars:
    """Global Variables.

    Attributes:
        SOURCE_MERGED (bool): Is the source file merged?
        TARGET_MERGED (bool): Is the target file merged?
        FROM_SOURCE (str): Is from source
        FROM_TARGET (str): Is from target
        FROM_MERGED (str): Is from merged
    """
    categories_items_merged = {}
    categories_items_source = {}
    categories_items_target = {}

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
        if (GlobalVars.SOURCE_MERGED or GlobalVars.TARGET_MERGED):

            properties_rescan = {}

            if (len(GlobalVars.Source.PROPERTIES) > 0
                    and self.from_profile == GlobalVars.FROM_SOURCE):
                GlobalVars.Source.PROPERTIES = {}
                GlobalVars.SOURCE_MERGED = False
                properties_rescan = GlobalVars.Target.PROPERTIES
            else:
                GlobalVars.Target.PROPERTIES = {}
                GlobalVars.TARGET_MERGED = False
                properties_rescan = GlobalVars.Source.PROPERTIES

            GlobalVars.Merged.PROPERTIES = {}
            for key, value in properties_rescan.items():
                GlobalVars.Merged.PROPERTIES[key] = value

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

        self.ui.list_source.itemExpanded.connect(self.handle_expand)
        self.ui.list_target.itemExpanded.connect(self.handle_expand)
        self.ui.list_merged.itemExpanded.connect(self.handle_expand)
        self.ui.list_source.itemCollapsed.connect(self.handle_expand)
        self.ui.list_target.itemCollapsed.connect(self.handle_expand)
        self.ui.list_merged.itemCollapsed.connect(self.handle_expand)

        self.ui.actionExpand_All.triggered.connect(lambda: ProfileMergerUI.do_set_expand_all(True))
        self.ui.actionCollapse_All.triggered.connect(lambda: ProfileMergerUI.do_set_expand_all(False))
        self.ui.actionMerge.triggered.connect(self.save_merged_profile)

        self.ui.list_source.verticalScrollBar().valueChanged.connect(self.sync_scroll)
        self.ui.list_target.verticalScrollBar().valueChanged.connect(self.sync_scroll)
        self.ui.list_merged.verticalScrollBar().valueChanged.connect(self.sync_scroll)
        self.ui.btn_start.clicked.connect(self.save_merged_profile)

        # Worker Instance
        self.scanner_worker = ProfileScanner()
        self.scanner_worker.addItems.connect(self.add_items)

        # QoL Stuff
        self.setWindowState(QtCore.Qt.WindowMaximized)

    def save_merged_profile(self):
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

            for model_field in sorted(
                GlobalVars.Merged.PROPERTIES.values(), key=lambda x: x.model_name + str(x)
            ):
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
            msgbox.setWindowTitle('Merge Results')
            msgbox.setIcon(QMessageBox.Information)
            msgbox.setText('Done.\t\t')
            msgbox.exec_()

    def handle_expand(self, item_clicked: QTreeWidgetItem, value_override=None):
        is_expanded = item_clicked.isExpanded()
        tree_widget = item_clicked.treeWidget()
        index = tree_widget.indexOfTopLevelItem(item_clicked)

        self.ui.list_source.topLevelItem(index).setExpanded(is_expanded)
        self.ui.list_target.topLevelItem(index).setExpanded(is_expanded)
        self.ui.list_merged.topLevelItem(index).setExpanded(is_expanded)

    def item_clicked(self, item_clicked: QTreeWidgetItem):
        if type(item_clicked) is UiProfileItem:
            parent_item = None
            parent_row = None
            child_row = None
            if item_clicked.treeWidget() is self.ui.list_source:
                parent_item = item_clicked.parent()
                parent_row = self.ui.list_source.indexOfTopLevelItem(parent_item)
                child_row = parent_item.indexOfChild(item_clicked)
            elif item_clicked.treeWidget() is self.ui.list_target:
                parent_item = item_clicked.parent()
                parent_row = self.ui.list_target.indexOfTopLevelItem(parent_item)
                child_row = parent_item.indexOfChild(item_clicked)
            else:
                # what in the fuck are you doing here
                return

            parent_merged_item = self.ui.list_merged.topLevelItem(parent_row)
            merged_item = parent_merged_item.child(child_row)
            merged_item.item_disabled = False
            if hasattr(item_clicked, 'toggle_value'):
                if item_clicked.toggle_value is not None:
                    merged_item.toggle_value = item_clicked.toggle_value
            else:
                merged_item.item_disabled = True

        item_clicked.setSelected(False)

    def merged_item_clicked(self, item_clicked: QTreeWidgetItem):
        if type(item_clicked) is UiProfileItem:
            disabled = item_clicked.item_disabled
            if hasattr(item_clicked, 'item_disabled'):
                merged = GlobalVars.Items.merged[item_clicked.id]
                if type(merged) is list:
                    for item in merged:
                        item.item_disabled = not disabled
                else:
                    item_clicked.item_disabled = not disabled
            item_clicked.setSelected(False)
        else:
            value = False
            for index in range(item_clicked.childCount()):
                item = item_clicked.child(index)
                if index == 0:
                    value = not item.item_disabled
                item_clicked.child(index).item_disabled = value

    def add_items(self, package: dict):
        if self.list_target:
            merged_dict = GlobalVars.Merged.PROPERTIES

            self.ui.list_merged.clear()
            self.ui.list_source.clear()
            self.ui.list_target.clear()

            GlobalVars.categories_items_merged = {}
            GlobalVars.categories_items_source = {}
            GlobalVars.categories_items_target = {}
            for key, value in models.classes_by_modelName.items():
                tree_item = QTreeWidgetItem()
                tree_item.setText(0, key)
                GlobalVars.categories_items_source[key] = tree_item

                tree_item = QTreeWidgetItem()
                tree_item.setText(0, key)
                GlobalVars.categories_items_target[key] = tree_item

                tree_item = QTreeWidgetItem()
                tree_item.setText(0, key)
                GlobalVars.categories_items_merged[key] = tree_item

            # Fill merged list
            for key in sorted(merged_dict.keys()):
                model_obj = merged_dict[key]
                model_type = model_obj.model_name
                model_name = str(model_obj)

                if len(model_obj.toggles.values()) > 0:
                    item_group = []
                    for toggle_name, toggle_value in model_obj.toggles.items():
                        if toggle_value is not None:
                            toggle_value = utils.str_to_bool(toggle_value)

                            item = UiProfileItem(
                                model_obj, GlobalVars.categories_items_merged[model_type],
                                toggle_name=toggle_name, toggle_value=toggle_value,
                            )
                            item_group.append(item)

                            ProfileMergerUI.replicate_item(
                                GlobalVars.Target.PROPERTIES,
                                GlobalVars.categories_items_target[model_type], self.ui.list_target, key,
                                toggle_name
                            )
                            ProfileMergerUI.replicate_item(
                                GlobalVars.Source.PROPERTIES,
                                GlobalVars.categories_items_source[model_type], self.ui.list_source, key,
                                toggle_name
                            )

                    GlobalVars.Items.merged[model_name] = item_group
                else:
                    item = UiProfileItem(model_obj, GlobalVars.categories_items_merged[model_type])
                    if hasattr(model_obj, 'value'):
                        item.toggle_value = model_obj.value
                    GlobalVars.Items.merged[model_name] = item
                    self.ui.list_merged.addTopLevelItem(item)

                    ProfileMergerUI.replicate_item(
                        GlobalVars.Target.PROPERTIES, 
                        GlobalVars.categories_items_target[model_type], self.ui.list_target, key
                    )
                    ProfileMergerUI.replicate_item(
                        GlobalVars.Source.PROPERTIES, 
                        GlobalVars.categories_items_source[model_type], self.ui.list_source, key
                    )

            categories_by_treewidget = {
                self.ui.list_target: GlobalVars.categories_items_target,
                self.ui.list_merged: GlobalVars.categories_items_merged,
                self.ui.list_source: GlobalVars.categories_items_source
            }

            for tree_widget, categories in categories_by_treewidget.items():
                for item in categories.values():
                    if item.childCount() > 0:
                        tree_widget.addTopLevelItem(item)

            print(f'SOURCE: {len(GlobalVars.Source.PROPERTIES.keys())}')
            print(f'TARGET: {len(GlobalVars.Target.PROPERTIES.keys())}')
            print(f'MERGED: {len(GlobalVars.Merged.PROPERTIES.keys())}')

    def sync_scroll(self, value):
        self.ui.list_source.verticalScrollBar().setValue(value)
        self.ui.list_target.verticalScrollBar().setValue(value)
        self.ui.list_merged.verticalScrollBar().setValue(value)

    # Uses open file dialog to setup a filepath
    def find_profile_file(self, le_target: QLineEdit, from_profile: str, list_target: QTreeWidget):
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

            list_target.setHeaderLabel(file_name)

        return file_path

    def replicate_item(
        global_dict, parent_item: QTreeWidgetItem, ui_list: QTreeWidget, key, toggle_name=None
    ):
        if global_dict.get(key):
            model_obj = global_dict[key]
            if toggle_name is not None:
                # Get the value from the item, not the merged list
                toggle_value = model_obj.toggles[toggle_name]

                item = UiProfileItem(
                    model_obj, parent_item, toggle_name=toggle_name, toggle_value=toggle_value
                )
            elif type(model_obj) is models.ProfileSingleValue and type(model_obj.value) is bool:
                item = UiProfileItem(
                    model_obj, parent_item, toggle_value=model_obj.value
                )

            else:
                item = UiProfileItem(model_obj, parent_item)
        else:
            item = QTreeWidgetItem(parent_item)
            item.setText(0, '')

    def do_set_expand_all(expand: bool):
        categories_lists = [
            GlobalVars.categories_items_source.values(),
            GlobalVars.categories_items_target.values(),
            GlobalVars.categories_items_merged.values(),
        ]

        for item_list in categories_lists:
            for item in item_list:
                item.setExpanded(expand)


if __name__ == "__main__":
    app = QApplication([])

    # Setup Style
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside())

    window = ProfileMergerUI()
    window.show()
    sys.exit(app.exec_())
