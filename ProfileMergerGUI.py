# -*- coding: utf-8 -*-
""" SF Profile Merger - GUI.

This module contains all the GUI functionality for SF Profile Merger

Copyright: Patricio Labin Correa - 2019

@F1r3f0x
"""

# std
import sys
from xml.etree import ElementTree
from xml.dom import minidom
# from pprint import pprint

# qt
from PySide2.QtCore import Qt, QThread, Signal
from PySide2.QtWidgets import QMainWindow, QApplication, QLineEdit, QFileDialog, QMessageBox
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem
from PySide2.QtGui import QIcon, QPixmap
import qdarkstyle

# mine
from ui import Ui_MainWindow, UiProfileItem
import ProfileMerger
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
        MERGE_A_TO_B (bool): Values from A take preference while merging.
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
        a = []
        b = []
        merged = {}


class ProfileScanner(QThread):
    """QThread to process profile, create the models and add the items to the interface.

    Attributes:
        profile_filepath (str): Path to the profile file
        from_profile (str): Internal profile name to fill

    [QT] Signals:
        addItems (bool): Signal to start adding items
    """
    profilesMerged = Signal(dict)

    def __init__(
        self, profile_merger: ProfileMerger.ProfileMerger, file_path_a=None, file_path_b=None,
        *args
    ):
        super().__init__(*args)
        self.profile_merger = profile_merger
        self.file_path_a = file_path_a
        self.file_path_b = file_path_b

    def run(self):
        profile_merged = self.profile_merger.merge_profiles(self.file_path_a, self.file_path_b)

        if profile_merged:
            self.profilesMerged.emit({
                'profile_merger': self.profile_merger
            })


