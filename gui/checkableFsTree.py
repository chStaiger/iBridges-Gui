from PyQt5.QtWidgets import QFileSystemModel, QFileIconProvider, QMessageBox
from PyQt5.QtCore import QFile, Qt, QDir
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from sys import platform
from time import sleep
import logging
import os

# a class to put checkbox on the folders and record which ones are checked.
class checkableFsTreeModel(QFileSystemModel):

    def __init__(self, TreeView, parent=None):
        """
        Initializes the Treeview with the root node. 
        """
        QFileSystemModel.__init__(self, None)
        self._checked_indeces = set() # keep track of the check files and folders...
        self.TreeView = TreeView
        self.setRootPath(QDir.currentPath())


    def initial_expand(self, previous_item = None):
        """
        Expands the Tree untill 'previous_item' and selects it.
        Input: filepath till previously selected file or folder
        """
        if previous_item != None: 
            index = self.index(previous_item, 0)
            self.TreeView.scrollTo(index)
            self._checked_indeces.add(index)
            self.setData(index, Qt.Checked, Qt.CheckStateRole)


    # Used to update the UI
    def data(self, index, role= Qt.DisplayRole):
        if role == Qt.CheckStateRole:
            if index in self._checked_indeces:
                return Qt.Checked
            else:
                return Qt.Unchecked
        return QFileSystemModel.data(self, index, role)

    def flags(self, index):
        return QFileSystemModel.flags(self, index) | Qt.ItemIsUserCheckable | Qt.ItemIsAutoTristate


    # Callback of the checkbox
    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.CheckStateRole:
            if value == Qt.Checked:
                path = self.data(index, QFileSystemModel.FilePathRole)
                if not os.access(path, os.W_OK):
                    message = "ERROR, insufficient rights:\nCannot select "+path
                    QMessageBox.information(self.TreeView, 'Error', message)
                    return False

                # Enforce single select
                while self._checked_indeces:
                    selected_index = self._checked_indeces.pop()
                    self.setData(selected_index, Qt.Unchecked, role)
                self._checked_indeces.add(index)
            else:
                self._checked_indeces.discard(index)
            self.TreeView.repaint()
            return True
        return QFileSystemModel.setData(self, index, value, role)


    # Returns the last selected item
    def get_checked(self):
        if len(self._checked_indeces) < 1:
            return None
        checked_item = list(self._checked_indeces)[0]
        filepath = self.filePath(checked_item)
        return filepath
