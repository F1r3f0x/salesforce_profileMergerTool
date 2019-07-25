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
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QMainWindow, QApplication, QLineEdit, QFileDialog
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem, QMessageBox
import qdarkstyle

# mine
from ui import Ui_MainWindow, UiProfileItem
from ui import main_stylesheet
import models
import utils


class GlobalEstate:
    """Program Global Estate

    Attributes:
        A_MERGED (bool): Is the A profile merged?
        B_MERGED (bool): Is the B profile merged?
        FROM_A (str): Is from A
        FROM_B (str): Is from B
        FROM_MERGED (str): Is from merged
    """
    A_MERGED = False
    B_MERGED = False

    FROM_A = 'A'
    FROM_B = 'B'
    FROM_MERGED = 'AB'

    MERGE_A_TO_B = False

    categories_items_a = None
    categories_items_b = None
    categories_items_merged = None

    class A:
        NAMESPACE = None
        PROPERTIES = {}

    class B:
        NAMESPACE = None
        PROPERTIES = {}

    class Merged:
        NAMESPACE = None
        PROPERTIES = {}

    class Items:
        a = {}
        b = {}
        merged = {}


class ProfileScanner(QtCore.QThread):
    """QThread to process profile, create the models and add the items to the interface.

    Attributes:
        profile_filepath (str): Path to the profile file
        from_profile (str): Internal profile name to fill

    [QT] Signals:
        addItems (bool): Signal to start adding items
    """
    addItems = QtCore.Signal(bool)

    def __init__(self):
        QtCore.QThread.__init__(self)
        self.profile_filepath = ''
        self.from_profile = ''

    def run(self):
        """
            Overloaded, is run by calling its start() function
        """
        ##
        # Reset tables
        if (GlobalEstate.A_MERGED or GlobalEstate.B_MERGED):
            properties_rescan = {}

            if (len(GlobalEstate.A.PROPERTIES) > 0
                    and self.from_profile == GlobalEstate.FROM_A):
                GlobalEstate.A.PROPERTIES = {}
                GlobalEstate.A_MERGED = False
                properties_rescan = GlobalEstate.B.PROPERTIES
            else:
                GlobalEstate.B.PROPERTIES = {}
                GlobalEstate.B_MERGED = False
                properties_rescan = GlobalEstate.A.PROPERTIES

            GlobalEstate.Merged.PROPERTIES = {}
            for key, value in properties_rescan.items():
                GlobalEstate.Merged.PROPERTIES[key] = value
        ##

        # Loop through profile XML
        tree = ElementTree.parse(self.profile_filepath)
        tree_root = tree.getroot()

        # This regex is for removing the namespace prefix of the tag
        namespace_pattern = '^{.*}'
        namespace_regex = re.compile(namespace_pattern)

        tag = ''
        # Create ProfileItems with the profile
        for prof_field_element in tree_root:
            namespace = namespace_regex.match(prof_field_element.tag).group()

            namespace_value = namespace.replace('{', '')
            namespace_value = namespace_value.replace('}', '')

            if self.from_profile == GlobalEstate.FROM_A and not GlobalEstate.A.NAMESPACE:
                GlobalEstate.A.NAMESPACE = namespace_value
            if self.from_profile == GlobalEstate.FROM_B and not GlobalEstate.B.NAMESPACE:
                GlobalEstate.B.NAMESPACE = namespace_value

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

                if self.from_profile == GlobalEstate.FROM_A:
                    GlobalEstate.A.PROPERTIES[_id] = profile_field
                if self.from_profile == GlobalEstate.FROM_B:
                    GlobalEstate.B.PROPERTIES[_id] = profile_field

        # Fill merged properties dict
        properties_dicts = None
        if GlobalEstate.MERGE_A_TO_B:
            properties_dicts = [GlobalEstate.B.PROPERTIES, GlobalEstate.A.PROPERTIES]
        else:
            properties_dicts = [GlobalEstate.A.PROPERTIES, GlobalEstate.B.PROPERTIES]

        for properties in properties_dicts:
            for _id, profile_field in properties.items():
                GlobalEstate.Merged.PROPERTIES[_id] = profile_field

        # GlobalEstate.Merged.PROPERTIES[_id] = profile_field

        GlobalEstate.A_MERGED = len(GlobalEstate.A.PROPERTIES) > 0
        GlobalEstate.B_MERGED = len(GlobalEstate.B.PROPERTIES) > 0

        self.addItems.emit(True)


