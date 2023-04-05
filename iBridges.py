#!/usr/bin/env python3
"""iBridges GUI startup script.

"""
import logging
import os
import setproctitle
import subprocess
import sys

import irods.exception
import PyQt6.QtCore
import PyQt6.QtGui
import PyQt6.QtWidgets
import PyQt6.uic

import gui
from irodsConnector.manager import IrodsConnector
import utils
from utils.irods_config_keys import irods_config_keys

app = PyQt6.QtWidgets.QApplication(sys.argv)
widget = PyQt6.QtWidgets.QStackedWidget()

# Work around a PRC XML issue handling special characters
os.environ['PYTHON_IRODSCLIENT_DEFAULT_XML'] = 'QUASI_XML'

class IrodsLoginWindow(PyQt6.QtWidgets.QDialog, gui.ui_files.irodsLoginConfigEditor.Ui_irodsLoginConfigEditor):
    """Definition and initialization of the iRODS login window.

    """

    this_application = 'iBridges'

    def __init__(self):
        super().__init__()
        self.icommands = False
        self._load_gui()
        self._init_configs_and_logging()
        self._init_envbox()
        self._ibridgesconf_display()
        self._irodsconf_display()
        self._init_password()

    def _load_gui(self):
        """

        """
        if getattr(sys, 'frozen', False):
            super().setupUi(self)
        else:
            PyQt6.uic.loadUi("gui/ui_files/irodsLoginConfigEditor.ui", self)
        self.connectButton.clicked.connect(self.login_function)
        self.ticketButton.clicked.connect(self.ticket_login)
        self.passwordField.setEchoMode(PyQt6.QtWidgets.QLineEdit.EchoMode.Password)
        self.envbox.currentTextChanged.connect(self._irodsconf_display)
        self.saveConfig.clicked.connect(self.saveConfigs)
        self.ienvAdd.clicked.connect(self.ienvAddLine)
        self.ibridgesAdd.clicked.connect(self.ibridgesAddLine)
        self.ienvDel.clicked.connect(self.ienvDelLine)
        self.ibridgesDel.clicked.connect(self.ibridgesDelLine)

    def saveConfigs(self):
        self.configErrorLabel.clear()
        self.configErrorLabel.setText("saveConfigs: TODO")

    def ienvAddLine(self):
        currentRowCount = self.irodsDisplay.rowCount()
        self.irodsDisplay.insertRow(currentRowCount)

    def ibridgesAddLine(self):
        currentRowCount = self.ibridgesDisplay.rowCount()
        self.ibridgesDisplay.insertRow(currentRowCount)

    def ienvDelLine(self):
        selected = self.irodsDisplay.selectedIndexes()
        if selected:
            idx = selected[0]
            self.irodsDisplay.removeRow(idx.row())

    def ibridgesDelLine(self):
        selected = self.ibridgesDisplay.selectedIndexes()
        if selected:
            idx = selected[0]
            self.ibridgesDisplay.removeRow(idx.row())

    def _init_configs_and_logging(self):
        """

        """
        # iBridges configuration
        ibridges_path = utils.utils.LocalPath(
            os.path.join('~', '.ibridges')).expanduser()
        
        if not ibridges_path.is_dir():
            ibridges_path.mkdir(parents=True)
        # Loads ibridges config if present, otherwise instantiaties ibridges context with {}
        self.context = utils.utils.Context()
        self.irods_path = utils.utils.LocalPath(
            os.path.join('~', '.irods')).expanduser()

        if not self.irods_path.is_dir():
            self.irods_path.mkdir(parents=True)
        # iBridges logging
        utils.utils.setup_logger(ibridges_path, 'iBridges')

    def _ibridgesconf_display(self):
        self.ibridgesDisplay.setRowCount(len(self.context.ibridges_env.keys()))
        self.ibridgesDisplay.setColumnWidth(0, 200)
        self.ibridgesDisplay.setColumnWidth(1, 200)
        for row, key in enumerate(self.context.ibridges_env):
            self.ibridgesDisplay.setItem(row, 0, PyQt6.QtWidgets.QTableWidgetItem(key))
            self.ibridgesDisplay.setItem(row, 1, PyQt6.QtWidgets.QTableWidgetItem(str(self.context.ibridges_env[key])))

    def _irodsconf_display(self):
        temp_ienv_file = self.irods_path.joinpath(self.envbox.currentText())
        temp_ienv = utils.utils.JsonConfig(temp_ienv_file).config

        self.irodsDisplay.setRowCount(len(temp_ienv))
        self.irodsDisplay.setColumnWidth(0, 200)
        self.irodsDisplay.setColumnWidth(1, 200)
        
        for row, key in enumerate(temp_ienv):
            self.irodsDisplay.setItem(row, 0, PyQt6.QtWidgets.QTableWidgetItem(key))
            self.irodsDisplay.setItem(row, 1, PyQt6.QtWidgets.QTableWidgetItem(
                str(temp_ienv[key])))

    def _init_envbox(self):
        """Populate environment drop-down.

        """
        env_jsons = [
            path.name for path in
            self.irods_path.glob('irods_environment*json')]
        if len(env_jsons) == 0:
            self.envError.setText(f'ERROR: no "irods_environment*json" files found in {self.irods_path}')
        self.envbox.clear()
        self.envbox.addItems(env_jsons)
        envname = ''
        if 'last_ienv' in self.context.ibridges_env and self.context.ibridges_env['last_ienv'] in env_jsons:
            envname = self.context.ibridges_env['last_ienv']
        elif 'irods_environment.json' in env_jsons:
            envname = 'irods_environment.json'
        index = 0
        if envname:
            index = self.envbox.findText(envname)
        self.envbox.setCurrentIndex(index)

    def _init_password(self):
        """

        """
        conn = IrodsConnector()
        if conn.password:
            self.passwordField.setText(conn.password)

    def _reset_mouse_and_error_labels(self):
        """Reset cursor and clear error text

        """
        self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
        self.passError.setText('')
        self.envError.setText('')

    def login_function(self):
        """Check connectivity and log in to iRODS handling common errors.

        """
        irods_env_file = self.irods_path.joinpath(self.envbox.currentText())
        # TODO expand JsonConfig usage to all relevant modules
        self.context.read_irods_config(irods_env_file)
        if self.context.irods_env is None:
            self.passError.clear()
            self.envError.setText('ERROR: iRODS environment file not found.')
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
            return
        if not utils.utils.can_connect(self.context.irods_env['irods_host']):
            logging.info('iRODS login: No network connection to server')
            self.envError.setText('No network connection to server')
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
            return
        self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.WaitCursor))
        password = self.passwordField.text()
        try:
            conn = IrodsConnector(irods_env_file=irods_env_file, password=password)
            # Add own filepath for easy saving.
            self.context.update_ibridges_keyval('ui_ienvFilePath', irods_env_file)
            self.context.update_ibridges_keyval('last_ienv', irods_env_file.name)
            # Save iBridges config to disk and combine with iRODS config.
            self.context.save_ibridges_config()
            # widget is a global variable
            stacked_envs = {}
            stacked_envs.update(self.context.irods_env)
            stacked_envs.update(self.context.ibridges_env)
            browser = gui.mainmenu(widget, conn, stacked_envs)
            if len(widget) == 1:
                widget.addWidget(browser)
            self._reset_mouse_and_error_labels()
            # self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
            widget.setCurrentIndex(widget.currentIndex()+1)
        except (irods.exception.CAT_INVALID_AUTHENTICATION,
                irods.exception.PAM_AUTH_PASSWORD_FAILED,
                irods.exception.CAT_INVALID_USER,
                ConnectionRefusedError):
            self.envError.clear()
            self.passError.setText('ERROR: Wrong password.')
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
        except irods.exception.CAT_PASSWORD_EXPIRED:
            self.envError.clear()
            self.passError.setText('ERROR: Cached password expired. Re-enter password.')
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
        except irods.exception.NetworkException:
            self.passError.clear()
            self.envError.setText('iRODS server ERROR: iRODS server down.')
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
        except Exception as unknown:
            message = f'Something went wrong: {unknown}'
            logging.exception(message)
            # logging.info(repr(error))
            self.envError.setText(message)
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))

    def ticket_login(self):
        """Log in to iRODS using a ticket.

        """
        # widget is a global variable
        browser = gui.mainmenu(widget, None, None)
        browser.menuOptions.clear()
        browser.menuOptions.deleteLater()
        if len(widget) == 1:
            widget.addWidget(browser)
        self._reset_mouse_and_error_labels()
        # self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
        widget.setCurrentIndex(widget.currentIndex()+1)

def closeClean():
    activeWidget = widget.currentWidget()
    try:
        activeWidget.ic.cleanup()
    except:
        pass

def main():
    """Main function

    """
    setproctitle.setproctitle('iBridges')
    login_window = IrodsLoginWindow()
    widget.addWidget(login_window)
    widget.show()
    #app.setQuitOnLastWindowClosed(False)
    app.lastWindowClosed.connect(closeClean)
    app.exec()


if __name__ == "__main__":
    main()
