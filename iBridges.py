#!/usr/bin/env python3
"""iBridges GUI startup script.

"""
import datetime
import logging
import logging.handlers
import os
import setproctitle
import sys

import irods.exception
import PyQt6.QtCore
import PyQt6.QtGui
import PyQt6.QtWidgets
import PyQt6.uic

import gui
import irodsConnector
import utils

# Global constants
LOG_LEVEL = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}
THIS_APPLICATION = 'iBridges'

# Application globals
app = PyQt6.QtWidgets.QApplication(sys.argv)
stacked_widget = PyQt6.QtWidgets.QStackedWidget()

# Work around a PRC XML issue handling special characters
os.environ['PYTHON_IRODSCLIENT_DEFAULT_XML'] = 'QUASI_XML'


class IrodsLoginWindow(PyQt6.QtWidgets.QDialog,
                       gui.ui_files.irodsLogin.Ui_irodsLogin,
                       utils.context.ContextContainer):
    """The login widget.

    """
    cached_password = ''
    given_password = ''
    icommands = False
    this_application = ''

    def __init__(self):
        """Initialize the login window.

        """
        super().__init__()
        self.irods_path = utils.path.LocalPath(utils.context.IRODS_DIR).expanduser()
        self._load_gui()
        self._init_envbox()
        self._init_password()

    def _load_gui(self):
        """Initialize and connect the GUI elements.

        """
        if getattr(sys, 'frozen', False):
            super().setupUi(self)
        else:
            PyQt6.uic.loadUi("gui/ui_files/irodsLogin.ui", self)
        self.selectIcommandsButton.toggled.connect(self.setup_icommands)
        self.standardButton.toggled.connect(self.setup_standard)
        self.connectButton.clicked.connect(self.login_function)
        self.ticketButton.clicked.connect(self.ticket_login)
        self.passwordField.setEchoMode(PyQt6.QtWidgets.QLineEdit.EchoMode.Password)

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
        if 'last_ienv' in self.conf and self.conf['last_ienv'] in env_jsons:
            envname = self.conf['last_ienv']
        elif 'irods_environment.json' in env_jsons:
            envname = 'irods_environment.json'
        index = 0
        if envname:
            index = self.envbox.findText(envname)
        self.envbox.setCurrentIndex(index)

    def _init_password(self):
        """Store this initial cached password scraped from auth file and
        set it to the password field so the user sees that previous
        login credentials have been found.

        """
        self.cached_password = self.conn.password
        self.passwordField.setText(self.cached_password)

    def reset_mouse_and_error_labels(self):
        """Reset cursor and clear any error text.

        """
        self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
        self.passError.setText('')
        self.envError.setText('')

    def setup_standard(self):
        """Check the state of the radio button for using the pure Python
        client.

        """
        if self.standardButton.isChecked():
            self._init_envbox()
            self.icommands = False

    def setup_icommands(self):
        """Check the state of the radio button for using iCommands.
        This includes a check for the existence of the iCommands on the
        current system.

        """
        if self.selectIcommandsButton.isChecked():
            self.icommandsError.setText('')
            if self.conn.icommands:
                self.icommands = True
                # TODO support arbitrary iRODS environment file for iCommands
            else:
                self.icommandsError.setText('ERROR: no iCommands found')
                self.standardButton.setChecked(True)

    def login_function(self):
        """Check connectivity and log in to iRODS handling common errors.

        The initial and subsequent sessions need to be handled
        differently.  Store the initial given password to see when the
        user has entered a new one.

        """
        # Replacement connector and currently cached password (required
        # for subsequent sessions)
        if not self.context.irods_connector:
            logging.debug('Setting new instance of the IrodsConnector')
            self.context.irods_connector = irodsConnector.manager.IrodsConnector()
            self.cached_password = self.conn.password
        irods_env_file = self.irods_path.joinpath(self.envbox.currentText())
        self.context.irods_env_file = irods_env_file
        logging.debug(f'IRODS ENVIRONMENT FILE SET: {irods_env_file.name}')
        self.envError.setText('')
        if not (self.context.irods_environment.config and self.context.ienv_is_complete()):
            message = 'iRODS environment missing or incomplete.'
            logging.error(message)
            self.context.irods_environment.reset()
            self.passError.clear()
            self.envError.setText(message)
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
            return
        irods_host = self.ienv.get('irods_host', '')
        if not utils.utils.can_connect(irods_host):
            message = f'No network connection to server: {irods_host}'
            logging.warning(message)
            self.envError.setText(message)
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
            return
        self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.WaitCursor))
        self.conf['last_ienv'] = irods_env_file.name
        self.context.save_ibridges_configuration()
        current_password = self.passwordField.text()
        known_passwords = (self.cached_password, self.given_password)
        # This a subsequent session if `given_password` is already set.
        if self.given_password and current_password in known_passwords:
            self.given_password = self.cached_password
        else:
            self.given_password = current_password
        self.conn.password = self.given_password
        logging.debug(f'IRODS PASSWORD SET: {"*"*len(self.given_password)*2}')
        try:
            self.conn.connect()
        except (irods.exception.CAT_INVALID_AUTHENTICATION,
                irods.exception.PAM_AUTH_PASSWORD_FAILED,
                irods.exception.CAT_INVALID_USER,
                ConnectionRefusedError):
            message = 'Wrong password!  Try again'
            logging.error(message)
            self.envError.clear()
            self.passError.setText(message)
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
            return
        except irods.exception.CAT_PASSWORD_EXPIRED:
            message = 'Cached password expired!  Re-enter password'
            logging.error(message)
            self.envError.clear()
            self.passError.setText(message)
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
            return
        except irods.exception.NetworkException:
            message = 'iRODS server down!  Check and try again'
            logging.error(message)
            self.passError.clear()
            self.envError.setText(message)
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
            return
        except Exception as unknown:
            message = f'Something unexpected occurred: {unknown!r}'
            logging.exception(message)
            self.envError.setText(message)
            self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
            return
        # stacked_widget is a global variable
        browser = gui.mainmenu.MainMenu(stacked_widget)
        if len(stacked_widget) == 1:
            stacked_widget.addWidget(browser)
        self.reset_mouse_and_error_labels()
        stacked_widget.setCurrentIndex(stacked_widget.currentIndex()+1)

    def ticket_login(self):
        """Log in to iRODS using a ticket.

        """
        # stacked_widget is a global variable
        browser = gui.mainmenu.MainMenu(stacked_widget)
        browser.menuOptions.clear()
        browser.menuOptions.deleteLater()
        if len(stacked_widget) == 1:
            stacked_widget.addWidget(browser)
        self.reset_mouse_and_error_labels()
        # self.setCursor(PyQt6.QtGui.QCursor(PyQt6.QtCore.Qt.CursorShape.ArrowCursor))
        stacked_widget.setCurrentIndex(stacked_widget.currentIndex()+1)


