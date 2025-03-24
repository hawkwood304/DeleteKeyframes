from shiboken2 import wrapInstance

import os
import maya.cmds as cm
# import pymel.core as pm
import maya.OpenMaya as om
import maya.OpenMayaUI as omui

from PySide2 import QtWidgets, QtCore, QtGui
from maya.mel import eval


# import sys


class QHLine(QtWidgets.QFrame):

    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(self.HLine)
        self.setFrameShadow(self.Sunken)


class QVLine(QtWidgets.QFrame):

    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(self.VLine)
        self.setFrameShadow(self.Sunken)


class QHLineName(QtWidgets.QGridLayout):

    def __init__(self, name):
        super(QHLineName, self).__init__()
        name_lb = QtWidgets.QLabel(name)
        name_lb.setAlignment(QtCore.Qt.AlignCenter)
        name_lb.setStyleSheet("font: italic 9pt;" "color: azure;")
        self.addWidget(name_lb, 0, 0, 1, 1)
        self.addWidget(QHLine(), 0, 1, 1, 2)


# noinspection PyAttributeOutsideInit
class DeleteTool(QtWidgets.QWidget):
    fbxVersions = {
        '2016': 'FBX201600',
        '2014': 'FBX201400',
        '2013': 'FBX201300',
        '2017': 'FBX201700',
        '2018': 'FBX201800',
        '2019': 'FBX201900'
    }

    def __init__(self):
        super(DeleteTool, self).__init__()

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.start_frame_lb = QtWidgets.QLabel("Start frame:")
        self.start_frame_le = QtWidgets.QLineEdit()

        self.end_frame_lb = QtWidgets.QLabel("End frame:")
        self.end_frame_le = QtWidgets.QLineEdit()

        self.get_current_time_range_btn = QtWidgets.QPushButton("Get Current Time Range")
        self.delete_key_btn = QtWidgets.QPushButton("Delete Key")

    def create_layouts(self):
        time_range_layout = QtWidgets.QHBoxLayout()
        time_range_layout.addWidget(self.start_frame_lb)
        time_range_layout.addWidget(self.start_frame_le)
        time_range_layout.addWidget(self.end_frame_lb)
        time_range_layout.addWidget(self.end_frame_le)

        command_layout = QtWidgets.QHBoxLayout()
        command_layout.addWidget(self.get_current_time_range_btn)
        command_layout.addWidget(self.delete_key_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(time_range_layout)
        main_layout.addLayout(command_layout)

    def create_connections(self):
        self.get_current_time_range_btn.clicked.connect(self.get_current_time_range)
        self.delete_key_btn.clicked.connect(self.delete_keyframes)

    def get_current_time_range(self):
        min_time = cm.playbackOptions(q=True, min=True)
        min_time = round(min_time)
        max_time = cm.playbackOptions(q=True, max=True)
        max_time = round(max_time)

        self.start_frame_le.setText(str(min_time))
        self.end_frame_le.setText(str(max_time))

    def delete_keyframes(self):
        selection_object = cm.ls(sl=True)
        if len(selection_object) > 0:
            min_time = self.start_frame_le.text()
            min_time = int(min_time)

            max_time = self.end_frame_le.text()
            max_time = int(max_time)

            cm.cutKey(selection_object, time=(min_time, max_time))

        else:
            om.MGlobal_displayError("Please chose at least one object to delete keyframes")


# noinspection PyMethodMayBeStatic,PyAttributeOutsideInit,PyMethodOverriding
class MainWindow(QtWidgets.QDialog):
    WINDOW_TITLE = "Delete Keyframes"

    SCRIPTS_DIR = cm.internalVar(userScriptDir=True)
    ICON_DIR = os.path.join(SCRIPTS_DIR, 'Thi/Icon')

    dlg_instance = None

    @classmethod
    def display(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = MainWindow()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()

        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    @classmethod
    def maya_main_window(cls):
        """

        Returns: The Maya main window widget as a Python object

        """
        main_window_ptr = omui.MQtUtil.mainWindow()
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

    def __init__(self):
        super(MainWindow, self).__init__(self.maya_main_window())

        self.setWindowTitle(self.WINDOW_TITLE)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.geometry = None

        self.setMinimumSize(400, 100)
        self.setMaximumSize(400, 100)
        self.create_widget()
        self.create_layouts()
        self.create_connections()

    def create_widget(self):
        self.content_layout = QtWidgets.QHBoxLayout()
        self.content_layout.addWidget(DeleteTool())

        self.close_btn = QtWidgets.QPushButton("Close")

    def create_layouts(self):

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(self.content_layout)

    def create_connections(self):
        self.close_btn.clicked.connect(self.close)

    def showEvent(self, e):
        super(MainWindow, self).showEvent(e)

        if self.geometry:
            self.restoreGeometry(self.geometry)

    def closeEvent(self, e):
        super(MainWindow, self).closeEvent(e)

        self.geometry = self.saveGeometry()
