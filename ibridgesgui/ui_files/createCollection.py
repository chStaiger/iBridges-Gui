# Form implementation generated from reading ui file 'ibridgesgui/ui_files/createCollection.ui'
#
# Created by: PyQt6 UI code generator 6.6.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_createCollection(object):
    def setupUi(self, createCollection):
        createCollection.setObjectName("createCollection")
        createCollection.resize(500, 200)
        createCollection.setMinimumSize(QtCore.QSize(500, 200))
        createCollection.setMaximumSize(QtCore.QSize(500, 200))
        createCollection.setStyleSheet("QWidget\n"
"{\n"
"    color: rgb(86, 184, 139);\n"
"    background-color: rgb(54, 54, 54);\n"
"    font: 16pt\n"
"}\n"
"\n"
"QLineEdit\n"
"{\n"
"    background-color: rgb(85, 87, 83);\n"
"    border-color: rgb(217, 174, 23)\n"
"}\n"
"\n"
"QLabel#error_label\n"
"{\n"
"    color: rgb(217, 174, 23);\n"
"}\n"
"\n"
"")
        self.verticalLayout = QtWidgets.QVBoxLayout(createCollection)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(parent=createCollection)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.coll_path_input = QtWidgets.QLineEdit(parent=createCollection)
        self.coll_path_input.setObjectName("coll_path_input")
        self.verticalLayout.addWidget(self.coll_path_input)
        self.error_label = QtWidgets.QLabel(parent=createCollection)
        self.error_label.setStyleSheet("")
        self.error_label.setText("")
        self.error_label.setObjectName("error_label")
        self.verticalLayout.addWidget(self.error_label)
        spacerItem1 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.verticalLayout.addItem(spacerItem1)
        self.buttonBox = QtWidgets.QDialogButtonBox(parent=createCollection)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(createCollection)
        self.buttonBox.accepted.connect(createCollection.accept) # type: ignore
        self.buttonBox.rejected.connect(createCollection.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(createCollection)

    def retranslateUi(self, createCollection):
        _translate = QtCore.QCoreApplication.translate
        createCollection.setWindowTitle(_translate("createCollection", "New Collection"))
        self.label.setText(_translate("createCollection", "iRODS path                                      /"))