def close_clean():
    """Clean up connections in preparation to close application.

    """
    context = utils.context.Context()
    if context.irods_connector:
        context.irods_connector.cleanup()


def init_logger():
    """Initialize the application logging service.

    """
    logger = logging.getLogger()
    logdir = utils.path.LocalPath(utils.context.IBRIDGES_DIR).expanduser()
    logfile = logdir.joinpath(f'{THIS_APPLICATION}.log')
    log_formatter = logging.Formatter(
        '[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s')
    file_handler = logging.handlers.RotatingFileHandler(logfile, 'a', 100000, 1)
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)
    # Indicate start of a new session
    with open(logfile, 'a', encoding='utf-8') as logfd:
        logfd.write('\n\n')
        underscores = f'{"_" * 50}\n'
        logfd.write(underscores * 2)
        logfd.write(f'\t\t{datetime.datetime.now().isoformat()}\n')
        logfd.write(underscores * 2)


def set_log_level(log_level: int):
    """Set the log level excluding DEBUG-level entries from other
    modules.

    Parameters
    ----------
    log_level : int
        Level to set the current logger.

    """
    logging.getLogger().setLevel(log_level)
    if log_level == logging.DEBUG:
        for logger in logging.Logger.manager.loggerDict.values():
            if hasattr(logger, 'name') and logger.name != 'root':
                logger.disabled = True


def main():
    """Main function.

    Initialize the context singleton, create the login widget, and
    execute the main application thread.

    """
    # Initialize logger first because Context may want to log as well.
    init_logger()
    # Singleton Context
    context = utils.context.Context()
    context.application_name = THIS_APPLICATION
    # Context is required to get the log_level from the configuration.
    verbose = context.ibridges_configuration.config.get('verbose', 'info')
    log_level = LOG_LEVEL.get(verbose, logging.INFO)
    set_log_level(log_level)
    context.irods_connector = irodsConnector.manager.IrodsConnector()
    setproctitle.setproctitle(context.application_name)
    login_window = IrodsLoginWindow()
    login_window.this_application = context.application_name
    stacked_widget.addWidget(login_window)
    stacked_widget.show()
    # app.setQuitOnLastWindowClosed(False)
    app.lastWindowClosed.connect(close_clean)
    app.exec()


if __name__ == "__main__":
    main()
