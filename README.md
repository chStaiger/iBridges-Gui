# iBridges

<p align="center">
  <p align="center">
    <a href="https://chstaiger.github.io/iBridges-Gui/"><strong> Documentation »</strong></a> .
    <a href="https://github.com/chStaiger/iBridges-Gui/issues">Report Bug or Request Feature</a>
    .
  </p>
</p>

## About

The git repository contains a generic *iRODS* graphical user interface and the corresponding command-line interface clients.  The GUI and CLI work with any *iRODS* instance.  However, for user and data security we depend on some *iRODS* event hooks that need to be installed on the *iRODS* server.  Please refer to the documentation below.

## Authors

Tim van Daalen, Christine Staiger

Wageningen University & Research 2021

## Contributors

J.P. Mc Farland

University of Groningen, Center for Information Technology, 2022

## Dependencies

### Supported iRODS versions

- 4.2.11, 4.2.12
- 4.3.0

### Python

- Python 3 (>= 3.9)
  - Tested with python versions 3.9 and 3.10 on Windows, Ubuntu20.22 and MacOs
- pip-22.2.2
- Python packages (see install via `requirements.txt` below)

Install dependencies with, for example:

```sh
python3.10 -m pip install -r requirements.txt
```
### icommands (optional)
If the icommands are installed, the users can choose them as backend for up and downloads.

## Usage
```
export PYTHON_IRODSCLIENT_DEFAULT_XML=QUASI_XML
./iBridges.py
```

Please consult the documentation for more information about the configuration: 

<p align="center">
    <a href="https://chstaiger.github.io/iBridges-Gui/docs/getting-started.html#configuration"><strong> iBridges Configuration »</strong></a> .
    
## Contributing
### Code
Instructions on how to extend the GUI or contribute to the code base can be found in the [documentation](https://chstaiger.github.io/iBridges-Gui/).

## License
This project is licensed under the GPL-v3 license.
The full license can be found in [LICENSE](LICENSE).
