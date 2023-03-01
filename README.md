# iBridges

## Authors

Tim van Daalen, Christine Staiger

Wageningen University & Research 2021

## Contributors

J.P. Mc Farland

University of Groningen, Center for Information Technology, 2022

## Synopsis

The git repository contains a generic *iRODS* graphical user interface and the corresponding command-line interface clients.  The GUI and CLI work with any *iRODS* instance.  However, for user and data security we depend on some *iRODS* event hooks that need to be installed on the *iRODS* server.  Please refer to the documentation below.

## Dependencies

### iRODS server

To protect the *iRODS* resources from overflowing you should install an event hook on the *iRODS* servers that fill the resources' `RESC_FREE_SPACE` attribute in the iCAT.  These can be either *catalog* or *resource* servers.  Please add the following to the `/etc/irods/core.re` or another rule engine file:

```py
######################################################
# Storage capacity policies.
# Update the metadata field free_space of the resource
# when data is moved there or deleted from it.
#
# Author: Christine Staiger (2021)
#######################################################

acPostProcForParallelTransferReceived(*leaf_resource) {
    msiWriteRodsLog("LOGGING: acPostProcForParallelTransferReceived", *Status);
    msi_update_unixfilesystem_resource_free_space(*leaf_resource);
}

acPostProcForDataCopyReceived(*leaf_resource) {
    msiWriteRodsLog("LOGGING: acPostProcForDataCopyReceived", *Status);
    msi_update_unixfilesystem_resource_free_space(*leaf_resource);
}

# for iput
acPostProcForPut {
    msi_update_unixfilesystem_resource_free_space($KVPairs.rescName);
}

# for storage update after irmtrash
acPostProcForDelete {
    msi_update_unixfilesystem_resource_free_space($KVPairs.rescName);
}
```

For very busy systems, updating this value for every upload or delete can be prevented by commenting out or removing the last two stanzas if performance is being hampered.

For more complex resource hierarchies, the top of the resource tree (the _root_ node) will usually not be updated with the free space values, but if it is (the sum of all _leaf_ nodes is asssumed), the value in any _leaf_ nodes will be ignored.  If the _root_ node has no free space value, the sum of the _leaf_ nodes will be used instead.  If none of the resource nodes are annotated, an error will occur.  This feature can be overridden by annotating the _root_ node's free space value with an arbitrarily large value.  _*Please note, that this action disables the built-in protection offered by this client.*_

### Python

- Python 3 (>= 3.6)
  - Tested on versions up to 3.10 on multiple platforms
- pip-22.2.2
- Python packages (see install via `requirements.txt` below)
  - elabjournal==0.0.19
  - PyQt6==6.4.2
  - python-irodsclient==1.1.6
  - Pillow==9.4.0
  - pyinstaller==5.8.0
  - setproctitle==1.3.2
  - watchdog==2.2.1

Install dependencies with, for example:

```sh
python3.10 -m pip install -r requirements.txt
```

### Install Python 3.10
- Ubuntu:

  ```sh
  sudo apt update && sudo apt upgrade -y
  sudo apt install software-properties-common -y
  sudo add-apt-repository ppa:deadsnakes/ppa
  sudo apt install python3.10
  curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
  python3.10 -m pip install --upgrade pip
  sudo apt install python3.10-distutils
  python3.10 -m pip install pyqt6
  ```

- Mac (homebrew):
  ```sh
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  brew update
  brew install python@3.10
  /opt/homebrew/opt/python@3.10/libexec/bin/python -m pip install --upgrade pip
  /opt/homebrew/opt/python@3.10/libexec/bin/pip install pyqt6
  ```
### Operating system

The client works on Mac, Windows and Linux distributions.  On Mac and Windows it makes use solely of the *iRODS* Python API.  On Linux, we implemented a switch: if the *iRODS* icommands are installed, you can choose at the login page to up and download data through the icommand `irsync`. This is recommended for large data transfers.

