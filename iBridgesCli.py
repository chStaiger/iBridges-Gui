#!/usr/bin/env python3

"""
Commandline client to upload data to a storage service and double-link the storage location with a metadata store.

Implemented for:
    Storage types:
        iRODS
"""
import argparse
import logging
import configparser
import os
import sys
import json
import getpass
from pathlib import Path
from irods.exception import CollectionDoesNotExist, SYS_INVALID_INPUT_PARAM
import irodsConnector.keywords as kw
from irodsConnector.manager import IrodsConnector
import utils
from utils.elab_plugin import ElabPlugin


def plugin_hook(func):
    """
    Callable function for the plugin_hook decorator.
    """
    def wrapper(self, **kwargs):
        """
        Executes hooked functions pre and post the decorated function.
        """

        pre_fs = post_fs = []
        actions = [x['actions'] for x in self.plugins if x['hook'] == func.__name__]
        if actions:
            pre_fs = [x['function'] for x in actions[0] if x['slot'] == 'pre']
            post_fs = [x['function'] for x in actions[0] if x['slot'] == 'post']

        for pre_f in pre_fs:
            pre_f(calling_class=self, **kwargs)

        func(self, **kwargs)

        for post_f in post_fs:
            post_f(calling_class=self, **kwargs)

    return wrapper


