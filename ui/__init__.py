from ui.UiProfileItem import UiProfileItem
from ui.UiTreeWidget import UiTreeWidget
from ui.MainWindow import Ui_MainWindow

from PySide2.QtGui import QBrush, QColor
from PySide2.QtCore import Qt
import json

# Get Stylesheets
qss_dir = 'ui/'
filename_stylesheet = 'stylesheet.css'
filename_b = 'BStyle.css'

main_stylesheet = None
try:
    with open(f'{qss_dir}{filename_stylesheet}', 'r') as fh:
        main_stylesheet = fh.read()
except FileNotFoundError:
    print(f'{qss_dir}{filename_stylesheet} not found!')