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


"""
class ProfileItem(QListWidgetItem):
    def __init__(self, id='', _property='', field='', item={}, from_profile='', toggle_value=True):
        super().__init__()
        self.id = id
        self.property = _property
        self.setText(_property)
        self._item_current = deepcopy(item)
        self.item_field = field
        self.item_original = item
        self._item_toggle = toggle_value
        self._item_disabled = False
        self.from_profile = from_profile
        self._refresh_styles()

    @property
    def toggle_value(self):
        return self._item_toggle

    @toggle_value.setter
    def toggle_value(self, value: bool):
        self._item_toggle = value
        self._refresh_styles()

    @property
    def item_disabled(self):
        return self._item_disabled

    @item_disabled.setter
    def item_disabled(self, value):
        self._item_disabled = value
        self._refresh_styles()

    @property
    def item(self):
        return self._item_current

    @item.setter
    def item(self, value):
        self._item_current = value

    @property
    def copy(self):
        return ProfileItem(
            id=self.id,
            _property=self.property,
            field=self.item_field,
            item=self.item,
            from_profile=self.from_profile,
            toggle_value=self.toggle_value
        )

    def compare_field_type(self, other):
        return self.id == other.id

    def _refresh_styles(self):
        if self.toggle_value != GlobalVar.ITEM_NOTOGGLE:
            if self.toggle_value:
                self.setBackground(brush_b_enabled)
            else:
                self.setBackground(brush_b_disabled)

        if self.item_disabled:
            self.setBackground(brush_b_removed)
            self.setForeground(brush_f_removed)
        else:
            self.setForeground(brush_f_normal)
            if self.toggle_value == GlobalVar.ITEM_NOTOGGLE:
                self.setBackground(brush_b_normal)

    def __eq__(self, other):
        if other is None:
            return self.id is None
        return self.id == other.id and self.property == other.property

    def __str__(self):
        return f'<ProfileItem: {self.property}>'
"""


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
        if (GlobalVar.SOURCE_MERGED and GlobalVar.TARGET_MERGED and
                len(GlobalVar.Merged.PROPERTIES) > 0):
            GlobalVar.SOURCE_MERGED, GlobalVar.TARGET_MERGED = False, False

            if self.from_profile == GlobalVar.FROM_SOURCE:
                properties_rescan = GlobalVar.Target.PROPERTIES
            else:
                properties_rescan = GlobalVar.Source.PROPERTIES

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

            namespace_value = namespace.replace('{', '')
            namespace_value = namespace_value.replace('}', '')

            if self.from_profile == GlobalVar.FROM_SOURCE and not GlobalVar.Source.NAMESPACE:
                GlobalVar.Source.NAMESPACE = namespace_value
            if self.from_profile == GlobalVar.FROM_TARGET and not GlobalVar.Target.NAMESPACE:
                GlobalVar.Target.NAMESPACE = namespace_value

            field_type_name = prof_field_element.tag.replace(namespace, '')

            # TODO: create exception if not found
            model_class_name = models.classes_by_modelName.get(field_type_name)

            if model_class_name:
                # Read metadata from xml
                fields = {}
                for field_child in prof_field_element:
                    tag = field_child.tag.replace(namespace, '')
                    fields[tag] = field_child.text

                # transfer to model
                profile_field = model_class_name()
                profile_field.fields = fields

                _id = str(profile_field)

                GlobalVar.Merged.PROPERTIES[_id] = profile_field
                fields_dict[_id] = profile_field

                if self.from_profile == GlobalVar.FROM_SOURCE:
                    GlobalVar.Source.PROPERTIES[_id] = profile_field
                if self.from_profile == GlobalVar.FROM_TARGET:
                    GlobalVar.Target.PROPERTIES[_id] = profile_field

        GlobalVar.SOURCE_MERGED = len(GlobalVar.Source.PROPERTIES) > 0
        GlobalVar.TARGET_MERGED = len(GlobalVar.Target.PROPERTIES) > 0

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

        self.ui.list_source.clear()

        self.ui.btn_source.clicked.connect(
            lambda: self.find_profile_file(ui.le_source, GlobalVar.FROM_SOURCE, ui.list_source)
        )
        self.ui.btn_target.clicked.connect(
            lambda: self.find_profile_file(ui.le_target, GlobalVar.FROM_TARGET, ui.list_target)
        )

        self.lastItem = None
        self.ui.list_source.itemClicked.connect(self.item_clicked)
        self.ui.list_target.itemClicked.connect(self.item_clicked)
        self.ui.list_merged.itemClicked.connect(self.merged_item_clicked)

        self.ui.list_source.verticalScrollBar().valueChanged.connect(self.syncScroll)
        self.ui.list_target.verticalScrollBar().valueChanged.connect(self.syncScroll)
        self.ui.list_merged.verticalScrollBar().valueChanged.connect(self.syncScroll)

        self.ui.btn_start.clicked.connect(self.startBtnClicked)

        self.scanner_worker = ProfileScanner()
        self.scanner_worker.addItems.connect(self.addItems)

    def startBtnClicked(self):
        xml_root = ElementTree.Element('Profile', attrib={'xmlns': 'http://soap.sforce.com/2006/04/metadata'})

        current_id = None
        for model_item in GlobalVar.Items.merged.values():
            print(model_item.id)
            if current_id != model_item.id:
                current_id = model_item.id
                model_field = model_item.item
                c = ElementTree.SubElement(xml_root, model_field.model_name)
                for field, value in model_field.fields.items():
                    if value is not None and value != '':
                        if type(value) is bool:
                            value = str(value).lower()
                        ElementTree.SubElement(c, field).text = value

        xml_str = ElementTree.tostring(xml_root, 'utf-8')
        reparsed = minidom.parseString(xml_str)
        xml_str = reparsed.toprettyxml(indent="    ", encoding='UTF-8').decode('utf-8').rstrip()

        file_path, _filter = QFileDialog.getSaveFileName(
            self,
            'Save your Profile file',
            '',
            '*.xml *.profile'
        )

        if file_path != '':
            with open(file_path, 'w', encoding='utf-8') as file_pointer:
                file_pointer.write(xml_str)

            msgbox = QMessageBox()
            msgbox.setWindowTitle('Merging Results')
            msgbox.setText('DONE!')
            msgbox.exec_()

    def item_clicked(self, item_clicked: QListWidgetItem):
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
            merged_item.toggle_value = item_clicked.toggle_value
        else:
            merged_item.item_disabled = True

        MainWindow.item_set_styles(merged_item)
        item_clicked.setSelected(False)

    def merged_item_clicked(self, item_clicked: QListWidgetItem):
        if hasattr(item_clicked, 'item_disabled'):
            item_clicked.item_disabled = not item_clicked.item_disabled
            MainWindow.item_set_styles(item_clicked)
        item_clicked.setSelected(False)

    def addItems(self, package: dict):
        if self.list_target:
            print(self.list_target)
            merged_dict = GlobalVar.Merged.PROPERTIES

            # Fill merged list
            self.ui.list_merged.clear()
            self.ui.list_source.clear()
            self.ui.list_target.clear()
            for key in sorted(merged_dict.keys()):
                model_obj = merged_dict[key]
                model_name = str(model_obj)

                if len(model_obj.toggles.keys()) > 0:
                    for toggle_name, toggle_value in model_obj.toggles.items():
                        toggle_value = utils.str_to_bool(toggle_value)
                        print(model_name, toggle_name, toggle_value)
                        item = MainWindow.item_from_model_field(
                            model_name, toggle_name, toggle_value
                        )
                        GlobalVar.Items.merged[item.text()] = item
                        self.ui.list_merged.addItem(item)

                        MainWindow.replicate_item(
                            GlobalVar.Target.PROPERTIES,
                            self.ui.list_target,
                            key,
                            model_name,
                            toggle_name,
                        )
                        MainWindow.replicate_item(
                            GlobalVar.Source.PROPERTIES,
                            self.ui.list_source,
                            key,
                            model_name,
                            toggle_name,
                        )
                else:
                    item = MainWindow.item_from_model_field(model_name)
                    GlobalVar.Items.merged[model_name] = item
                    self.ui.list_merged.addItem(item)

                    MainWindow.replicate_item(
                        GlobalVar.Target.PROPERTIES,
                        self.ui.list_target,
                        key,
                        model_name
                    )
                    MainWindow.replicate_item(
                        GlobalVar.Source.PROPERTIES,
                        self.ui.list_source,
                        key,
                        model_name
                    )

            print(f'SOURCE: {self.ui.list_source.count()}')
            print(f'TARGET: {self.ui.list_target.count()}')
            print(f'MERGED: {self.ui.list_merged.count()}')

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
            if from_profile == GlobalVar.FROM_SOURCE:
                self.ui.lbl_source_2.setText(file_name)
            if from_profile == GlobalVar.FROM_TARGET:
                self.ui.lbl_target_2.setText(file_name)

        return file_path

    def item_set_styles(item):
        if item.toggle_value != GlobalVar.ITEM_NOTOGGLE:
            if item.toggle_value:
                item.setBackground(brush_b_enabled)
            else:
                item.setBackground(brush_b_disabled)

        if item.item_disabled:
            item.setBackground(brush_b_removed)
            item.setForeground(brush_f_removed)
        else:
            item.setForeground(brush_f_normal)
            if item.toggle_value == GlobalVar.ITEM_NOTOGGLE:
                item.setBackground(brush_b_normal)

    def item_from_model_field(model_name, field=None, value=None) -> QListWidgetItem:
        item = QListWidgetItem(model_name)
        item.item_disabled = False
        item.toggle_value = GlobalVar.ITEM_NOTOGGLE

        if field is not None and value is not None:
            item.setText(f'{model_name} -- {field}: {value}')
            item.toggle_value = value

            if value:
                item.setBackground(brush_b_enabled)
            else:
                item.setBackground(brush_b_disabled)

        return item

    def replicate_item(global_dict, ui_list, key, model_name, toggle_name=None):
        if global_dict.get(key):
            if (toggle_name is not None):
                
                # Get the value from the item, not the merged list
                toggle_value = global_dict[key].toggles[toggle_name]

                item = MainWindow.item_from_model_field(model_name, toggle_name, toggle_value)
            else:
                item = MainWindow.item_from_model_field(model_name)
            global_dict[item.text()] = item
            ui_list.addItem(item)
        else:
            ui_list.addItem('')


if __name__ == "__main__":
    app = QApplication([])

    # Setup Style
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside())

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
