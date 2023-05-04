""" session operations
"""
import logging
import os
import ssl

import irods.connection
import irods.exception
import irods.password_obfuscation
import irods.session

import utils
from . import keywords as kw


class Session(object):
    """Irods session operations """
    _irods_session = None
    # Singleton instance initially configured in iBridges.py
    context = utils.context.Context()

    def __init__(self, password=''):
        """ iRODS authentication with Python client.

        Parameters
        ----------
        password : str
            Plain text password.

        The 'password' property can autoload from its cache, but can be
        overridden by `password` argument.  The iRODS authentication
        file is expected in the standard location (~/.irods/.irodsA) or
        to be specified in the local environment with the
        IRODS_AUTHENTICATION_FILE variable.

        """
        self._password = password

    def __del__(self):
        del self.irods_session

    @property
    def conf(self) -> dict:
        """iBridges configuration dictionary.

        Returns
        -------
        dict
            Configuration from JSON serialized string.

        """
        if self.context.ibridges_configuration:
            return self.context.ibridges_configuration.config
        return {}

    @property
    def davrods(self) -> str:
        """DavRODS server URL.

        Returns
        -------
        str
            URL of the configured DavRODS server.

        """
        return self.conf.get('davrods_server', '')

    @property
    def default_resc(self) -> str:
        """Default resource name from iRODS environment.

        Returns
        -------
        str
            Resource name.

        """
        if self.has_irods_session():
            return self.irods_session.default_resource
        return ''

    @property
    def host(self) -> str:
        """Retrieve hostname of the iRODS server

        Returns
        -------
        str
            Hostname.

        """
        if self.has_irods_session():
            return self.irods_session.host
        return ''

    @property
    def ienv(self) -> dict:
        """iRODS environment dictionary.

        Returns
        -------
        dict
            Environment from JSON serialized string.
        """
        if self.context.irods_environment:
            return self.context.irods_environment.config
        return {}

    @property
    def port(self) -> str:
        """Retrieve port of the iRODS server

        Returns
        -------
        str
            Port.

        """
        if self.has_irods_session():
            return str(self.irods_session.port)
        return ''

    @property
    def username(self) -> str:
        """Retrieve username

        Returns
        -------
        str
            Username.

        """
        if self.has_irods_session():
            return self.irods_session.username
        return ''

    @property
    def server_version(self) -> tuple:
        """Retrieve version of the iRODS server

        Returns
        -------
        tuple
            Server version: (major, minor, patch).

        """
        if self.has_irods_session():
            return self.irods_session.server_version
        return ()

    @property
    def zone(self) -> str:
        """Retrieve the zone name

        Returns
        -------
        str
            Zone.

        """
        if self.has_irods_session():
            return self.irods_session.zone
        return ''

    @property
    def password(self) -> str:
        """iRODS password.

        Returns
        -------
        str
            iRODS password pre-set or decoded from iRODS authentication
            file. Can be a PAM negotiated password.

        """
        if not self._password:
            irods_auth_file = os.environ.get(
                'IRODS_AUTHENTICATION_FILE', None)
            if irods_auth_file is None:
                irods_auth_file = utils.path.LocalPath(
                    '~/.irods/.irodsA').expanduser()
            if irods_auth_file.exists():
                with open(irods_auth_file, encoding='utf-8') as authfd:
                    self._password = irods.password_obfuscation.decode(
                        authfd.read())
        return self._password

    @password.setter
    def password(self, password: str):
        """iRODS password setter method.

        Pararmeters
        -----------
        password: str
            Unencrypted iRODS password.

        """
        self._password = password

    @password.deleter
    def password(self):
        """iRODS password deleter method.

        """
        self._password = ''

    @property
    def irods_session(self) -> irods.session.iRODSSession:
        """iRODS session creation.

        Returns
        -------
        iRODSSession
            iRODS connection based on given environment and password.

        """
        if self._irods_session is None:
            if not self.context.irods_env_file:
                if 'last_ienv' in self.conf:
                    print(f'{kw.YEL}"irods_env_file" not set.  Using "last_ienv" value.{kw.DEFAULT}')
                    irods_path = utils.path.LocalPath(utils.context.IRODS_DIR).expanduser()
                    self.context.irods_env_file = irods_path.joinpath(self.conf['last_ienv'])
                else:
                    print(f'{kw.RED}No iRODS session: "irods_env_file" not set!{kw.DEFAULT}')
                    return
            options = {
                'irods_env_file': str(self.context.irods_env_file),
            }
            if self.ienv is not None:
                options.update(self.ienv)
            given_pass = self.password
            del self.password
            # Accessing reset password property scrapes cached password.
            cached_pass = self.password
            del self.password
            if given_pass != cached_pass:
                options['password'] = given_pass
            self._irods_session = self._get_irods_session(options)
            # If session exists, it is validated.
            if self._irods_session:
                if given_pass != cached_pass:
                    self._write_pam_password()
                print('Welcome to iRODS:')
                print(f'iRODS Zone: {self._irods_session.zone}')
                print(f'You are: {self._irods_session.username}')
                print(f'Default resource: {self.default_resc}')
                print('You have access to: \n')
                home_path = f'/{self._irods_session.zone}/home'
                if self._irods_session.collections.exists(home_path):
                    colls = self._irods_session.collections.get(home_path).subcollections
                    print('\n'.join([coll.path for coll in colls]))
                logging.info(
                    'IRODS LOGIN SUCCESS: %s, %s, %s', self._irods_session.username,
                    self._irods_session.zone, self._irods_session.host)
        return self._irods_session

    @irods_session.deleter
    def irods_session(self):
        """Properly delete iRODS session.
        """
        if self._irods_session is not None:
            # In case the iRODS session is not fully there.
            try:
                self._irods_session.cleanup()
            except NameError:
                pass
            del self._irods_session
            self._irods_session = None

    @staticmethod
    def _get_irods_session(options):
        """Run through different types of authentication methods and
        instantiate an iRODS session.

        Parameters
        ----------
        options : dict
            Initial iRODS settings for the session.

        Returns
        -------
        iRODSSession
            iRODS connection based on given environment and password.

        """
        irods_env_file = options.pop('irods_env_file')
        if 'password' not in options:
            try:
                print('AUTH FILE SESSION')
                session = irods.session.iRODSSession(
                    irods_env_file=irods_env_file)
                _ = session.server_version
                return session
            except TypeError as typeerr:
                print(f'{kw.RED}AUTH FILE LOGIN FAILED: Have you set the iRODS environment file correctly?{kw.DEFAULT}')
                raise typeerr
            except Exception as error:
                print(f'{kw.RED}AUTH FILE LOGIN FAILED (unhandled): {error!r}{kw.DEFAULT}')
                raise error
        else:
            password = options.pop('password')
            try:
                print('FULL ENVIRONMENT SESSION')
                session = irods.session.iRODSSession(password=password, **options)
                _ = session.server_version
                return session
            except Exception as autherror:
                logging.info('AUTHENTICATION ERROR')
                print(f'{kw.RED}AUTHENTICATION ERROR: {autherror!r}{kw.DEFAULT}')
                raise autherror

    def _write_pam_password(self):
        """Store the returned PAM/LDAP password in the iRODS
        authentication file in obfuscated form.

        """
        connection = self._irods_session.pool.get_connection()
        pam_passwords = self._irods_session.pam_pw_negotiated
        if len(pam_passwords):
            irods_auth_file = self._irods_session.get_irods_password_file()
            with open(irods_auth_file, 'w', encoding='utf-8') as authfd:
                authfd.write(
                    irods.password_obfuscation.encode(pam_passwords[0]))
        else:
            logging.info('WARNING -- unable to cache obfuscated password locally')
        connection.release()

    def connect(self):
        """Manually establish an iRODS session.

        """
        if not self.has_irods_session():
            _ = self.irods_session.server_version

    def has_irods_session(self) -> bool:
        """Check if an iRODS session has been assigned to its shadow
        variable.

        Returns
        -------
        bool
            Has a session been set?

        """
        return self._irods_session is not None
