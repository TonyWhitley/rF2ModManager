import unittest

from configIni import Config

class Test_test_configini(unittest.TestCase):
    def test_nested_config_files(self):
        config_o = Config('1960s_F1.modlist.txt ')
        locations = config_o.get_locations()
        vehicles = config_o.get_vehicles()
        assert locations
        assert vehicles


if __name__ == '__main__':
    unittest.main()
