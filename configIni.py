""" docstring """
from configparser import ConfigParser

RFACTOR_FOLDER_SECTION = 'rFactor folder'
NESTED_CONFIG_FILES_SECTION = 'Nested config files'

SECTIONS = [
    RFACTOR_FOLDER_SECTION,
    'Locations',
    'Vehicles'
]


class Config:
    """ docstring """
    def __init__(self, config_file_name):
        # instantiate
        self.config_file_name = config_file_name
        self.config = ConfigParser(interpolation=None, allow_no_value=True)

        # set default value(s)
        _section = RFACTOR_FOLDER_SECTION
        self.config.add_section(_section)
        self.config.set(_section,
                        'Path',
                        r'%ProgramFiles(x86)%\Steam\steamapps\common\rFactor 2')

        # if there is an existing file parse values over those
        try:
            # .read(file) doesn't give an exception, open(file) does
            self.config.read_file(open(config_file_name))
        except Exception as e:
            print(f'Could not open "{config_file_name}"\n', e)
            self.config_file_name = 'NO CONFIG FILE'
            return

        self._locations = []
        if self.config.has_section('Locations'):
            for _location in (self.config.options('Locations')):
                self._locations.append(_location)
        #except:
        #    print(f'No Locations in {self.config_file_name}')

        self._vehicles = []
        if self.config.has_section('Vehicles'):
            for _vehicle in (self.config.options('Vehicles')):
                self._vehicles.append(_vehicle)
        #except:
        #    print(f'No Vehicles in {self.config_file_name}')

        if self.config.has_section(NESTED_CONFIG_FILES_SECTION):
            for _config_file in (self.config.options(NESTED_CONFIG_FILES_SECTION)):
                _nested_config = Config(_config_file)
                for _location in _nested_config.get_locations():
                    self._locations.append(_location)
                for _vehicle in _nested_config.get_vehicles():
                    self._vehicles.append(_vehicle)
        # de-dupe the lists
        self._locations = list(set(self._locations))
        self._vehicles = list(set(self._vehicles))

    def get(self, _section, _val):
        """ get a config value """
        try:
            # get existing value
            return self.config.get(_section, _val)
        except:  # pylint: disable=bare-except
            # No such section in file
            return None
    def get_rfactor_folder(self) -> str:
        return self.get(RFACTOR_FOLDER_SECTION, 'Path')
    def get_locations(self) -> list:
        return self._locations
    def get_vehicles(self) -> list:
        return self._vehicles


if __name__ == "__main__":
    _CONFIG_O = Config('no such file')
    assert _CONFIG_O.get_rfactor_folder() == \
        r'c:\Program Files(x86)\Steam\steamapps\common\rFactor 2'
    assert _CONFIG_O.get_locations() == []
    assert _CONFIG_O.get_vehicles() == []

    _CONFIG_O = Config('sample.modlist.txt')
    print(_CONFIG_O.get_locations())
    print(_CONFIG_O.get_vehicles())