class ProfileMergerUI(QMainWindow):
    """ Profile Merger main class

    Attributes:
        ui (MainWindow): class that has all the Qt ui components and the layout.
        tree_target: target QTreeWidget to fill with items after an addItems signal from
            Profile Scanner.
    """
    def __init__(self):
        super().__init__()

        ##
        # Class Attributes
        self.ui = Ui_MainWindow()
        self.tree_target = None
        ##

        # Setup UI class generated with QTCreator
        self.ui.setupUi(self)

        ##
        # Set initial state
        self.setWindowState(QtCore.Qt.WindowMaximized)
        ##

        # Setup Tree Widgets
        all_tree_widgets = [self.ui.tree_a, self.ui.tree_b, self.ui.tree_merged]
        for tree in all_tree_widgets:
            tree.clear()
            tree.headerItem().setTextAlignment(0, Qt.AlignHCenter | Qt.AlignVCenter)
            tree.itemExpanded.connect(self.handle_expand)
            tree.itemCollapsed.connect(self.handle_expand)
            tree.verticalScrollBar().valueChanged.connect(self.sync_scroll)

        self.ui.tree_a.itemClicked.connect(self.item_clicked)
        self.ui.tree_b.itemClicked.connect(self.item_clicked)
        self.ui.tree_merged.itemClicked.connect(self.merged_item_clicked)

        # Connect Buttons
        self.ui.btn_a.clicked.connect(
            lambda: self.load_profile_file(
                self.ui.le_a, GlobalEstate.FROM_A, self.ui.tree_a
            )
        )
        self.ui.btn_b.clicked.connect(
            lambda: self.load_profile_file(
                self.ui.le_b, GlobalEstate.FROM_B, self.ui.tree_b
            )
        )
        self.ui.btn_start.clicked.connect(self.save_merged_profile)
        self.ui.btn_expandAll.clicked.connect(
            lambda: ProfileMergerUI.expand_all_categories(True)
        )
        self.ui.btn_collapseAll.clicked.connect(
            lambda: ProfileMergerUI.expand_all_categories(False)
        )
        self.ui.btn_merge_dir.clicked.connect(self.change_merge_direction)

        # Connect Actions
        self.ui.actionExpand_All.triggered.connect(
            lambda: ProfileMergerUI.expand_all_categories(True)
        )
        self.ui.actionCollapse_All.triggered.connect(
            lambda: ProfileMergerUI.expand_all_categories(False)
        )
        self.ui.actionMerge.triggered.connect(self.save_merged_profile)
        self.ui.actionOpenProfileA.triggered.connect(
            lambda: self.load_profile_file(
                self.ui.le_a, GlobalEstate.FROM_A, self.ui.tree_a
                )
        )
        self.ui.actionOpenProfileB.triggered.connect(
            lambda: self.load_profile_file(
                self.ui.le_b, GlobalEstate.FROM_B, self.ui.tree_b
            )
        )
        ##

        # Worker Instance
        self.scanner_worker = ProfileScanner()
        self.scanner_worker.addItems.connect(self.add_items)

        # TODO
        self.ui.actionApplyAvalues.setEnabled(False)
        self.ui.actionApplyBValues.setEnabled(False)

    ##
    # Instance Methods
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
                GlobalEstate.Merged.PROPERTIES.values(), key=lambda x: x.model_name + str(x)
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

        self.ui.tree_a.topLevelItem(index).setExpanded(is_expanded)
        self.ui.tree_b.topLevelItem(index).setExpanded(is_expanded)
        self.ui.tree_merged.topLevelItem(index).setExpanded(is_expanded)

    def item_clicked(self, item_clicked: QTreeWidgetItem):
        if type(item_clicked) is UiProfileItem:
            parent_item = None
            parent_row = None
            child_row = None
            if item_clicked.treeWidget() is self.ui.tree_a:
                parent_item = item_clicked.parent()
                parent_row = self.ui.tree_a.indexOfTopLevelItem(parent_item)
                child_row = parent_item.indexOfChild(item_clicked)
            elif item_clicked.treeWidget() is self.ui.tree_b:
                parent_item = item_clicked.parent()
                parent_row = self.ui.tree_b.indexOfTopLevelItem(parent_item)
                child_row = parent_item.indexOfChild(item_clicked)
            else:
                return

            parent_merged_item = self.ui.tree_merged.topLevelItem(parent_row)
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
                merged = GlobalEstate.Items.merged[item_clicked.id]
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

    def change_merge_direction(self, a_to_b=None):
        if a_to_b is not None:
            GlobalEstate.MERGE_A_TO_B = not GlobalEstate.MERGE_A_TO_B
        else:
            GlobalEstate.MERGE_A_TO_B = a_to_b
        print(a_to_b)
        print('NEW A_TO_B:', GlobalEstate.MERGE_A_TO_B)

    def add_items(self, state: bool):
        if self.tree_target:
            merged_dict = GlobalEstate.Merged.PROPERTIES

            self.ui.tree_merged.clear()
            self.ui.tree_a.clear()
            self.ui.tree_b.clear()

            GlobalEstate.categories_items_merged = {}
            GlobalEstate.categories_items_a = {}
            GlobalEstate.categories_items_b = {}
            for key, value in models.classes_by_modelName.items():
                tree_item = QTreeWidgetItem()
                tree_item.setText(0, key)
                GlobalEstate.categories_items_a[key] = tree_item

                tree_item = QTreeWidgetItem()
                tree_item.setText(0, key)
                GlobalEstate.categories_items_b[key] = tree_item

                tree_item = QTreeWidgetItem()
                tree_item.setText(0, key)
                GlobalEstate.categories_items_merged[key] = tree_item

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
                                model_obj, GlobalEstate.categories_items_merged[model_type],
                                toggle_name=toggle_name, toggle_value=toggle_value,
                            )
                            item_group.append(item)

                            ProfileMergerUI.replicate_item(
                                GlobalEstate.B.PROPERTIES,
                                GlobalEstate.categories_items_b[model_type],
                                self.ui.tree_b,
                                key,
                                toggle_name
                            )
                            ProfileMergerUI.replicate_item(
                                GlobalEstate.A.PROPERTIES,
                                GlobalEstate.categories_items_a[model_type],
                                self.ui.tree_a,
                                key,
                                toggle_name
                            )

                    GlobalEstate.Items.merged[model_name] = item_group
                else:
                    item = UiProfileItem(model_obj, GlobalEstate.categories_items_merged[model_type])
                    if hasattr(model_obj, 'value'):
                        item.toggle_value = model_obj.value
                    GlobalEstate.Items.merged[model_name] = item
                    self.ui.tree_merged.addTopLevelItem(item)

                    ProfileMergerUI.replicate_item(
                        GlobalEstate.B.PROPERTIES,
                        GlobalEstate.categories_items_b[model_type], self.ui.tree_b, key
                    )
                    ProfileMergerUI.replicate_item(
                        GlobalEstate.A.PROPERTIES,
                        GlobalEstate.categories_items_a[model_type], self.ui.tree_a, key
                    )

            categories_by_treewidget = {
                self.ui.tree_b: GlobalEstate.categories_items_b,
                self.ui.tree_merged: GlobalEstate.categories_items_merged,
                self.ui.tree_a: GlobalEstate.categories_items_a
            }

            for tree_widget, categories in categories_by_treewidget.items():
                for item in categories.values():
                    if item.childCount() > 0:
                        tree_widget.addTopLevelItem(item)

            print(f'SOURCE: {len(GlobalEstate.A.PROPERTIES.keys())}')
            print(f'TARGET: {len(GlobalEstate.B.PROPERTIES.keys())}')
            print(f'MERGED: {len(GlobalEstate.Merged.PROPERTIES.keys())}')

    def sync_scroll(self, value):
        self.ui.tree_a.verticalScrollBar().setValue(value)
        self.ui.tree_b.verticalScrollBar().setValue(value)
        self.ui.tree_merged.verticalScrollBar().setValue(value)

    def load_profile_file(self, le_target: QLineEdit, from_profile: str, tree_target: QTreeWidget):
        """Opens file dialog to pick a profile and then initiates a thread to process it.

        Args:
            le_target (QLineEdit): QLineEdit that will store the file path.
            from_profile (str): What profile is being loaded.
            tree_target (QTreeWidget): Widget that will be filled with the profile fields.
        """
        # Open file dialog
        file_path, _filter = QFileDialog.getOpenFileName(
            self,
            f'Pick your Profile {from_profile}',
            '',
            '*.xml *.profile'
        )

        if file_path != '' and le_target:
            le_target.setText(file_path)

            self.tree_target = tree_target
            self.scanner_worker.profile_filepath = file_path
            self.scanner_worker.from_profile = from_profile
            self.scanner_worker.start()

            file_name = file_path.split('/')[-1].replace('.profile', '')

            tree_target.setHeaderLabel(file_name)

        return file_path
    ##

    ##
    # Static Methods
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

    def expand_all_categories(expand: bool):
        categories_lists = [
            GlobalEstate.categories_items_a.values(),
            GlobalEstate.categories_items_b.values(),
            GlobalEstate.categories_items_merged.values(),
        ]

        for item_list in categories_lists:
            for item in item_list:
                item.setExpanded(expand)
    ##

if __name__ == "__main__":
    app = QApplication([])

    # Setup Style
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside())

    window = ProfileMergerUI()
    window.show()

    # Apply my styling
    window.setStyleSheet(main_stylesheet)

    sys.exit(app.exec_())