class ProfileMergerUI(QMainWindow):
    """ Profile Merger main class

    Attributes:
        ui (MainWindow): class that has all the Qt ui components and the layout.
        tree_target: target QTreeWidget to fill with items after an addItems signal from
            Profile Scanner.
    """
    def __init__(self):
        super().__init__()

        # Setup UI class generated with QTCreator
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        ##
        # Attributes

        self.tree_target = None
        self.main_stylesheet = None
        self.icon_a_to_b = QIcon()
        self.icon_b_to_a = QIcon()

        self.profile_merger = ProfileMerger.ProfileMerger()

        self.items_a = {}
        self.items_b = {}
        self.items_merged = {}
        self.items = [self.items_a, self.items_b, self.items_merged]

        self.categories_a = {}
        self.categories_b = {}
        self.categories_merged = {}
        self.categories = [self.categories_a, self.categories_b, self.categories_merged]

        self.trees = [self.ui.tree_a, self.ui.tree_b, self.ui.tree_merged]


        ##
        # Set initial state
        self.setWindowState(Qt.WindowMaximized)

        # Get Stylesheets
        qss_dir = 'ui/'
        filename_stylesheet = 'stylesheet.css'
        try:
            with open(f'{qss_dir}{filename_stylesheet}', 'r') as fh:
                self.main_stylesheet = fh.read()
                self.setStyleSheet(self.main_stylesheet)
        except FileNotFoundError:
            print(f'{qss_dir}{filename_stylesheet} not found!')

        # Icons
        self.icon_b_to_a.addPixmap(QPixmap("ui/icons/arrow-left.svg"), QIcon.Normal, QIcon.Off)
        self.icon_a_to_b.addPixmap(QPixmap("ui/icons/arrow-right.svg"), QIcon.Normal, QIcon.Off)
        self.ui.btn_merge_dir.setMaximumSize(23, 23)
        self.change_merge_direction(False)
        ##

        # Setup Tree Widgets
        for tree in self.trees:
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
        self.ui.btn_applyA.clicked.connect(
            lambda: self.apply_all_values(GlobalEstate.FROM_A)
        )
        self.ui.btn_applyB.clicked.connect(
            lambda: self.apply_all_values(GlobalEstate.FROM_B)
        )
        self.ui.btn_close_a.clicked.connect(
            lambda: self.close_profile(GlobalEstate.FROM_A)
        )
        self.ui.btn_close_b.clicked.connect(
            lambda: self.close_profile(GlobalEstate.FROM_B)
        )
        ##

        self.scanner = ProfileScanner(self.profile_merger, None, None)
        self.scanner.profilesMerged.connect(self.add_items)

        # TODO
        self.ui.btn_applyA.setEnabled(False)
        self.ui.btn_applyB.setEnabled(False)

    ##
    # Instance Methods
    def save_merged_profile(self):
        """Picks a path and saves the merged profile to it.
        """
        file_path, _filter = QFileDialog.getSaveFileName(
            self,
            'Save your Profile file',
            '',
            '*.xml *.profile'
        )

        # If a path was selected
        if file_path != '':
            xml_root = ElementTree.Element(
                'Profile', attrib={'xmlns': 'http://soap.sforce.com/2006/04/metadata'}
            )

            # Goes through the merged profile and fills the xml
            for model_field in sorted(
                GlobalEstate.Merged.PROPERTIES.values(), key=lambda x: x.id
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

            # Get the xml as a String and then prettyfies it
            xml_str = ElementTree.tostring(xml_root, 'utf-8')
            reparsed = minidom.parseString(xml_str)
            xml_str = reparsed.toprettyxml(indent="    ", encoding='UTF-8').decode('utf-8').rstrip()

            # Write to the selected path
            with open(file_path, 'w', encoding='utf-8') as file_pointer:
                file_pointer.write(xml_str)     

            # Show result
            msgbox = QMessageBox()
            msgbox.setWindowTitle('Merge Results')
            msgbox.setIcon(QMessageBox.Information)
            msgbox.setText('Done.\t\t')
            msgbox.exec_()

    def handle_expand(self, item_clicked: QTreeWidgetItem, value_override=None):
        """Syncs the expand and collapse of categories of the QTrees.

        Args:
            item_clicked (QTreeWidgetItem): Item that was clicked in the QTree, comes from a Signal.
            value_override (bool): (Optional)
        """
        is_expanded = item_clicked.isExpanded()
        tree_widget = item_clicked.treeWidget()
        index = tree_widget.indexOfTopLevelItem(item_clicked)

        self.ui.tree_a.topLevelItem(index).setExpanded(is_expanded)
        self.ui.tree_b.topLevelItem(index).setExpanded(is_expanded)
        self.ui.tree_merged.topLevelItem(index).setExpanded(is_expanded)

    def item_clicked(self, item_clicked: QTreeWidgetItem):
        """Handle left click for the A and B QTrees.
            - If it's an item, update the merged item with the clicked item value.

        Args:
            item_clicked (QTreeWidgetItem): Item that was clicked in the QTree, comes from a Signal.
        """
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
        """Handle left click for the merged QTree.
            - If it's an item, disable it.
            - If it's a category, disable all the childs

        Args:
            item_clicked (QTreeWidgetItem): Item that was clicked in the QTree, comes from a Signal.
        """
        # Is an item
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
        # Is a category
        else:
            value = False
            for index in range(item_clicked.childCount()):
                item = item_clicked.child(index)
                if index == 0:
                    value = not item.item_disabled
                item_clicked.child(index).item_disabled = value

    def change_merge_direction(self, a_to_b=None):
        """Toggle or change the merge direction

        Args:
            a_to_b (bool): (Optional) sets the merge direction.
        """
        if a_to_b is not None:
            GlobalEstate.MERGE_A_TO_B = not GlobalEstate.MERGE_A_TO_B
        else:
            GlobalEstate.MERGE_A_TO_B = a_to_b

        if GlobalEstate.MERGE_A_TO_B:
            self.ui.btn_merge_dir.setIcon(self.icon_a_to_b)
        else:
            self.ui.btn_merge_dir.setIcon(self.icon_b_to_a)

    """
    def apply_all_values(self, from_profile: str):
        if from_profile == GlobalEstate.FROM_A:
            fields_to_apply = GlobalEstate.A.PROPERTIES
            items = GlobalEstate.Items.a
        else:
            fields_to_apply = GlobalEstate.B.PROPERTIES
            items = GlobalEstate.Items.b

        for item in items:
            pprint(item.__dict__)
    """

    def add_items(self, response_dict: dict):
        profile_merger = response_dict.get('profile_merger')
        if profile_merger is None:
            return

        # Clear QTreeWidgets
        for tree in self.trees:
            tree.clear()
        for categories_dict in self.categories:
            categories_dict.clear()

        # Fill the categories dicts, with the available ones
        for key, value in models.classes_by_modelName.items():
            tree_item = QTreeWidgetItem()
            tree_item.setText(0, key)
            self.categories_a[key] = tree_item

            tree_item = QTreeWidgetItem()
            tree_item.setText(0, key)
            self.categories_b[key] = tree_item

            tree_item = QTreeWidgetItem()
            tree_item.setText(0, key)
            self.categories_merged[key] = tree_item

        # Add items to the tree widgets
        categories_by_treewidget = {
            self.ui.tree_a: self.categories_a,
            self.ui.tree_b: self.categories_b,
            self.ui.tree_merged: self.categories_merged,
        }
        for tree_widget, categories in categories_by_treewidget.items():
            for item in categories.values():
                tree_widget.addTopLevelItem(item)

        # Fill trees
        trees_by_profile = {
            profile_merger.profile_a: self.ui.tree_a,
            profile_merger.profile_b: self.ui.tree_b,
            profile_merger.profile_merged: self.ui.tree_merged
        }
        items_by_profile = {
            profile_merger.profile_a: self.items_a,
            profile_merger.profile_b: self.items_b,
            profile_merger.profile_merged: self.items_merged
        }
        for profile, tree in trees_by_profile.items():
            categories_dict = categories_by_treewidget[tree]
            for _id, field in profile.fields.items():
                if len(field.toggles.values()) > 0:
                    item_group = []
                    for toggle_name, toggle_value in field.toggles.items():
                        if toggle_value is not None:
                            toggle_value = utils.str_to_bool(toggle_value)

                            item = UiProfileItem(
                                field, categories_dict[field.model_name],
                                toggle_name=toggle_name, toggle_value=toggle_value,
                            )
                        item_group.append(item)

                    items_by_profile[profile][_id] = item_group
                else:
                    toggle_value = None
                    if hasattr(field, 'value'):
                        toggle_value = field.value

                    item = UiProfileItem(
                        field, categories_dict[field.model_name],
                        toggle_value=toggle_value,
                    )
                    items_by_profile[profile][_id] = item

        for tree_widget, categories in categories_by_treewidget.items():
            for item in categories.values():
                if item.childCount() > 0:
                    tree_widget.addTopLevelItem(item)
                else:
                    # Remove empty categories
                    row_index = tree_widget.indexOfTopLevelItem(item)
                    tree_widget.takeTopLevelItem(row_index)

    def sync_scroll(self, value):
        """Syncs the scrollbar of the QTreeWidgets.

        Args:
            value (int): Index to set the scrollbar, comes from a signal.
        """
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
            """
            self.tree_target = tree_target
            self.scanner_worker.profile_filepath = file_path
            self.scanner_worker.from_profile = from_profile
            self.scanner_worker.start()
            """

            if from_profile == ProfileMerger.PROFILE_A:
                self.scanner.file_path_a = file_path
            else:
                self.scanner.file_path_b = file_path
            self.scanner.run()

            file_name = file_path.split('/')[-1].replace('.profile', '')

            tree_target.setHeaderLabel(file_name)

            """
            if from_profile == GlobalEstate.FROM_A:
                self.ui.btn_close_a.setEnabled(True)
            if from_profile == GlobalEstate.FROM_B:
                self.ui.btn_close_b.setEnabled(True)
            """

    def close_profile(self, from_profile: str):
        if from_profile == GlobalEstate.FROM_A:
            self.tree_target = self.ui.tree_a
            self.ui.le_a.setText('')
            GlobalEstate.A.PROPERTIES.clear()
            GlobalEstate.A_MERGED = False
            other_from = GlobalEstate.FROM_B
            reset_other_path = self.ui.le_b.text()
            self.ui.btn_close_a.setEnabled(False)
        else:
            self.tree_target = self.ui.tree_b
            self.ui.le_b.setText('')
            GlobalEstate.B.PROPERTIES.clear()
            GlobalEstate.B_MERGED = False
            other_from = GlobalEstate.FROM_A
            reset_other_path = self.ui.le_a.text()
            self.ui.btn_close_b.setEnabled(False)

        self.clear_trees()
        GlobalEstate.Merged.PROPERTIES.clear()
        GlobalEstate.Items.merged.clear()
        self.tree_target.setHeaderLabel(f'Profile {from_profile}')

        if reset_other_path:
            self.scanner_worker.profile_filepath = reset_other_path
            self.scanner_worker.from_profile = other_from
            self.scanner_worker.start()

    def clear_trees(self):
        all_tree_widgets = [self.ui.tree_a, self.ui.tree_b, self.ui.tree_merged]
        for tree in all_tree_widgets:
            tree.clear()
    ##

    ##
    # Static Methods
    def replicate_item(
        global_dict: dict, item_list: list, parent_item: QTreeWidgetItem, profile_field_id: str,
        toggle_name=None
    ):
        """Replicates a UiProfileItem below a parent_item (category) for the A or B QTrees,
        if the item is not found on the current list it generates an empty item for spacing.

        Args:
            global_dict (dict): Dict with the profile's properties
            parent_item (QTreeWidgetItem): Category item that will hold the replicated item
            profile_field_id (str): Id of the field
            toggle_name (str): Name of the toggable value if it's a toggle.
        """
        if global_dict.get(profile_field_id):
            profile_field = global_dict[profile_field_id]
            item = None
            if toggle_name is not None:
                # Get the value from the profile field, not the merged list
                toggle_value = profile_field.toggles[toggle_name]

                item = UiProfileItem(
                    profile_field, parent_item, toggle_name=toggle_name, toggle_value=toggle_value
                )
            elif (type(profile_field) is models.ProfileSingleValue
                    and type(profile_field.value) is bool):
                item = UiProfileItem(
                    profile_field, parent_item, toggle_value=profile_field.value
                )
            else:
                item = UiProfileItem(profile_field, parent_item)
            item_list.append(item)
        else:
            item = QTreeWidgetItem(parent_item)
            item.setText(0, '')
        item = None  # remove ref

    def expand_all_categories(expand: bool):
        """ Expand or Collapses all the categories

        Args:
            expand (bool): Expand the categories or collpase them?
        """
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
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())

    window = ProfileMergerUI()
    window.show()

    sys.exit(app.exec_())
