""" Irods connection factory

"""
import irods.collection
import irods.data_object
import irods.resource
import irods.session

from . import dataOperations
from . import Icommands
from . import keywords as kw
from . import meta
from . import permission
from . import query
from . import resource
from . import rules
from . import session
from . import tickets
from . import users


class IrodsConnector:
    """Top-level connection to the Python iRODS client

    """
    _instance = None
    _data_op = None
    _icommands = None
    _meta = None
    _permission = None
    _query = None
    _resource = None
    _rules = None
    _session = None
    _tickets = None
    _users = None
    use_icommands = None

    def __new__(cls):
        """Give only a single new instance ever.

        Returns
        -------
        IrodsConnector
            A singleton instance.

        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, password=''):
        """Initialize connection to iRODS functionality based on the
        user's credentials.

        Parameters
        ----------
        password : str
            Plain text password.

        """
        self.__name__ = 'IrodsConnector'
        self._password = password

    def __del__(self):
        self.cleanup()
        del self.session

    # Properties for all the classes themselves
    #
    @property
    def data_op(self) -> dataOperations.DataOperation:
        if self._data_op is None:
            self._data_op = dataOperations.DataOperation(self.resource, self.session)
        return self._data_op

    @property
    def icommands(self) -> Icommands.IrodsConnectorIcommands:
        if self._icommands is None:
            self._icommands = Icommands.IrodsConnectorIcommands()
        return self._icommands

    @property
    def meta(self) -> meta.Meta:
        if self._meta is None:
            self._meta = meta.Meta()
        return self._meta

    @property
    def permission(self) -> permission.Permission:
        if self._permission is None:
            self._permission = permission.Permission(self.data_op, self.session)
        return self._permission

    @property
    def query(self) -> query.Query:
        if self._query is None:
            self._query = query.Query(self.session)
        return self._query

    @property
    def resource(self) -> resource.Resource:
        if self._resource is None:
            self._resource = resource.Resource(self.session)
        return self._resource

    @property
    def rules(self) -> rules.Rules:
        if self._rules is None:
            self._rules = rules.Rules(self.session)
        return self._rules

    @property
    def session(self) -> session.Session:
        if self._session is None:
            self._session = session.Session(self._password)
        return self._session

    @session.deleter
    def session(self):
        # TODO figure out why this is necessary!
        if self._session is not None:
            del self._session
            self._session = None

    @property
    def tickets(self) -> tickets.Tickets:
        if self._tickets is None:
            self._tickets = tickets.Tickets(self.session)
        return self._tickets

    @property
    def users(self) -> users.Users:
        if self._users is None:
            self._users = users.Users(self.session)
        return self._users

    # Data operation/iCommands functionality
    #
    def collection_exists(self, path: str) -> bool:
        return self.data_op.collection_exists(path)

    def dataobject_exists(self, path: str) -> bool:
        return self.data_op.dataobject_exists(path)

    def delete_data(self, item: None):
        return self.data_op.delete_data(item)

    def diff_obj_file(self, objpath: str, fspath: str, scope: str = "size") -> tuple:
        return self.data_op.diff_obj_file(objpath, fspath, scope)

    def diff_irods_localfs(self, coll: irods.collection.iRODSCollection,
                           dirpath: str, scope: str = "size") -> tuple:
        return self.data_op.diff_irods_localfs(coll, dirpath, scope)

    def download_data(self,
                      source: (irods.collection.iRODSCollection,
                               irods.data_object.iRODSDataObject),
                      destination: str, size: int, buff: int = kw.BUFF_SIZE,
                      force: bool = False, diffs: tuple = None):
        if self.use_icommands:
            return self.icommands.download_data(source, destination, size, buff, force)
        else:
            return self.data_op.download_data(source, destination, size, buff, force, diffs)

    def ensure_coll(self, coll_name: str) -> irods.collection.iRODSCollection:
        return self.data_op.ensure_coll(coll_name)

    def ensure_data_object(self, data_object_name: str) -> irods.data_object.iRODSDataObject:
        return self.data_op.ensure_data_object(data_object_name)

    def get_collection(self, path: str) -> irods.collection.iRODSCollection:
        return self.data_op.get_collection(path)

    def get_dataobject(self, path: str) -> irods.data_object.iRODSDataObject:
        return self.data_op.get_dataobject(path)

    def get_irods_size(self, path_names: list) -> int:
        return self.data_op.get_irods_size(path_names)

    def irods_put(self, local_path: str, irods_path: str, res_name: str = ''):
        return self.data_op.irods_put(local_path, irods_path, res_name)

    def irods_get(self, irods_path: str, local_path: str, options: dict = None):
        return self.data_op.irods_get(irods_path, local_path, options)

    def is_collection(self, obj) -> bool:
        return self.data_op.is_collection(obj)

    def is_dataobject(self, obj) -> bool:
        return self.data_op.is_dataobject(obj)

    def upload_data(self, source: str, destination: irods.collection.iRODSCollection,
                    res_name: str, size: int, buff: int = kw.BUFF_SIZE,
                    force: bool = False, diffs: tuple = None):
        if self.use_icommands:
            return self.icommands.upload_data(
                source, destination, res_name, size, buff, force)
        else:
            return self.data_op.upload_data(
                source, destination, res_name, size, buff, force, diffs)

    # Metadata functionality
    #
    def add_metadata(self, items: list, key: str, value: str, units: str = None):
        return self.meta.add(items, key, value, units)

    def add_multiple_metadata(self, items, avus):
        return self.meta.add_multiple(items, avus)

    def delete_metadata(self, items: list, key: str, value: str, units: str = None):
        return self.meta.delete(items, key, value, units)

    def update_metadata(self, items: list, key: str, value: str, units: str = None):
        return self.meta.update(items, key, value, units)

    # Permission functionality
    #
    @property
    def permissions(self) -> dict:
        return self.permission.permissions

    def get_permissions(self, path: str = '', obj: irods.collection = None) -> list:
        return self.permission.get_permissions(path, obj)

    def set_permissions(self, perm: str, path: str, user: str = '', zone: str = '',
                        recursive: bool = False, admin: bool = False):
        return self.permission.set_permissions(perm, path, user, zone, recursive, admin)

    # Query functionality
    #
    def search(self, key_vals: dict = None) -> list:
        return self.query.search(key_vals)

    # Resource functionality
    #
    @property
    def resources(self) -> dict:
        return self.resource.resources

    def get_free_space(self, resc_name: str, multiplier: int = 1) -> int:
        return self.resource.get_free_space(resc_name, multiplier)

    def get_resource(self, resc_name: str) -> irods.resource.iRODSResource:
        return self.resource.get_resource(resc_name)

    def get_resource_children(self, resc: irods.resource.iRODSResource) -> list:
        return self.resource.get_resource_children(resc)

    def list_resources(self, attr_names: list = None) -> tuple:
        return self.resource.list_resources(attr_names)

    def resource_space(self, resc_name: str) -> int:
        return self.resource.resource_space(resc_name)

    # Rules functionality
    #
    def execute_rule(self, rule_file: str, params: dict, output: str = 'ruleExecOut') -> tuple:
        return self.rules.execute_rule(rule_file, params, output)

    # Session functionality
    #
    def connect(self):
        """Manually establish an iRODS session.

        """
        if not self.session.has_irods_session():
            self.session.connect()

    def cleanup(self):
        if self.has_session() and self.session.has_irods_session():
            # In case the iRODS session is not fully there.
            try:
                self.session.irods_session.cleanup()
            except NameError:
                pass

    @staticmethod
    def get_cached_password() -> str:
        """Acquire the cached password from the iRODS auth file.

        Returns
        -------
        str
            Cached password or null string.

        """
        return session.get_cached_password()

    def has_session(self) -> bool:
        """Check if an iBridges session has been assigned to its shadow
        variable.

        Returns
        -------
        bool
            Has a session been set?

        """
        return self._session is not None

    def reset(self):
        del self.session

    @property
    def davrods(self) -> str:
        return self.session.davrods

    @property
    def default_resc(self) -> str:
        return self.session.default_resc

    @property
    def host(self) -> str:
        return self.session.host

    @property
    def password(self) -> str:
        """Password scraped from iRODS obfuscated auth file or manually
        set.

        Returns
        -------
        str
            Plain text password.

        """
        return self.session.password

    @password.setter
    def password(self, password: str):
        """Set the session password.

        This method is _vital_ for updating the session password _after_
        Session instantiation.

        Parameters
        ----------
        password : str
            Plain text password.

        """
        self.session.password = password
        # This is purely cosmetic.  This variable is used only once
        # when instantiating the Session (a.k.a. self.session).
        self._password = password

    @property
    def port(self) -> str:
        return self.session.port

    @property
    def server_version(self) -> tuple:
        return self.session.server_version

    @property
    def username(self) -> str:
        return self.session.username

    @property
    def zone(self) -> str:
        return self.session.zone

    # Tickets functionality
    #
    def create_ticket(self, obj_path: str, expiry_string: str = '') -> tuple:
        return self.tickets.create_ticket(obj_path, expiry_string)

    # Users functionality
    #
    def get_user_info(self) -> tuple:
        return self.users.get_user_info()
