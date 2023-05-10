"""IrodsConnector for iCommands
"""
import logging
import os
import shutil
from subprocess import call, Popen, PIPE

import irods.collection
import irods.data_object

from . import keywords as kw
from . import resource
from . import session


class IrodsConnectorIcommands:
    """Connection to an iRODS server while using iCommands.
    """

    def __init__(self, resc_man: resource.Resource, sess_man: session.Session):
        """ iRODS icommands initialization

            Parameters
            ----------
            resc_man : resource.Resource
                Instance of the Reource class
            sess_man : session.Session
                instance of the Session class

        """
        self.resc_man = resc_man
        self.sess_man = sess_man

    @staticmethod
    def icommands() -> bool:
        """

        Returns
        -------
        bool
            Are the iCommands available?
        """
        return call(['which', 'iinit'], shell=True, stderr=PIPE) == 0

    def upload_data(self, source: str, destination: irods.collection.iRODSCollection, res_name: str,
                    size: int, buff: int = kw.BUFF_SIZE, force: bool = False):
        """Upload files or folders to an iRODS collection.

        Parameters
        ----------
        source: str
            absolute path to file or folder
        destination: iRODS collection to upload to

        res_name: str
            name of the iRODS storage resource to use
        size: int
            size of data to be uploaded in bytes
        buff: int
            buffer on resource that should be left over
        force: bool
            upload without checking the available space

        """
        logging.info('iRODS UPLOAD: %s --> %s, %s', source, str(destination), str(res_name))
        if not force:
            try:
                space = self.resc_man.resource_space(res_name)
                if int(size) > (int(space) - buff):
                    raise ValueError('ERROR iRODS upload: Not enough space on resource.')
                if buff < 0:
                    raise BufferError('ERROR iRODS upload: Negative resource buffer.')
            except Exception as error:
                logging.error(error)
                raise error

        if os.path.isfile(source):
            logging.info('CREATE %s', destination.path + '/' + os.path.basename(source))
            self.sess_man.irods_session.collections.create(destination.path)
            if res_name:
                cmd = 'irsync -aK ' + source + ' i:' + destination.path + ' -R ' + res_name
            else:
                cmd = 'irsync -aK ' + source + ' i:' + destination.path
        elif os.path.isdir(source):
            self.sess_man.irods_session.collections.create(destination.path + '/' + os.path.basename(source))
            sub_coll = self.sess_man.irods_session.collections.get(destination.path + '/' + os.path.basename(source))
            if res_name:
                cmd = 'irsync -aKr ' + source + ' i:' + sub_coll.path + ' -R ' + res_name
            else:
                cmd = 'irsync -aKr ' + source + ' i:' + sub_coll.path
        else:
            logging.info('UPLOAD ERROR', exc_info=True)
            raise FileNotFoundError('ERROR iRODS upload: not a valid source path')
        logging.info('IRODS UPLOAD: %s', cmd)
        p = Popen([cmd], stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)
        out, err = p.communicate()
        logging.info('IRODS UPLOAD INFO: out:%s \nerr: %s', str(out), str(err))

    def download_data(self, source: (irods.collection.iRODSCollection, irods.data_object.iRODSDataObject), destination: str,
                      size: int, buff: int = kw.BUFF_SIZE, force: bool = False):
        """Download object or collection.

        Parameters
        ----------
        source: iRODS collection or data object

        destination: str
            absolut path to download folder
        size: int
            size of data to be downloaded in bytes
        buff: int
            buffer on the filesystem that should be left over
        """
        logging.info('iRODS DOWNLOAD: %s --> %s', str(source), destination)
        destination = '/' + destination.strip('/')
        if not os.access(destination, os.W_OK):
            logging.info('IRODS DOWNLOAD: No rights to write to destination.')
            raise PermissionError('IRODS DOWNLOAD: No rights to write to destination.')
        if not os.path.isdir(destination):
            logging.info("IRODS DOWNLOAD: Path seems to be directory, but is file.")
            raise IsADirectoryError("IRODS DOWNLOAD: Path seems to be directory, but is file.")

        if not force:
            try:
                space = shutil.disk_usage(destination).free
                if int(size) > (int(space) - buff):
                    logging.info('ERROR iRODS download: Not enough space on disk.')
                    raise ValueError('ERROR iRODS download: Not enough space on disk.')
                if buff < 0:
                    logging.info('ERROR iRODS download: Negative disk buffer.')
                    raise BufferError('ERROR iRODS download: Negative disk buffer.')
            except Exception as error:
                logging.info('DOWNLOAD ERROR', exc_info=True)
                raise error

        if self.sess_man.irods_session.data_objects.exists(source.path):
            cmd = 'irsync -K i:' + source.path + ' ' + destination + os.sep + os.path.basename(source.path)
        elif self.sess_man.irods_session.collections.exists(source.path):
            cmd = 'irsync -Kr i:' + source.path + ' ' + destination + os.sep + os.path.basename(source.path)
        else:
            raise FileNotFoundError('IRODS download: not a valid source.')
        logging.info('IRODS DOWNLOAD: %s', cmd)
        pros = Popen([cmd], stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)
        out, err = pros.communicate()
        logging.info('IRODS DOWNLOAD INFO: out:%s \nerr: %s', str(out), str(err))

    def irods_put(self, local_path: str, irods_path: str, res_name: str = ''):
        """Upload `local_path` to `irods_path` following iRODS `options`.

        Parameters
        ----------
        local_path : str
            Path of local file or directory/folder.
        irods_path : str
            Path of iRODS data object or collection.
        res_name : str
            Optional resource name.

        """
        commands = [f'iput -aK -N {kw.NUM_THREADS}']
        if res_name:
            commands.append(f'-R {res_name}')
        commands.append(f'{local_path} {irods_path}')
        call(' '.join(commands), shell=True)

    def irods_get(self, irods_path: str, local_path: str):
        """ Download `irods_path` to `local_path` following iRODS `options`.

        Parameters
        ----------
        irods_path : str
            Path of iRODS data object or collection.
        local_path : str
            Path of local file or directory/folder.

        """
        commands = [f'iget -K -N {kw.NUM_THREADS} {irods_path} {local_path}']
        call(' '.join(commands), shell=True)
