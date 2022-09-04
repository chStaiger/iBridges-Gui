from PyQt6.QtWidgets import QHeaderView, QMessageBox
from PyQt6 import QtCore
import os

from gui.checkableFsTree import checkableFsTreeModel
from gui.irodsTreeView import IrodsModel
from utils.utils import saveIenv

from gui.popupWidgets import irodsCreateCollection, createDirectory
from gui.dataTransfer import dataTransfer


class irodsUpDownload:
    def __init__(self, widget, ic, ienv):
        self.ic = ic
        self.widget = widget
        self.ienv = ienv
        self.syncing = False  # syncing or not

        # QTreeViews
        self.dirmodel = checkableFsTreeModel(self.widget.localFsTreeView)
        self.widget.localFsTreeView.setModel(self.dirmodel)
        # Hide all columns except the Name
        self.widget.localFsTreeView.setColumnHidden(1, True)
        self.widget.localFsTreeView.setColumnHidden(2, True)
        self.widget.localFsTreeView.setColumnHidden(3, True)
        self.widget.localFsTreeView.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        home_location = QtCore.QStandardPaths.standardLocations(
                               QtCore.QStandardPaths.StandardLocation.HomeLocation)[0]
        index = self.dirmodel.setRootPath(home_location)
        self.widget.localFsTreeView.setCurrentIndex(index)
        self.dirmodel.initial_expand()
        
        # iRODS zone info
        self.widget.irodsZoneLabel.setText("/"+self.ic.session.zone+":")
        # iRODS tree
        self.irodsmodel = IrodsModel(ic, self.widget.irodsFsTreeView)
        self.widget.irodsFsTreeView.setModel(self.irodsmodel)
        self.irodsRootColl = '/'+ic.session.zone
        self.irodsmodel.setHorizontalHeaderLabels([self.irodsRootColl,
                                              'Level', 'iRODS ID',
                                              'parent ID', 'type'])

        self.widget.irodsFsTreeView.expanded.connect(self.irodsmodel.refreshSubTree)
        self.widget.irodsFsTreeView.clicked.connect(self.irodsmodel.refreshSubTree)
        self.irodsmodel.initTree()

        self.widget.irodsFsTreeView.setHeaderHidden(True)
        self.widget.irodsFsTreeView.header().setDefaultSectionSize(180)
        self.widget.irodsFsTreeView.setColumnHidden(1, True)
        self.widget.irodsFsTreeView.setColumnHidden(2, True)
        self.widget.irodsFsTreeView.setColumnHidden(3, True)
        self.widget.irodsFsTreeView.setColumnHidden(4, True)

        # Buttons
        self.widget.UploadButton.clicked.connect(self.upload)
        self.widget.DownloadButton.clicked.connect(self.download)
        # self.widget.ContUplBut.clicked.connect(self.cont_upload)
        self.widget.ContUplBut.setHidden(True)  # For first release hide special buttons
        self.widget.uplSetGB_2.setHidden(True)
        self.widget.createFolderButton.clicked.connect(self.createFolder)
        self.widget.createCollButton.clicked.connect(self.createCollection)

        # Resource selector
        available_resources = self.ic.listResources()
        self.widget.resourceBox.clear()
        self.widget.resourceBox.addItems(available_resources)
        if ("default_resource_name" in ienv) and \
                (ienv["default_resource_name"] != "") and \
                (ienv["default_resource_name"] in available_resources):
            index = self.widget.resourceBox.findText(ienv["default_resource_name"])
            self.widget.resourceBox.setCurrentIndex(index)

        # Continuous upload settings
        if ienv["irods_host"] in ["scomp1461.wur.nl", "npec-icat.irods.surfsara.nl"]:
            # self.widget.uplSetGB_2.setVisible(True)
            if "ui_remLocalcopy" in ienv:
                self.widget.rLocalcopyCB.setChecked(ienv["ui_remLocalcopy"])
            if "ui_uplMode" in ienv:
                uplMode = ienv["ui_uplMode"]
                if uplMode == "f500":
                    self.widget.uplF500RB.setChecked(True)
                elif uplMode == "meta":
                    self.widget.uplMetaRB.setChecked(True)
                else:
                    self.widget.uplAllRB.setChecked(True)
            # self.widget.rLocalcopyCB.stateChanged.connect(self.saveUIset)
            # self.widget.uplF500RB.toggled.connect(self.saveUIset)
            # self.widget.uplMetaRB.toggled.connect(self.saveUIset)
            # self.widget.uplAllRB.toggled.connect(self.saveUIset)
        else:
            self.widget.uplSetGB_2.hide()
            self.widget.ContUplBut.hide()

    def enableButtons(self, enable):
        self.widget.UploadButton.setEnabled(enable)
        self.widget.DownloadButton.setEnabled(enable)
        self.widget.ContUplBut.setEnabled(enable)
        self.widget.uplSetGB_2.setEnabled(enable)
        self.widget.createFolderButton.setEnabled(enable)
        self.widget.createCollButton.setEnabled(enable)
        self.widget.localFsTreeView.setEnabled(enable)
        self.widget.localFsTreeView.setEnabled(enable)

    def infoPopup(self, message):
        QMessageBox.information(self.widget, 'Information', message)

    def saveUIset(self):
        self.ienv["ui_remLocalcopy"] = self.getRemLocalCopy()
        self.ienv["ui_uplMode"] = self.getUplMode()
        saveIenv(self.ienv)

    def getResource(self):
        return self.widget.resourceBox.currentText()

    def getRemLocalCopy(self):
        return self.widget.rLocalcopyCB.isChecked()

    def getUplMode(self):
        if self.widget.uplF500RB.isChecked():
            uplMode = "f500"
        elif self.widget.uplMetaRB.isChecked():
            uplMode = "meta"
        else:  # Default
            uplMode = "all"
        return uplMode

    def createFolder(self):
        parent = self.dirmodel.get_checked()
        if parent is None:
            self.widget.errorLabel.setText("No parent folder selected.")
        else:
            createDirWidget = createDirectory(parent)
            createDirWidget.exec()
            # self.dirmodel.initial_expand(previous_item = parent)

    def createCollection(self):
        idx, parent = self.irodsmodel.get_checked()
        if parent is None:
            self.widget.errorLabel.setText("No parent collection selected.")
        else:
            creteCollWidget = irodsCreateCollection(parent, self.ic)
            creteCollWidget.exec()
            self.irodsmodel.refreshSubTree(idx)

    # Upload a file/folder to IRODS and refresh the TreeView
    def upload(self):
        self.enableButtons(False)
        self.widget.errorLabel.clear()
        (fsSource, irodsDestIdx, irodsDestPath) = self.getPathsFromTrees()
        if fsSource is None or irodsDestPath is None:
            self.widget.errorLabel.setText(
                    "ERROR Up/Download: Please select source and destination.")
            self.enableButtons(True)
            return
        if not self.ic.session.collections.exists(irodsDestPath):
            self.widget.errorLabel.setText(
                    "ERROR UPLOAD: iRODS destination is file, must be collection.")
            self.enableButtons(True)
            return
        destColl = self.ic.session.collections.get(irodsDestPath)
        # if os.path.isdir(fsSource):
        self.uploadWindow = dataTransfer(self.ic, True, fsSource, destColl, 
                                         irodsDestIdx, self.getResource())
        self.uploadWindow.finished.connect(self.finishedUpDownload)

    def finishedUpDownload(self, success, irodsIdx):
        # Refreshes iRODS subtree ad irodsIdx (set "None" if to skip)
        # Saves upload parameters if check box is set
        if success is True:
            if irodsIdx is not None:
                self.irodsmodel.refreshSubTree(irodsIdx)
            if self.widget.saveSettings.isChecked():
                print("FINISH UPLOAD/DOWNLOAD: saving ui parameters.")
                self.saveUIset()
            self.widget.errorLabel.setText("INFO UPLOAD/DOWNLOAD: completed.")
        self.uploadWindow = None  # Release
        self.enableButtons(True)

    def download(self):
        self.enableButtons(False)
        self.widget.errorLabel.clear()
        (fsDest, irodsSourceIdx, irodsSourcePath) = self.getPathsFromTrees()
        if fsDest is None or irodsSourcePath is None:
            self.widget.errorLabel.setText(
                    "ERROR Up/Download: Please select source and destination.")
            self.enableButtons(True)
            return
        if os.path.isfile(fsDest):
            self.widget.errorLabel.setText(
                    "ERROR DOWNLOAD: Local Destination is file, must be folder.")
            self.enableButtons(True)
            return
        # File           
        if self.ic.session.data_objects.exists(irodsSourcePath):
            irodsItem = self.ic.session.data_objects.get(irodsSourcePath)
        else:
            irodsItem = self.ic.session.collections.get(irodsSourcePath)
        self.uploadWindow = dataTransfer(self.ic, False, fsDest, irodsItem)
        self.uploadWindow.finished.connect(self.finishedUpDownload)

    # Helpers to check file paths before upload
    def getPathsFromTrees(self):
        source = self.dirmodel.get_checked()
        if source is None:
            return (None, None, None)     
        destIdx, destPath = self.irodsmodel.get_checked()
        if destIdx is None or os.path.isfile(destPath):
            return (None, None, None)     
        return (source, destIdx, destPath)
