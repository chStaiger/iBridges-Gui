"""Provide the GUI with iRODS information

"""
import sys

import PyQt6
import PyQt6.QtWidgets
import PyQt6.uic

import gui
import irodsConnector


class irodsInfo(PyQt6.QtWidgets.QWidget,
                gui.ui_files.tabInfo.Ui_tabInfo):
    """Set iRODS information in the GUI

    """
    conn = irodsConnector.manager.IrodsConnector()

    def __init__(self):
        super().__init__()
        if getattr(sys, 'frozen', False):
            super().setupUi(self)
        else:
            PyQt6.uic.loadUi("gui/ui_files/tabInfo.ui", self)
        self.refreshButton.clicked.connect(self.refresh_info)
        self.refresh_info()

    def refresh_info(self):
        """Find and set the information of the connected iRODS system
        including the availble top-level resources.
        """
        self.rescTable.setRowCount(0)
        self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.WaitCursor))
        # irods Zone
        self.zoneLabel.setText(self.conn.zone)
        # irods user
        self.userLabel.setText(self.conn.username)
        # irods user type and groups
        user_type, user_groups = self.conn.get_user_info()
        self.typeLabel.setText(user_type)
        self.groupsLabel.setText('\n'.join(user_groups))
        # default resource
        self.rescLabel.setText(self.conn.default_resc)
        # irods server and version
        self.serverLabel.setText(self.conn.host)
        self.versionLabel.setText(
            '.'.join((str(num) for num in self.conn.server_version)))
        # irods resources
        resc_info = self.conn.list_resources(['name', 'status', 'free_space'])
        self.rescTable.setRowCount(len(resc_info[0]))
        for row, (name, status, space) in enumerate(zip(*resc_info)):
            self.rescTable.setItem(row, 0, PyQt6.QtWidgets.QTableWidgetItem(name))
            self.rescTable.setItem(row, 1, PyQt6.QtWidgets.QTableWidgetItem(str(space)))
            self.rescTable.setItem(row, 2, PyQt6.QtWidgets.QTableWidgetItem(str(status or '')))
        self.rescTable.resizeColumnsToContents()
        self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
