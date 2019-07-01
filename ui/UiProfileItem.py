from PySide2 import QtGui, QtCore
from PySide2.QtWidgets import QListWidgetItem
import models

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
