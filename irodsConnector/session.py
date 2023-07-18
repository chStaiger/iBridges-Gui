""" session operations
"""
import logging

import irods.connection
import irods.exception
import irods.password_obfuscation
import irods.session

import utils


class Session:
    """Irods session authentication.

    """
    context = utils.context.Context()

    def __init__(self, password=''):
        """ iRODS authentication with Python client.

        Parameters
        ----------
        password : str
            Plain text password.

        """
        self._password = password
        self._irods_session = None

    def __del__(self):
        del self.irods_session

    @property
    def irods_session(self) -> irods.session.iRODSSession:
        """iRODS session creation.

        Returns
        -------
        iRODSSession
            iRODS connection based on the current environment and password.

        """
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

    # Authentication workflow methods
    #

    def has_valid_irods_session(self) -> bool:
        """Check if the iRODS session is valid.

        Returns
        -------
        bool
            Is the session valid?

        """
        return self.server_version != ()

    def connect(self):
        """Establish an iRODS session.

        """
        user = self.context.irods_environment.config.get('irods_user_name', '')
        if user == 'anonymous':
            try:
                # TODO: implement and test for SSL enabled iRODS
                logging.debug('iRODS LOGIN of anonymous user')
                # self._irods_session = iRODSSession(user='anonymous',
                #                        password='',
                #                        zone=zone,
                #                        port=1247,
                #                        host=host)
                assert False
            except Exception:
                logging.error('Anonymous LOGIN FAILED: %s', 'Not implemented')
                return {'successful': False, 'reason': 'Not implemented'}
        else:  # authentication with irods environment and password
            if self._password == '':
                print("Auth without password")
                # use cached password of .irodsA built into prc
                return self.authenticate_using_auth_file()
            else:
                print("Auth with password")
                # irods environment and given password
                logging.info('FULL ENVIRONMENT SESSION')
                return self.authenticate_using_password()

    def authenticate_using_password(self):
        try:
            self._irods_session = irods.session.iRODSSession(password=self._password,
                                                             **self.context.irods_environment.config)
            assert self._irods_session.server_version != ()
            logging.info('IRODS LOGIN SUCCESS: %s:%s',
                         self._irods_session.host, self._irods_session.port)
            self._write_pam_password()
            return {'successful': True}
        except Exception as e:
            logging.error('FULL ENVIRONMENT LOGIN FAILED: %r', e)
            return {'successful': False, 'reason': repr(e)}

    def authenticate_using_auth_file(self):
        logging.info('AUTH FILE SESSION')
        try:
            self._irods_session = irods.session.iRODSSession(irods_env_file=self.context.irods_env_file)
            assert self._irods_session.server_version != ()
            logging.info('IRODS LOGIN SUCCESS: %s:%s',
                         self._irods_session.host, self._irods_session.port)
            return {'successful': True}
        except Exception as e:
            logging.error('AUTH FILE LOGIN FAILED')
            logging.error('Have you set the iRODS environment file correctly?')
            return {'successful': False, 'reason': repr(e)}

    # Introspection properties
    #
    @property
    def davrods(self) -> str:
        """DavRODS server URL.

        Returns
        -------
        str
            URL of the configured DavRODS server.

        """
        return self.context.ibridges_configuration.config.get('davrods_server', '')

    @property
    def default_resc(self) -> str:
        """Default resource name from iRODS environment.

        Returns
        -------
        str
            Resource name.

        """
        if self._irods_session:
            return self._irods_session.default_resource
        return ''

    @property
    def host(self) -> str:
        """Retrieve hostname of the iRODS server.

        Returns
        -------
        str
            Hostname.

        """
        if self._irods_session:
            return self._irods_session.host
        return ''

    @property
    def port(self) -> str:
        """Retrieve port of the iRODS server.

        Returns
        -------
        str
            Port.

        """
        if self._irods_session:
            return self._irods_session.port
        return ''

    @property
    def server_version(self) -> tuple:
        """Retrieve version of the iRODS server

        Returns
        -------
        tuple
            Server version: (major, minor, patch).

        """
        try:
            return self._irods_session.server_version
        except Exception:
            return ()

    @property
    def username(self) -> str:
        """Retrieve username.

        Returns
        -------
        str
            Username.

        """
        if self._irods_session:
            return self._irods_session.username
        return ''

    @property
    def zone(self) -> str:
        """Retrieve the zone name.

        Returns
        -------
        str
            Zone.

        """
        if self._irods_session:
            return self._irods_session.zone
        return ''

    def _write_pam_password(self):
        """Store the password in the iRODS
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
