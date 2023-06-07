# Form implementation generated from reading ui file 'gui/ui_files/example_tab.ui'
#
# Created by: PyQt6 UI code generator 6.3.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_ExampleTab(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(767, 429)
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
"QTreeView\n"
"{\n"
"background-color: rgb(85, 87, 83);\n"
"}\n"
"\n"
"QLabel#errorLabel\n"
"{\n"
"    color: rgb(217, 174, 23);\n"
"}")
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_2)
        self.error_label = QtWidgets.QLabel(Form)
        self.error_label.setText("")
        self.error_label.setObjectName("error_label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.error_label)
        self.textField = QtWidgets.QLineEdit(Form)
        self.textField.setObjectName("textField")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.textField)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.formLayout.setItem(1, QtWidgets.QFormLayout.ItemRole.FieldRole, spacerItem)
        self.horizontalLayout.addLayout(self.formLayout)
        self.irodsTreeView = QtWidgets.QTreeView(Form)
        self.irodsTreeView.setObjectName("irodsTreeView")
        self.horizontalLayout.addWidget(self.irodsTreeView)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Info Text"))
        self.label_2.setText(_translate("Form", "Error Label"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
