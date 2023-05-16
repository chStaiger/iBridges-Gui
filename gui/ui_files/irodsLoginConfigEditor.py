# Form implementation generated from reading ui file 'irodsLoginConfigEditor.ui'
#
# Created by: PyQt6 UI code generator 6.3.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_irodsLoginConfigEditor(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(900, 600)
        Form.setMinimumSize(QtCore.QSize(900, 600))
        Form.setStyleSheet("QWidget\n"
"{\n"
"    background-color: rgb(54, 54, 54);\n"
"    color: rgb(86, 184, 139);\n"
"    border-color: rgb(217, 174, 23);\n"
"}\n"
"\n"
"QLineEdit\n"
"{\n"
"    background-color: rgb(85, 87, 83);\n"
"    border-color: rgb(217, 174, 23);\n"
"}\n"
"\n"
"\n"
"QLabel#passError, QLabel#envError\n"
"{\n"
"    color: rgb(217, 174, 23);\n"
"}\n"
"\n"
"QPushButton#connectButton\n"
"{\n"
"    background-color: rgb(86, 184, 139);\n"
"    color: rgb(54, 54, 54);\n"
"}\n"
"")
        self.verticalLayoutWidget_3 = QtWidgets.QWidget(Form)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(10, 10, 871, 541))
        self.verticalLayoutWidget_3.setObjectName("verticalLayoutWidget_3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_4.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetNoConstraint)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetNoConstraint)
        self.gridLayout.setObjectName("gridLayout")
        self.ticketButton = QtWidgets.QPushButton(self.verticalLayoutWidget_3)
        self.ticketButton.setObjectName("ticketButton")
        self.gridLayout.addWidget(self.ticketButton, 8, 0, 1, 1)
        self.envError = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.envError.setText("")
        self.envError.setObjectName("envError")
        self.gridLayout.addWidget(self.envError, 4, 1, 1, 1)
        self.passwordField = QtWidgets.QLineEdit(self.verticalLayoutWidget_3)
        self.passwordField.setObjectName("passwordField")
        self.gridLayout.addWidget(self.passwordField, 5, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout.addItem(spacerItem1, 7, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 5, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setKerning(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.envbox = QtWidgets.QComboBox(self.verticalLayoutWidget_3)
        self.envbox.setObjectName("envbox")
        self.gridLayout.addWidget(self.envbox, 3, 1, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.connectButton = QtWidgets.QPushButton(self.verticalLayoutWidget_3)
        font = QtGui.QFont()
        font.setBold(True)
        self.connectButton.setFont(font)
        self.connectButton.setObjectName("connectButton")
        self.horizontalLayout.addWidget(self.connectButton)
        self.gridLayout.addLayout(self.horizontalLayout, 8, 1, 1, 1)
        self.passError = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.passError.setText("")
        self.passError.setObjectName("passError")
        self.gridLayout.addWidget(self.passError, 6, 1, 1, 1)
        self.verticalLayout_4.addLayout(self.gridLayout)
        self.label_7 = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.label_7.setText("")
        self.label_7.setObjectName("label_7")
        self.verticalLayout_4.addWidget(self.label_7)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_4 = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.irodsDisplay = QtWidgets.QTableWidget(self.verticalLayoutWidget_3)
        self.irodsDisplay.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.irodsDisplay.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.irodsDisplay.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.irodsDisplay.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.irodsDisplay.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.irodsDisplay.setObjectName("irodsDisplay")
        self.irodsDisplay.setColumnCount(2)
        self.irodsDisplay.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.irodsDisplay.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.irodsDisplay.setHorizontalHeaderItem(1, item)
        self.verticalLayout.addWidget(self.irodsDisplay)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_5 = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_2.addWidget(self.label_5)
        self.ibridgesDisplay = QtWidgets.QTableWidget(self.verticalLayoutWidget_3)
        self.ibridgesDisplay.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.ibridgesDisplay.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.ibridgesDisplay.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.ibridgesDisplay.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.ibridgesDisplay.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.ibridgesDisplay.setObjectName("ibridgesDisplay")
        self.ibridgesDisplay.setColumnCount(2)
        self.ibridgesDisplay.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.ibridgesDisplay.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.ibridgesDisplay.setHorizontalHeaderItem(1, item)
        self.verticalLayout_2.addWidget(self.ibridgesDisplay)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem4)
        self.configButton = QtWidgets.QPushButton(self.verticalLayoutWidget_3)
        self.configButton.setObjectName("configButton")
        self.horizontalLayout_3.addWidget(self.configButton)
        self.saveConfig = QtWidgets.QPushButton(self.verticalLayoutWidget_3)
        self.saveConfig.setObjectName("saveConfig")
        self.horizontalLayout_3.addWidget(self.saveConfig)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.ticketButton.setText(_translate("Form", "Login with ticket"))
        self.label_2.setText(_translate("Form", "iRods environment file:"))
        self.label_3.setText(_translate("Form", "Password"))
        self.label.setText(_translate("Form", "iRODS Login"))
        self.connectButton.setText(_translate("Form", "Connect"))
        self.label_4.setText(_translate("Form", "iRODS config:"))
        item = self.irodsDisplay.horizontalHeaderItem(0)
        item.setText(_translate("Form", "iRODS key"))
        item = self.irodsDisplay.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Value"))
        self.label_5.setText(_translate("Form", "iBridges config:"))
        item = self.ibridgesDisplay.horizontalHeaderItem(0)
        item.setText(_translate("Form", "Key"))
        item = self.ibridgesDisplay.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Value"))
        self.configButton.setText(_translate("Form", "Edit Configuration"))
        self.saveConfig.setText(_translate("Form", "Save Configuration"))
