from irods.session import iRODSSession
from irods.access import iRODSAccess
from irods.ticket import Ticket
from irods.exception import CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME, \
                            CAT_NO_ACCESS_PERMISSION, CAT_SUCCESS_BUT_WITH_NO_INFO, \
                            CAT_INVALID_ARGUMENT, CAT_INVALID_USER, CAT_INVALID_AUTHENTICATION

from irods.exception import CollectionDoesNotExist
from irods.connection import PlainTextPAMPasswordError
from irods.models import Collection, DataObject, Resource, CollectionMeta, DataObjectMeta
from irods.models import User, UserGroup
from irods.column import Like
import irods.keywords as kw
from irods.rule import Rule

import json
import os
from base64 import b64decode
from shutil import disk_usage
import hashlib
import ssl
import random
import string
import logging

RED = '\x1b[1;31m'
DEFAULT = '\x1b[0m'
YEL = '\x1b[1;33m'
BLUE = '\x1b[1;34m'


class irodsConnector():
    def __init__(self, envFile, password=""):
        """
        iRODS authentication with python.
        Input:
            envFile: json document with iRODS connection parameters
            password: string

        If you like to overwrite one or both parameters, use the envFile and password.

        Throws errors:
            irods.exception.CAT_INVALID_USER: password no longer properly cached
            irods.exception.PAM_AUTH_PASSWORD_FAILED: wrong password
            NetworkException: No connection could be established
            All other errors refer to having the envFile not setup properly
        """
        self.__name__ = "irodsConnector"

        try:
            with open(envFile) as f:
                ienv = json.load(f)
            if password == "": 
                # requires a valid .irods/.irodsA (linux/mac only)
                # self.session = iRODSSession(irods_env_file=envFile)
                raise CAT_INVALID_AUTHENTICATION("No password provided.")

            else:
                self.session = iRODSSession(**ienv, password=password)
                testcoll = self.session.collections.get(
                        "/"+self.session.zone+"/home")
        except PlainTextPAMPasswordError:
            try:
                ssl_context = ssl.create_default_context(
                    purpose=ssl.Purpose.SERVER_AUTH, cafile=None, capath=None, cadata=None)
                ssl_settings = {'client_server_negotiation': 'request_server_negotiation',
                            'client_server_policy': 'CS_NEG_REQUIRE',
                            'encryption_algorithm': 'AES-256-CBC',
                            'encryption_key_size': 32,
                            'encryption_num_hash_rounds': 16,
                            'encryption_salt_size': 8,
                            'ssl_context': ssl_context}
                self.session = iRODSSession(
                                **ienv, password=password, **ssl_settings)
            except:
                raise

        except CollectionDoesNotExist:
            pass
        except Exception as error:
            logging.info('AUTHENTICATION ERROR', exc_info=True)
            print(RED+"AUTHENTICATION ERROR: "+repr(error)+DEFAULT)
            raise

        try:
            colls = self.session.collections.get(
                    "/"+self.session.zone+"/home").subcollections
        except CollectionDoesNotExist:
            colls = self.session.collections.get(
                    "/"+self.session.zone+"/home/"+self.session.username).subcollections
        except:
            logging.info('AUTHENTICATION ERROR', exc_info=True)
            print(RED+"IRODS ERROR LOADING COLLECTION HOME/USER: "+DEFAULT)
            print(RED+"Collection does not exist or user auth failed."+DEFAULT)
            raise
        
        collnames = [c.path for c in colls]

        if "default_resource_name" in ienv:
            self.defaultResc = ienv["default_resource_name"]
        else:
            self.defaultResc = "demoResc"

        if "davrods_server" in ienv:
            self.davrods = ienv["davrods_server"].strip('/')
        else:
            self.davrods = None

        print("Welcome to iRODS:")
        print("iRODS Zone: "+self.session.zone)
        print("You are: "+self.session.username)
        print("Default resource: "+self.defaultResc)
        print("You have access to: \n")
        print('\n'.join(collnames))

        logging.info(
            'IRODS LOGIN SUCCESS: '+self.session.username+", "+self.session.zone+", "+self.session.host)

    def getUserInfo(self):
        userGroupQuery = self.session.query(UserGroup).filter(Like(User.name, self.session.username))
        userTypeQuery = self.session.query(User.type).filter(Like(User.name, self.session.username))
        
        userType = []
        for t in userTypeQuery.get_results():
            userType.extend(list(t.values()))
        userGroups = []
        for g in userGroupQuery.get_results():
            userGroups.extend(list(g.values()))

        return(userType, userGroups)

    def getPermissions(self, iPath):
        """
        iPath: Can be a string or an iRODS collection/object
        Throws:
            irods.exception.CollectionDoesNotExist
        """
        try:
            return self.session.permissions.get(iPath)
        except:
            try:
                coll = self.session.collections.get(iPath)
                return self.session.permissions.get(coll)
            except:
                try:
                    obj = self.session.data_objects.get(iPath)
                    return self.session.permissions.get(obj)
                except:
                    logging.info('GET PERMISSIONS', exc_info=True)
                    raise

    def setPermissions(self, rights, user, path, zone, recursive=False):
        """
        Sets permissions to an iRODS collection or data object.
        path: string
        rights: string, [own, read, write, null]
        """
        acl = iRODSAccess(rights, path, user, zone)

        try:
            if recursive and self.session.collections.exists(path):
                self.session.permissions.set(acl, recursive=True)
            else:
                self.session.permissions.set(acl, recursive=False)
        except CAT_INVALID_USER:
            raise CAT_INVALID_USER("ACL ERROR: user unknown ")
        except CAT_INVALID_ARGUMENT:
            print(RED+"ACL ERROR: rights or path not known "+path+DEFAULT)
            logging.info('ACL ERROR: rights or path not known', exc_info=True)
            raise

    def ensureColl(self, collPath):
        """
        Raises:
            irods.exception.CAT_NO_ACCESS_PERMISSION
        """
        try:
            self.session.collections.create(collPath)
            return self.session.collections.get(collPath)
        except:
            logging.info('ENSURE COLLECTION', exc_info=True)
            raise

    def search(self, keyVals=None):
        """
        Given a dictionary with keys and values, searches for colletions and
        data objects that fullfill the criteria.
        The key 'checksum' will be mapped to DataObject.checksum, the key 'path'
        will be mapped to Collection.name and the key 'object' will be mapped to DataObject.name.
        Default: if no keyVals are given, all accessible colletcins and data objects will be returned

        keyVals: dict; {'checksum': '', 'key1': 'val1', 'key2': 'val2', 'path': '', 'object': ''}

        Returns:
        list: [[Collection name, Object name, checksum]]
        """
        collQuery = None
        # data query
        if 'checksum' in keyVals or 'object' in keyVals:
            objQuery = self.session.query(Collection.name, DataObject.name, DataObject.checksum)
            if 'object' in keyVals:
                if keyVals['object']:
                    objQuery = objQuery.filter(Like(DataObject.name, keyVals['object']))
            if 'checksum' in keyVals:
                if keyVals['checksum']:
                    objQuery = objQuery.filter(Like(DataObject.checksum, keyVals['checksum']))
        else:
            collQuery = self.session.query(Collection.name)
            objQuery = self.session.query(Collection.name, DataObject.name, DataObject.checksum)

        if 'path' in keyVals and keyVals['path']: 
            if collQuery:
                collQuery = collQuery.filter(Like(Collection.name, keyVals['path']))
            objQuery = objQuery.filter(Like(Collection.name, keyVals['path']))
        
        for key in keyVals:
            if key not in ['checksum', 'path', 'object']:
                if objQuery:
                    objQuery.filter(DataObjectMeta.name == key)
                if collQuery:
                    collQuery.filter(CollectionMeta.name == key)
                if keyVals[key]:
                    if objQuery:
                        objQuery.filter(DataObjectMeta.value == keyVals[key])
                    if collQuery:
                        collQuery.filter(CollectionMeta.value == keyVals[key])

        results = [['', '', ''], ['', '', ''], ['', '', '']]
        collBatch = [[]]
        objBatch = [[]]
        # return only 100 results
        if collQuery:
            results[0] = ["Collections found: "+str(sum(1 for _ in collQuery)), '', '']
            collBatch = [b for b in collQuery.get_batches()]
        if objQuery:
            results[1] = ["Objects found: "+str(sum(1 for _ in objQuery)), '', '']
            objBatch = [b for b in objQuery.get_batches()]
       
        for res in collBatch[0][:50]:
            results.append([res[list(res.keys())[0]], '', ''])
        for res in objBatch[0][:50]:
            results.append([res[list(res.keys())[0]],
                            res[list(res.keys())[1]],
                            res[list(res.keys())[2]]])
        return results

    def listResources(self):
        """
        Returns list of all root resources, that accept data.
        """
        query = self.session.query(Resource.name, Resource.parent)
        resources = []
        for item in query.get_results():
            rescName, parent = item.values()
            if parent is None:
                resources.append(rescName)

        if 'bundleResc' in resources:
            resources.remove('bundleResc')
        if 'demoResc' in resources:
            resources.remove('demoResc')

        return resources

    def getResource(self, resource):
        """
        Raises:
            irods.exception.ResourceDoesNotExist
        """
        return self.session.resources.get(resource)

    def resourceSize(self, resource):
        """
        Returns the available space left on a resource in bytes
        resource: Name of the resource
        Throws: ResourceDoesNotExist if resource not known
                AttributeError if 'free_space' not set
        """
        try:
            size = self.session.resources.get(resource).free_space
            return size
        except Exception as error:
            logging.info('RESOURCE ERROR: Either resource does not exist or size not set.',
                         exc_info=True)
            raise error("RESOURCE ERROR: Either resource does not exist or size not set.")

    def uploadData(self, source, destination, resource, size, buff=1024**3,
                   force=False, diffs=[]):
        """
        source: absolute path to file or folder
        destination: iRODS collection where data is uploaded to
        resource: name of the iRODS storage resource to use
        size: size of data to be uploaded in bytes
        buff: buffer on resource that should be left over
        force: If true, do not calculate storage capacity on destination
        diffs: output of diff functions

        The function uploads the contents of a folder with all subfolders to 
        an iRODS collection.
        If source is the path to a file, the file will be uploaded.

        Throws:
        ResourceDoesNotExist
        ValueError (if resource too small or buffer is too small)
        
        """
        logging.info('iRODS UPLOAD: ['+source+']-->['+str(destination)+'], ['+str(resource)+']')
        if resource is not None and resource != "":
            options = {kw.RESC_NAME_KW: resource,
                       kw.REG_CHKSUM_KW: '', kw.ALL_KW: '',
                       kw.VERIFY_CHKSUM_KW: ''}
        else:
            options = {kw.REG_CHKSUM_KW: '', kw.ALL_KW: '', 
                       kw.VERIFY_CHKSUM_KW: ''}

        if not diffs:
            if os.path.isfile(source):
                (diff, onlyFS, onlyIrods, same) = self.diffObjFile(
                                                  destination.path+'/'+os.path.basename(source), 
                                                  source, scope="checksum")
            elif os.path.isdir(source):
                subcoll = self.session.collections.create(
                          destination.path+'/'+os.path.basename(source))
                (diff, onlyFS, onlyIrods, same) = self.diffIrodsLocalfs(subcoll, source)
            else:
                raise FileNotFoundError("ERROR iRODS upload: not a valid source path")
        else:
            (diff, onlyFS, onlyIrods, same) = diffs

        if not force:
            try:
                space = self.session.resources.get(resource).free_space
                if not space:
                    logging.info(
                        'ERROR iRODS upload: No size set on iRODS resource. Refuse to upload.', 
                        exc_info=True)
                    raise ValueError(
                        'ERROR iRODS upload: No size set on iRODS resource. Refuse to upload.')
                if int(size) > (int(space)-buff):
                    logging.info('ERROR iRODS upload: Not enough space on resource.', 
                                 exc_info=True)
                    raise ValueError('ERROR iRODS upload: Not enough space on resource.')
                if buff < 0:
                    logging.info('ERROR iRODS upload: Negative resource buffer.', 
                        exc_info=True)
                    raise BufferError('ERROR iRODS upload: Negative resource buffer.')
            except Exception as error:
                logging.info('UPLOAD ERROR', exc_info=True)
                raise error

        if os.path.isfile(source) and len(diff+onlyFS) > 0:
            try:
                print("IRODS UPLOADING FILE", destination.path+"/"+os.path.basename(source))
                self.session.data_objects.put(
                        source, destination.path+"/"+os.path.basename(source), 
                        num_threads=4, **options)
                return
            except IsADirectoryError:
                logging.info('IRODS UPLOAD ERROR: There exists a collection of same name as '+source, 
                    exc_info=True)
                print("IRODS UPLOAD ERROR: There exists a collection of same name as "+source)
                raise
            
        try:  # collections/folders
            logging.info("IRODS UPLOAD started:")
            for d in diff:
                # upload files to distinct data objects
                destColl = self.session.collections.create(os.path.dirname(d[0]))
                logging.info("REPLACE: "+d[0]+" with "+d[1])
                self.session.data_objects.put(d[1], d[0], num_threads=4, **options)

            for o in onlyFS:  # can contain files and folders
                # Create subcollections and upload
                sourcePath = os.path.join(source, o)
                if len(o.split(os.sep)) > 1:
                    subColl = self.session.collections.create(
                                destination.path+'/'+os.path.basename(source)+'/'+os.path.dirname(o))
                else:
                    subColl = self.session.collections.create(
                            destination.path+'/'+os.path.basename(source))
                logging.info("UPLOAD: "+sourcePath+" to "+subColl.path)
                logging.info("CREATE "+subColl.path+"/"+os.path.basename(sourcePath))
                self.session.data_objects.put(
                    sourcePath, subColl.path+"/"+os.path.basename(sourcePath), 
                    num_threads=0, **options)
        except:
            logging.info('UPLOAD ERROR', exc_info=True)
            raise

    def downloadData(self, source, destination, size, buff=1024**3, force=False, diffs=[]):
        """
        Download object or collection.
        source: iRODS collection or data object
        destination: absolute path to download folder
        size: size of data to be downloaded in bytes
        buff: buffer on resource that should be left over
        force: If true, do not calculate storage capacity on destination
        diffs: output of diff functions
        """
        logging.info('iRODS DOWNLOAD: '+str(source)+'-->'+destination) 
        options = {kw.FORCE_FLAG_KW: '', kw.REG_CHKSUM_KW: ''}

        if destination.endswith(os.sep):
            destination = destination[:len(destination)-1]
        if not os.path.isdir(destination):
            logging.info('DOWNLOAD ERROR: destination path does not exist or is not directory', 
                    exc_info=True)
            raise FileNotFoundError(
                "ERROR iRODS download: destination path does not exist or is not directory")
        if not os.access(destination, os.W_OK):
            logging.info('DOWNLOAD ERROR: No rights to write to destination.', 
                exc_info=True)
            raise PermissionError("ERROR iRODS download: No rights to write to destination.")

        if not diffs:  # Only download if not present or difference in files
            if self.session.data_objects.exists(source.path):
                (diff, onlyFS, onlyIrods, same) = self.diffObjFile(source.path,
                                                    os.path.join(
                                                        destination, os.path.basename(source.path)),
                                                    scope="checksum")
            elif self.session.collections.exists(source.path):
                subdir = os.path.join(destination, source.name)
                if not os.path.isdir(os.path.join(destination, source.name)):
                    os.mkdir(os.path.join(destination, source.name))

                (diff, onlyFS, onlyIrods, same) = self.diffIrodsLocalfs(
                                                    source, subdir, scope="checksum")
            else:
                raise FileNotFoundError("ERROR iRODS download: not a valid source path")
        else:
            (diff, onlyFS, onlyIrods, same) = diffs

        if not force:  # Check space on destination
            try:
                space = disk_usage(destination).free
                if int(size) > (int(space)-buff):
                    logging.info('DOWNLOAD ERROR: Not enough space on disk.', 
                            exc_info=True)
                    raise ValueError('ERROR iRODS download: Not enough space on disk.')
                if buff < 0:
                    logging.info('DOWNLOAD ERROR: Negative disk buffer.', exc_info=True)
                    raise BufferError('ERROR iRODS download: Negative disk buffer.')
            except Exception as error:
                logging.info('DOWNLOAD ERROR', exc_info=True)
                raise error

        if self.session.data_objects.exists(source.path) and len(diff+onlyIrods) > 0:
            try:
                logging.info("IRODS DOWNLOADING object:" + source.path +
                             " to " + destination)
                self.session.data_objects.get(source.path, 
                            local_path=os.path.join(destination, source.name), **options)
                return
            except:
                logging.info('DOWNLOAD ERROR: '+source.path+"-->"+destination, 
                        exc_info=True)
                raise

        try:  # collections/folders
            subdir = os.path.join(destination, source.name)
            logging.info("IRODS DOWNLOAD started:")
            for d in diff:
                # upload files to distinct data objects
                logging.info("REPLACE: "+d[1]+" with "+d[0])
                self.session.data_objects.get(d[0], local_path=d[1], **options)

            for IO in onlyIrods:  # can contain files and folders
                # Create subcollections and upload
                sourcePath = source.path + "/" + IO
                locO = IO.replace("/", os.sep)
                destPath = os.path.join(subdir, locO)
                if not os.path.isdir(os.path.dirname(destPath)):
                    os.makedirs(os.path.dirname(destPath))
                logging.info('INFO: Downloading '+sourcePath+" to "+destPath)
                self.session.data_objects.get(sourcePath, local_path=destPath, **options)
        except:
            logging.info('DOWNLOAD ERROR', exc_info=True)
            raise

    def diffObjFile(self, objPath, fsPath, scope="size"):
        """
        Compares and iRODS object to a file system file.
        returns ([diff], [onlyIrods], [onlyFs], [same])
        """
        if os.path.isdir(fsPath) and not os.path.isfile(fsPath):
            raise IsADirectoryError("IRODS FS DIFF: file is a directory.")
        if self.session.collections.exists(objPath):
            raise IsADirectoryError("IRODS FS DIFF: object exists already as collection. "+objPath)

        if not os.path.isfile(fsPath) and self.session.data_objects.exists(objPath):
            return ([], [], [objPath], [])

        elif not self.session.data_objects.exists(objPath) and os.path.isfile(fsPath):
            return ([], [fsPath], [], [])

        # both, file and object exist
        obj = self.session.data_objects.get(objPath)
        if scope == "size":
            objSize = obj.size
            fSize = os.path.getsize(fsPath)
            if objSize != fSize:
                return ([(objPath, fsPath)], [], [], [])
            else:
                return ([], [], [], [(objPath, fsPath)])
        elif scope == "checksum":
            objCheck = obj.checksum
            if objCheck is None:
                try:
                    obj.chksum()
                    objCheck = obj.checksum
                except:
                    logging.info('No checksum for '+obj.path)
                    return([(objPath, fsPath)], [], [], [])
            if objCheck.startswith("sha2"):
                sha2Obj = b64decode(objCheck.split('sha2:')[1])
                with open(fsPath, "rb") as f:
                    stream = f.read()
                    sha2 = hashlib.sha256(stream).digest()
                print(sha2Obj != sha2)
                if sha2Obj != sha2:
                    return([(objPath, fsPath)], [], [], [])
                else:
                    return ([], [], [], [(objPath, fsPath)])
            elif objCheck:
                # md5
                with open(fsPath, "rb") as f:
                    stream = f.read()
                    md5 = hashlib.md5(stream).hexdigest()
                if objCheck != md5:
                    return([(objPath, fsPath)], [], [], [])
                else:
                    return ([], [], [], [(objPath, fsPath)])

    def diffIrodsLocalfs(self, coll, dirPath, scope="size"):
        """
        Compares and iRODS tree to a directory and lists files that are not in sync.
        Syncing scope can be 'size' or 'checksum'
        Returns: zip([dataObjects][files]) where there is a difference
        collection: iRODS collection
        """

        listDir = []
        if dirPath is not None:
            if not os.access(dirPath, os.R_OK):
                raise PermissionError("IRODS FS DIFF: No rights to write to destination.")
            if not os.path.isdir(dirPath):
                raise IsADirectoryError("IRODS FS DIFF: directory is a file.")
            for root, dirs, files in os.walk(dirPath, topdown=False):
                for name in files:
                    listDir.append(os.path.join(root.split(dirPath)[1], name).strip(os.sep))

        listColl = []
        if coll is not None:
            for root, subcolls, obj in coll.walk():
                for o in obj:
                    listColl.append(os.path.join(root.path.split(coll.path)[1], o.name).strip('/'))

        diff = []
        same = []
        for locPartialPath in set(listDir).intersection(listColl):
            iPartialPath = locPartialPath.replace(os.sep, "/")
            if scope == "size":
                objSize = self.session.data_objects.get(coll.path + '/' + iPartialPath).size
                fSize = os.path.getsize(os.path.join(dirPath, iPartialPath))
                if objSize != fSize:
                    diff.append((coll.path + '/' + iPartialPath, os.path.join(dirPath, locPartialPath)))
                else:
                    same.append((coll.path + '/' + iPartialPath, os.path.join(dirPath, locPartialPath)))
            elif scope == "checksum":
                objCheck = self.session.data_objects.get(coll.path + '/' + iPartialPath).checksum
                if objCheck is None:
                    try:
                        self.session.data_objects.get(coll.path + '/' + iPartialPath).chksum()
                        objCheck = self.session.data_objects.get(
                                    coll.path + '/' + iPartialPath).checksum
                    except:
                        logging.info('No checksum for '+coll.path + '/' + iPartialPath)
                        diff.append((coll.path + '/' + iPartialPath, 
                                     os.path.join(dirPath, locPartialPath)))
                        continue
                if objCheck.startswith("sha2"):
                    sha2Obj = b64decode(objCheck.split('sha2:')[1])
                    with open(os.path.join(dirPath, locPartialPath), "rb") as f:
                        stream = f.read()
                        sha2 = hashlib.sha256(stream).digest()
                    if sha2Obj != sha2:
                        diff.append((coll.path + '/' + iPartialPath, os.path.join(dirPath, locPartialPath)))
                    else:
                        same.append((coll.path + '/' + iPartialPath, os.path.join(dirPath, locPartialPath)))
                elif objCheck:
                    # md5
                    with open(os.path.join(dirPath, locPartialPath), "rb") as f:
                        stream = f.read()
                        md5 = hashlib.md5(stream).hexdigest()
                    if objCheck != md5:
                        diff.append((coll.path + '/' + iPartialPath, os.path.join(dirPath, locPartialPath)))
                    else:
                        same.append((coll.path + '/' + iPartialPath, os.path.join(dirPath, locPartialPath)))
            else:  # same paths, no scope
                diff.append((coll.path + '/' + iPartialPath, os.path.join(dirPath, locPartialPath)))

        # adding files that are not on iRODS, only present on local FS
        # adding files that are not on local FS, only present in iRODS
        # adding files that are stored on both devices with the same checksum/size
        irodsOnly = list(set(listColl).difference(listDir))
        for i in range(0, len(irodsOnly)):
            irodsOnly[i] = irodsOnly[i].replace(os.sep, "/")
        return (diff, list(set(listDir).difference(listColl)), irodsOnly, same)

    def addMetadata(self, items, key, value, units=None):
        """
        Adds metadata to all items
        items: list of iRODS data objects or iRODS collections
        key: string
        value: string
        units: (optional) string 

        Throws:
            CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME
        """
        for item in items:
            try:
                item.metadata.add(key, value, units)
            except CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME:
                print(RED+"INFO ADD META: Metadata already present"+DEFAULT)
            except CAT_NO_ACCESS_PERMISSION:
                raise CAT_NO_ACCESS_PERMISSION("ERROR UPDATE META: no permissions")

    def updateMetadata(self, items, key, value, units=None):
        """
        Updates a metadata entry to all items
        items: list of iRODS data objects or iRODS collections
        key: string
        value: string
        units: (optional) string

        Throws: CAT_NO_ACCESS_PERMISSION
        """
        try:
            for item in items:
                if key in item.metadata.keys():
                    meta = item.metadata.get_all(key)
                    valuesUnits = [(m.value, m.units) for m in meta]
                    if (value, units) not in valuesUnits:
                        # remove all iCAT entries with that key
                        for m in meta:
                            item.metadata.remove(m)
                        # add key, value, units
                        self.addMetadata(items, key, value, units)

                else:
                    self.addMetadata(items, key, value, units)
        except CAT_NO_ACCESS_PERMISSION:
            raise CAT_NO_ACCESS_PERMISSION("ERROR UPDATE META: no permissions "+item.path)

    def deleteMetadata(self, items, key, value, units):
        """
        Deletes a metadata entry of all items
        items: list of iRODS data objects or iRODS collections
        key: string
        value: string
        units: (optional) string

        Throws:
            CAT_SUCCESS_BUT_WITH_NO_INFO: metadata did not exist
        """
        for item in items:
            try:
                item.metadata.remove(key, value, units)
            except CAT_SUCCESS_BUT_WITH_NO_INFO:
                print(RED+"INFO DELETE META: Metadata never existed"+DEFAULT)
            except CAT_NO_ACCESS_PERMISSION:
                raise CAT_NO_ACCESS_PERMISSION("ERROR UPDATE META: no permissions "+item.path)

    def deleteData(self, item):
        """
        Delete a data object or a collection recursively.
        item: iRODS data object or collection
        """

        if self.session.collections.exists(item.path):
            logging.info("IRODS DELETE: "+item.path)
            try:
                item.remove(recurse=True, force=True)
            except CAT_NO_ACCESS_PERMISSION:
                raise CAT_NO_ACCESS_PERMISSION("ERROR IRODS DELETE: no permissions")
        elif self.session.data_objects.exists(item.path):
            logging.info("IRODS DELETE: "+item.path)
            try:
                item.unlink(force=True)
            except CAT_NO_ACCESS_PERMISSION:
                raise CAT_NO_ACCESS_PERMISSION("ERROR IRODS DELETE: no permissions " + item.path)

    def executeRule(self, ruleFile, params, output='ruleExecOut'):
        """
        Executes and interactive rule. Returns stdout and stderr.
        params: Depending on rule,
                dictionary of variables for rule, will overwrite the default settings.
        params format example:
        params = {  # extra quotes for string literals
            '*obj': '"/zone/home/user"',
            '*name': '"attr_name"',
            '*value': '"attr_value"'
        }
        """
        try:
            rule = Rule(self.session, ruleFile, params=params, output=output)
            out = rule.execute()
        except Exception as e:
            logging.info('RULE EXECUTION ERROR', exc_info=True)
            return [], [repr(e)]

        stdout = []
        stderr = []
        if len(out.MsParam_PI) > 0:
            try:
                stdout = [o.decode() 
                    for o in (out.MsParam_PI[0].inOutStruct.stdoutBuf.buf.strip(b'\x00')).split(b'\n')]
                stderr = [o.decode() 
                    for o in (out.MsParam_PI[0].inOutStruct.stderrBuf.buf.strip(b'\x00')).split(b'\n')]
            except AttributeError:
                logging.info('RULE EXECUTION ERROR: '+str(stdout+stderr), exc_info=True)
                return stdout, stderr
        
        return stdout, stderr

    def getSize(self, itemPaths):
        """
        Compute the size of the iRods dataobject or collection
        Returns: size in bytes.
        itemPaths: list of irods paths pointing to collection or object
        """
        size = 0
        for path in itemPaths:
            # remove possible leftovers of windows fs separators
            path = path.replace("\\", "/")
            if self.session.data_objects.exists(path):
                size = size + self.session.data_objects.get(path).size

            elif self.session.collections.exists(path):
                coll = self.session.collections.get(path)
                walk = [coll]
                while walk:
                    try:
                        coll = walk.pop()
                        walk.extend(coll.subcollections)
                        for obj in coll.data_objects:
                            size = size + obj.size
                    except:
                        logging.info('DATA SIZE', exc_info=True)
                        raise
        return size

    def createTicket(self, path, expiryString=""):
        ticket = Ticket(self.session, 
                        ''.join(random.choice(string.ascii_letters) for _ in range(20)))
        ticket.issue("read", path)
        logging.info('CREATE TICKET: '+ticket.ticket+': '+path)
        # returns False when no expiry date is set
        return ticket.ticket, False
