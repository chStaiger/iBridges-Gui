# Form implementation generated from reading ui file 'ibridgesgui/ui_files/welcome.ui'
#
# Created by: PyQt6 UI code generator 6.6.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore


class Ui_Welcome(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(401, 300)
        Form.setStyleSheet("QWidget\n"
"{\n"
"    background-color: rgb(211,211,211);\n"
"    color: rgb(88, 88, 90);\n"
"    selection-background-color: rgb(21, 165, 137);\n"
"    selection-color: rgb(245, 244, 244);\n"
"    \n"
"    font: 16pt\n"
"}\n"
"\n"
"QLabel\n"
"{\n"
"  background-color: rgb(211,211,211);\n"
"}\n"
"\n"
"QLabel#error_label\n"
"{\n"
"   color: rgb(220, 130, 30);\n"
"}\n"
"\n"
"QTabBar::tab:top:selected {\n"
"    background-color: rgb(21, 165, 137);\n"
"    color: rgb(88, 88, 90);\n"
"}\n"
"\n"
"")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