- Install the *iBridges* GUI on a Linux (sub)system
- [Install the icommands](https://git.wur.nl/rdm-infrastructure/irods-training/-/blob/master/04-Training-Setup.md#icommands). 
- Start the *iBridges* GUI in the mode (icommands) on the Login screen.
<img src="gui/icons/irods-basicGUI_Login.png" width="500">

## Configuration

### iRODS environment.json

- Please create a directory/folder named `.irods` in your home directory/folder (`~/.irods/` in Linux shorthand).
  - Linux: `/home/\<username\>/.irods/irods_environment.json`
  - Mac: `/Users/\<username\>/.irods/irods_environment.json`
  - Windows: `C:\\\\....\\\<username\>\\.irods\\irods_environment.json`

- Your *iRODS* admin will provide an `irods_environment.json` file, its contents, or instructions on how to create it.  Place that file into the `.irods` directory/folder.  Here it an example that can be created with the `iinit` iCommand on Linux:

```json
{
    "irods_host": "server.fqdn.nl", 
    "irods_port": 1247, 
    "irods_user_name": "username", 
    "irods_zone_name": "myZone", 
    "irods_default_resource": "myResc" 
}
```

### iBridges config.json

*iBridges* will create its own configuration file in `~/.ibridges/` containing the name of the last *iRODS* environment file used.  This `config.json` file can be updated to control other aspects of *iBridges*.  For example:

```json
{
    "last_ienv": "irods_environment.json", 
    "davrods_server": "https://server.fqdn.nl", 
    "ui_tabs": [ 
        "tabUpDownload", 
        "tabELNData", 
        "tabDataBundle", 
        "tabCreateTicket" 
    ], 
    "force_unknown_free_space": false 
}
```
Options:
- `davrods_server`: for annotation of eLabJournal data
- `ui_tabs`: configure which tabs are shown (Browser and Info tabs always are)
  - `tabUpDownload`: a two-pane upload/download tab
  - `tabELNData`: for the Electronic Lab Notebook, eLabJournal
  - `tabDataBundle`: (un)bundle datasets from/to four supported formats
  - `tabCreateTicket`: create iRODS tickets for anonymous access
- `force_unknown_free_space`: ignore if resources' free space is unannotated

The `force_unknown_free_space` option is *REQUIRED* to be set to `true` if your default resource does not yet have its free space annotated.  It makes unannotated top-level resources visible in the drop-downs allowing selection of them.  In addition, it sets the `force` flag for uploads overriding resource overflow protection.

The logs for both GUI and CLI clients can be found in the `~/.ibridges/` directory/folder.

## Usage

```bash
export PYTHON_IRODSCLIENT_DEFAULT_XML=QUASI_XML
./irods-iBridgesGui.py
```

## Remarks

### Data (un)bundling

iRODS 4.2.x currently has no support for compressed structured files outside the iCommand `ibun`.  Therefore, without custom microservices installed on a given iRODS server, only uncompressed TAR files are supported.

#### TAR file format

The `ibun` help gives the example to use the `-C` option to change into the directory containing the potential contents of the TAR file.  The bundling done with iBridges assumes this same format and creates TAR files likewise.  For example bundling the contents of the collection `/testZone/home/user/testColl` containing:

```commandline
/testZone/home/user/testColl/file1.ext
/testZone/home/user/testColl/file2.ext
/testZone/home/user/testColl/file3.ext
```

stores only the three data objects:

```commandline
file1.ext
file2.ext
file3.ext
```

into `/testZone/home/user/testColl.tar`.  Unbundling this data object recreates the `/testZone/home/user/testColl` collection if it does not exist and deposits the data objects into it.  If there are already data objects or collections existing there, an error will result and the bundle will not be extracted.

#### (Un)bundle options

iBridges has one option for (un)bundling data: `Force operations`.  If the option is checked, two types of operations will be forced: one is to overwrite a bundle/collection that already exists, and the other is to remove the bundle files or collection contents without first sending them to the bin.  **If this behavior is undesirable, DO NOT USE THIS FORCE OPTION.**

It is recommended that any kind of destructive actions be done in a separate step.

### Performance

- When the client is started for the first time it, might take some time to launch.
- Tested on
  - 4/2cores, 8/4GB memory: Quick performance.  GUI reacts very quickly.  Data transfers with default python API perform okay.  For large data we recommend to move to a linux system, install the icommands and use the GUI with icommands settings upon login.

- Upload performances
  - icommands: Upload speed is mainly impacted by network speed
  - default: Upload performance is depending on network speed and performance of the iRODS python API: https://github.com/chStaiger/irods-performances
  - 4GB from home network through python API takes about 30 minutes.

### eLabJournal

- Data Upload to eLabJournal works in an own thread.  Hence, you can continue working in other Tabs of the application.
- The loading of Projects and Experiments takes quite long and depends on the performance of the eLabJournal server and the eLabJournal python library.
- After clicking 'Upload' the application also waits for some response of the eLabJournal and seems to 'hang'.
- Before data is uploaded, there is a check whether data fits on th iRODS resource.
- Small hickup after Data upload to eLabJournal finished.  The stopping and cleaning up of the thread is done in the main application and affects all Tabs for a short moment.

## Delete function

- If a lot of data is deleted, the application 'hangs'.