class IBridgesCli:                          # pylint: disable=too-many-instance-attributes
    """
    Class for up- and downloading to YODA/iRODS via the command line.
    Includes option for writing metadata to Elab Journal.
    """
    context = utils.context.Context()

    def __init__(self,                      # pylint: disable=too-many-arguments
                 local_path: str,
                 irods_path: str,
                 irods_env: str,
                 irods_resc: str,
                 operation: str,
                 logdir: str,
                 plugins: list[dict] = None) -> None:

        self.irods_env = None
        self.irods_path = None
        self.irods_resc = None
        self.local_path = None
        self.config_file = None
        self.download_finished = None
        self.upload_finished = None
        self.irods_conn = None
        
        default_irods_env = utils.path.LocalPath('~/.irods', 'irods_environment.json').expanduser()
        logdir_path = utils.path.LocalPath(logdir)

        # CLI parameters override ibridges_config.json
        last_env = None
        if self.context.ibridges_configuration.config.get('last_ienv', ''):
            last_env = utils.path.LocalPath(
                    '~/.irods/'+self.context.ibridges_configuration.config.get('last_ienv', ''))
        irods_env_file = irods_env or last_env or default_irods_env \
            or self._clean_exit("need iRODS environment file", True)
        self.context.irods_environment.reset()
        self.context.irods_env_file = irods_env_file
        self.irods_path = irods_path or self._clean_exit("need iRODS path", True)
        self.local_path = local_path or self._clean_exit("need local path", True)

        self.local_path = Path(os.path.expanduser(self.local_path))
        self.irods_path = self.irods_path.rstrip("/")

        # checking if paths actually exist
        for path in [self.context.irods_env_file, self.local_path, logdir_path]:
            if not path.exists():
                self._clean_exit(f"{path} does not exist")

        # reading default irods_resc from env file if not specified otherwise
        self.irods_resc = irods_resc \
                or self.context.irods_environment.config.get('irods_default_resource', '') \
                or self._clean_exit("need an iRODS resource", True)

        self.operation = operation
        self.plugins = self._cleanup_plugins(plugins)
        utils.utils.init_logger("iBridgesCli")
        utils.utils.set_log_level()
        self._run()

    @classmethod
    def _cleanup_plugins(cls, plugins):
        """
            Format:
            plugins = [
                {
                    'hook': 'upload',
                    'actions' : [
                        { 'slot': 'pre', 'function': function_before },
                        { 'slot': 'post', 'function': function_after }
                    ]
                }
            ]
        """
        plugins = [x for x in plugins if 'hook' in x and 'actions' in x]
        for key, val in enumerate(plugins):
            plugins[key]['actions'] = [x for x in val['actions']
                                       if 'function' in x and callable(x['function'])
                                       and 'slot' in x and x['slot'] in ['pre', 'post']]

        return [x for x in plugins if len(x['actions']) > 0]

    @classmethod
    def from_arguments(cls, **kwargs):
        """
        Creates class instance from CLI-arguments. Optionally, functions to be triggered
        at hook-points can be specified.
        """
        cls.parser = argparse.ArgumentParser(
            prog='python iBridgesCli.py',
            description="",
            epilog=""
            )
        default_logdir = utils.path.LocalPath('~/.ibridges').expanduser()

        cls.parser.add_argument('--local_path', '-l',
                                help='Local path to download to, or upload from',
                                type=str)
        cls.parser.add_argument('--irods_path', '-i',
                                help='iRods path to upload to, or download from',
                                type=str)
        cls.parser.add_argument('--operation', '-o',
                                type=str,
                                choices=['upload', 'download'],
                                required=True)
        cls.parser.add_argument('--env', '-e', type=str,
                                help=f'Path to iRods environment file (irods_environment.json).')
        cls.parser.add_argument('--irods_resc', '-r', type=str,
                                help='iRods resource. If omitted default will be read from iRods env file.')
        cls.parser.add_argument('--logdir', type=str,
                                help=f'Directory for logfile. Default: {default_logdir}',
                                default=default_logdir)

        args = cls.parser.parse_args()

        return cls(irods_env=args.env,
                   irods_resc=args.irods_resc,
                   local_path=args.local_path,
                   irods_path=args.irods_path,
                   operation=args.operation,
                   logdir=args.logdir,
                   plugins=kwargs["plugins"] if "plugins" in kwargs else None
                   )

    def _clean_exit(self, message=None, show_help=False, exit_code=1):
        if message:
            if exit_code == 0:
                logging.info(message)
            else:
                logging.error(message)
        if show_help:
            IBridgesCli.parser.print_help()
        if self.irods_conn:
            self.irods_conn.cleanup()
        sys.exit(exit_code)

    def connect_irods(self):
        """
        Connect to iRods instance after interactivelty asking for password.
        """
        attempts = 0
        while True:
            secret = getpass.getpass(
                    f'Password for {self.context.irods_env_file} (leave empty to use cached): ')
            try:
                if not (self.context.ienv_is_complete()):
                    self._clean_exit("iRODS environment file incomplete", True)
                # Fix to having a functional ic
                # TODO: remove "contect.irods_connector "later
                self.irods_conn = context.irods_connector = IrodsConnector(secret)
                self.irods_conn.ibridges_configuration = self.context.ibridges_configuration
                self.irods_conn.irods_env_file = self.context.irods_env_file
                self.irods_conn.irods_environment = self.context.irods_environment
                self.irods_conn.connect()
                
                if self.irods_conn.icommands.has_icommands:
                    in_var = input("Use icommands (Y/N, default Y): ").strip().lower()
                    if in_var in ['', 'y', 'yes']:
                        self.irods_conn.use_icommands = True
                        self.irods_conn.icommands.set_irods_env_file(self.context.irods_env_file)
                        
                assert self.irods_conn.session.has_valid_irods_session(), "No session"

                break
            except AssertionError as error:
                logging.error('Failed to connect: %r', error)
                attempts += 1
                if attempts >= 3 or input('Try again (Y/n): ').lower() == 'n':
                    return False
        return

    @plugin_hook
    def download(self):
        """
        Download dataobject or collection from iRods.
        """
        # status for ther benefit of the plugin
        self.download_finished = False

        # checks if remote object exists and if it's an object or a collection
        if self.irods_conn.collection_exists(self.irods_path):
            item = self.irods_conn.get_collection(self.irods_path)
        elif self.irods_conn.dataobject_exists(self.irods_path):
            item = self.irods_conn.get_dataobject(self.irods_path)
        else:
            logging.error('iRODS path %s does not exist', self.irods_path)
            return False

        # get its size to check if there's enough space
        download_size = self.irods_conn.get_irods_size([self.irods_path])
        logging.info("Downloading '%s' (approx. %sGB)", self.irods_path, round(download_size * kw.MULTIPLIER, 2))

        # download
        self.irods_conn.download_data(source=item, destination=self.local_path, size=download_size, force=False)

        self.download_finished = True

        logging.info('Download complete')
        return True

    @plugin_hook
    def upload(self):
        """
        Uploads local file(s) to iRods.
        """
        # status for ther benefit of the plugin
        self.upload_finished = False

        # check if intended upload target exists
        try:
            self.irods_conn.ensure_coll(self.target_path)
            logging.info('Uploading to %s', self.target_path)
        except (CollectionDoesNotExist, SYS_INVALID_INPUT_PARAM):
            logging.error('Collection path invalid: %s', self.target_path)
            return False

        # check if there's enough space left on the resource
        upload_size = utils.utils.get_local_size([self.local_path])

        free_space = int(self.irods_conn.get_free_space(resc_name=self.irods_resc))
        if free_space-1000**3 < upload_size and \
                not self.context.ibridges_configuration.config.get('force_transfers', False):
            logging.error('Not enough space left on iRODS resource to upload.')
            return False

        self.irods_conn.upload_data(
            source=self.local_path,
            destination=self.irods_conn.get_collection(self.target_path),
            res_name=self.irods_resc,
            size=upload_size,
            force=True)

        self.upload_finished = True

        return True

    def _run(self):
        self.connect_irods()

        if not self.irods_conn:
            self._clean_exit("Connection failed")

        if self.operation == 'download':

            if not self.download():
                self._clean_exit()

        elif self.operation == 'upload':

            # try:
            #     _ = self.irods_conn.resources.get(self.irods_resc)
            # except ResourceDoesNotExist:
            #     self._clean_exit(f"iRODS resource '{self.irods_resc}' not found")

            if self.irods_resc not in self.irods_conn.resources:
                self._clean_exit(f"iRODS resource '{self.irods_resc}' not found")

            self.target_path = self.irods_path

            if not self.upload():
                self._clean_exit()

        else:
            logging.error('Unknown operation: %s', self.operation)

        self._clean_exit(message="Done", exit_code=0)


if __name__ == "__main__":

    elab = ElabPlugin()

    cli = IBridgesCli.from_arguments(plugins=[
        {
            'hook': 'upload',
            'actions': [
                {'slot': 'pre', 'function': elab.setup},
                {'slot': 'post', 'function': elab.annotate}
            ]
        }
    ])
