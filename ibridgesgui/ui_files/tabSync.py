# Form implementation generated from reading ui file 'ibridgesgui/ui_files/tabSync.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_tabSync(object):
    def setupUi(self, tabSync):
        tabSync.setObjectName("tabSync")
        tabSync.resize(1234, 721)
        tabSync.setStyleSheet(
            "QWidget\n"
            "{\n"
            "    color: rgb(86, 184, 139);\n"
            "    background-color: rgb(54, 54, 54);\n"
            "    selection-background-color: rgb(58, 152, 112);\n"
            "}\n"
            "\n"
            "QGroupBox\n"
            "{\n"
            "    background-color: rgb(85, 87, 83);\n"
            "}\n"
            "\n"
            "QTreeView,QTextBrowser\n"
            "{\n"
            "    background-color: rgb(85, 87, 83);\n"
            "}\n"
            "\n"
            "QLabel#error_label\n"
            "{\n"
            "    color: rgb(217, 174, 23);\n"
            "}"
        )
        self.layoutWidget = QtWidgets.QWidget(parent=tabSync)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 1231, 771))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_11.setSizeConstraint(
            QtWidgets.QLayout.SizeConstraint.SetDefaultConstraint
        )
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setSizeConstraint(
            QtWidgets.QLayout.SizeConstraint.SetDefaultConstraint
        )
        self.verticalLayout_5.setSpacing(2)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_19 = QtWidgets.QLabel(parent=self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_19.sizePolicy().hasHeightForWidth())
        self.label_19.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.label_19.setFont(font)
        self.label_19.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_19.setObjectName("label_19")
        self.verticalLayout_5.addWidget(self.label_19)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.create_dir_button = QtWidgets.QPushButton(parent=self.layoutWidget)
        self.create_dir_button.setObjectName("create_dir_button")
        self.horizontalLayout_13.addWidget(self.create_dir_button)
        self.label = QtWidgets.QLabel(parent=self.layoutWidget)
        self.label.setText("")
        self.label.setObjectName("label")
        self.horizontalLayout_13.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
        )
        self.horizontalLayout_13.addItem(spacerItem)
        self.verticalLayout_5.addLayout(self.horizontalLayout_13)
        self.local_fs_tree = QtWidgets.QTreeView(parent=self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.local_fs_tree.sizePolicy().hasHeightForWidth())
        self.local_fs_tree.setSizePolicy(sizePolicy)
        self.local_fs_tree.setStyleSheet("")
        self.local_fs_tree.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored
        )
        self.local_fs_tree.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.local_fs_tree.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.SingleSelection
        )
        self.local_fs_tree.setHeaderHidden(True)
        self.local_fs_tree.setObjectName("local_fs_tree")
        self.verticalLayout_5.addWidget(self.local_fs_tree)
        self.verticalLayout_5.setStretch(2, 1)
        self.horizontalLayout_5.addLayout(self.verticalLayout_5)
        spacerItem1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
        )
        self.horizontalLayout_5.addItem(spacerItem1)
        self.verticalLayout_15 = QtWidgets.QVBoxLayout()
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        spacerItem2 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding
        )
        self.verticalLayout_15.addItem(spacerItem2)
        self.gridLayout_7 = QtWidgets.QGridLayout()
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.local_to_irods_button = QtWidgets.QPushButton(parent=self.layoutWidget)
        self.local_to_irods_button.setMinimumSize(QtCore.QSize(100, 0))
        self.local_to_irods_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap("ibridgesgui/ui_files/../icons/arrow-right.png"),
            QtGui.QIcon.Mode.Normal,
            QtGui.QIcon.State.Off,
        )
        self.local_to_irods_button.setIcon(icon)
        self.local_to_irods_button.setIconSize(QtCore.QSize(50, 50))
        self.local_to_irods_button.setObjectName("local_to_irods_button")
        self.gridLayout_7.addWidget(self.local_to_irods_button, 0, 1, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
        )
        self.gridLayout_7.addItem(spacerItem3, 0, 2, 1, 1)
        self.irods_to_local_button = QtWidgets.QPushButton(parent=self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.irods_to_local_button.sizePolicy().hasHeightForWidth())
        self.irods_to_local_button.setSizePolicy(sizePolicy)
        self.irods_to_local_button.setMinimumSize(QtCore.QSize(100, 0))
        self.irods_to_local_button.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap("ibridgesgui/ui_files/../icons/arrow-left.png"),
            QtGui.QIcon.Mode.Normal,
            QtGui.QIcon.State.Off,
        )
        self.irods_to_local_button.setIcon(icon1)
        self.irods_to_local_button.setIconSize(QtCore.QSize(50, 50))
        self.irods_to_local_button.setObjectName("irods_to_local_button")
        self.gridLayout_7.addWidget(self.irods_to_local_button, 3, 1, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
        )
        self.gridLayout_7.addItem(spacerItem4, 0, 0, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Maximum
        )
        self.gridLayout_7.addItem(spacerItem5, 1, 1, 1, 1)
        self.verticalLayout_15.addLayout(self.gridLayout_7)
        spacerItem6 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding
        )
        self.verticalLayout_15.addItem(spacerItem6)
        self.horizontalLayout_5.addLayout(self.verticalLayout_15)
        spacerItem7 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
        )
        self.horizontalLayout_5.addItem(spacerItem7)
        self.verticalLayout_16 = QtWidgets.QVBoxLayout()
        self.verticalLayout_16.setObjectName("verticalLayout_16")
        self.label_20 = QtWidgets.QLabel(parent=self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_20.sizePolicy().hasHeightForWidth())
        self.label_20.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.label_20.setFont(font)
        self.label_20.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        self.label_20.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_20.setObjectName("label_20")
        self.verticalLayout_16.addWidget(self.label_20)
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        spacerItem8 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
        )
        self.horizontalLayout_15.addItem(spacerItem8)
        self.create_coll_button = QtWidgets.QPushButton(parent=self.layoutWidget)
        self.create_coll_button.setObjectName("create_coll_button")
        self.horizontalLayout_15.addWidget(self.create_coll_button)
        self.verticalLayout_16.addLayout(self.horizontalLayout_15)
        self.irods_tree = QtWidgets.QTreeView(parent=self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.irods_tree.sizePolicy().hasHeightForWidth())
        self.irods_tree.setSizePolicy(sizePolicy)
        self.irods_tree.setStyleSheet("")
        self.irods_tree.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents
        )
        self.irods_tree.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.irods_tree.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.irods_tree.setHeaderHidden(True)
        self.irods_tree.setObjectName("irods_tree")
        self.verticalLayout_16.addWidget(self.irods_tree)
        self.verticalLayout_16.setStretch(2, 1)
        self.horizontalLayout_5.addLayout(self.verticalLayout_16)
        self.horizontalLayout_5.setStretch(0, 1)
        self.horizontalLayout_5.setStretch(4, 1)
        self.verticalLayout_11.addLayout(self.horizontalLayout_5)
        spacerItem9 = QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed
        )
        self.verticalLayout_11.addItem(spacerItem9)
        self.error_label = QtWidgets.QLabel(parent=self.layoutWidget)
        self.error_label.setText("")
        self.error_label.setObjectName("error_label")
        self.verticalLayout_11.addWidget(self.error_label)
        spacerItem10 = QtWidgets.QSpacerItem(
            20, 10, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum
        )
        self.verticalLayout_11.addItem(spacerItem10)
        self.status_browser = QtWidgets.QTextBrowser(parent=self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.status_browser.sizePolicy().hasHeightForWidth())
        self.status_browser.setSizePolicy(sizePolicy)
        self.status_browser.setMaximumSize(QtCore.QSize(16777215, 200))
        self.status_browser.setObjectName("status_browser")
        self.verticalLayout_11.addWidget(self.status_browser)

        self.retranslateUi(tabSync)
        QtCore.QMetaObject.connectSlotsByName(tabSync)

    def retranslateUi(self, tabSync):
        _translate = QtCore.QCoreApplication.translate
        tabSync.setWindowTitle(_translate("tabSync", "Form"))
        self.label_19.setText(_translate("tabSync", "LOCAL"))
        self.create_dir_button.setText(_translate("tabSync", "Create Folder"))
        self.label_20.setText(_translate("tabSync", "IRODS"))
        self.create_coll_button.setText(_translate("tabSync", "Create Collection"))
