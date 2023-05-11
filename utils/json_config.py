"""Manipulate configurations stored as JSON files.

"""
import json

from . import path


class JSONConfig:
    """A configuration stored in a JSON file.

    """

    def __init__(self, filepath: str = ''):
        """Create the configuration.

        Parameters
        ----------
        filepath : str

        """
        self._config = {}
        self.filepath = filepath

    def __bool__(self) -> bool:
        """If 'config' dictionary is truthy.

        Returns
        -------
        bool
            If self.config is truthy.

        """
        return self.config != {}

    def __repr__(self) -> str:
        """Representation of this configuration.

        Returns
        -------
        str
            Representation.

        """
        return f'{self.__class__.__name__}("{self._config.__repr__()}")'

    @property
    def config(self) -> dict:
        """A persistent configuration dictionary.

        Attempt to load a configuration from the JSON file.

        Returns
        -------
        dict
            A dictionary loaded from the configuration file, if it
            exists.  The empty persistent dictionary otherwise.

        """
        if self._config == {}:
            if self.filepath.is_file():
                with open(self.filepath, 'r', encoding='utf-8') as confd:
                    self._config.update(json.load(confd))
        return self._config

    @config.setter
    def config(self, conf_dict: dict):
        """Configuration setter.

        Set the configuration to `conf_dict`.
        file.

        Parameters
        ----------
        conf_dict : dict
            New configuration.

        """
        self._config.clear()
        self._config.update(conf_dict)

    @config.deleter
    def config(self):
        """Configuration deleter.

        Delete the contents of the configuration dictionary.

        """
        self._config.clear()

    @property
    def filepath(self) -> path.LocalPath:
        """Path to configuration file.

        Returns
        -------
        path.LocalPath

        """
        if not isinstance(self._filepath, path.LocalPath):
            self._filepath = path.LocalPath(self._filepath)
        return self._filepath

    @filepath.setter
    def filepath(self, filepath: str):
        """Filepath setter.

        Parameters
        ----------
        filepath : str
            New filepath.

        """
        self._filepath = path.LocalPath(filepath).expanduser()

    def clear(self):
        """Clear the configuration .

        """
        self._config.clear()

    def reset(self):
        """Reset current instance

        """
        self._config.clear()
        self._filepath = ''

    def save(self):
        """Write the serialized configuration dictionary to the JSON
        file.

        """
        config = {}
        if self.config != {}:
            config = self.config
        with open(self.filepath, 'w', encoding='utf-8') as confd:
            json.dump(config, confd, indent=4, sort_keys=True)
