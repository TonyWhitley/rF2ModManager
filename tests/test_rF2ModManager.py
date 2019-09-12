import unittest

from test_Path import Test_test_Path
from rF2ModManager import Mod_manager

LOCATIONS = [
    '3PA_Bathurst_2014',
    'Adelaide_Street_Circuit',
    'Barbagallo_v2.3'
    ]

VEHICLES = [
    'AC_427SC_1967',
    'AC_Cobra_1954_Endurance',
    'Datsun Bluebird',
    'FLAT12_917k_1971',
    'Howston_DISS_1974'
    ]

class Test_test_rF2ModManager(unittest.TestCase):
    def setUp(self):
        self.test_path = Test_test_Path()
        self.test_path.setUp()
    def tearDown(self):
        self.test_path.tearDown()
    def test_mod_manager_setup(self):
        self.mm_o = Mod_manager(self.test_path.rf2dir)
        assert self.mm_o

        self.mm_o.setup()
        _cs_locations = self.test_path.content_store.joinpath('Locations')
        _cs_vehicles = self.test_path.content_store.joinpath('Vehicles')
        assert _cs_locations.exists(), _cs_locations
        assert _cs_vehicles.exists(), _cs_vehicles
        pass

    def test_mod_manager_select_mods(self):
        self.test_mod_manager_setup()
        for location in LOCATIONS:
            if not self.mm_o.select_mod(('Locations', location)):
                print(f'Locations {location} not found')

        for vehicle in VEHICLES:
            if not self.mm_o.select_mod(('Vehicles', vehicle)):
                print(f'Vehicles {vehicle} not found')

        _ins_last_location = self.test_path.installed.joinpath('Locations')\
            .joinpath(LOCATIONS[-1])
        _ins_last_vehicle = self.test_path.installed.joinpath('Vehicles')\
            .joinpath(VEHICLES[-1])
        assert _ins_last_location.exists(), _ins_last_location
        assert _ins_last_vehicle.exists(), _ins_last_vehicle

    def test_mod_manager_cleanup(self):
        self.test_mod_manager_select_mods()
        self.mm_o.unselect_mods()
        assert not self.test_path.content_store.exists(), self.content_store


if __name__ == '__main__':
    unittest.main()
