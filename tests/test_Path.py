"""
Unit test use of Path
"""
from pathlib_plus.pathlib_plus import Path
from os.path import expandvars
import unittest

test_base = Path(expandvars(r'%temp%'))
test_folder = Path(r'Program Files(x86)\Steam\steamapps\common\rFactor 2')

DUMMY_FOLDERS = [
    r'Installed\Locations\3pa_bathurst_2014',
    r'Installed\Locations\60sHockenheim',
    r'Installed\Locations\70sWatkinsGlen',
    r'Installed\Locations\adelaide_street_circuit',
    r'Installed\Locations\barbagallo_v2.3',
    r'Installed\Locations\bathurst_2016_v3',
    r'Installed\Locations\phillip island',
    r'Installed\Vehicles\ac_427sc_1967',
    r'Installed\Vehicles\ac_cobra_1954_endurance',
    r'Installed\Vehicles\Brabham_1966',
    r'Installed\Vehicles\datsun bluebird',
    r'Installed\Vehicles\Ferrari_312_67',
    r'Installed\Vehicles\flat12_917k_1971',
    r'Installed\Vehicles\howston_diss_1974',
    r'Installed\Vehicles\howston_g4_1967_endurance',
    r'Installed\Vehicles\howston_g4_1968',
    r'Installed\Vehicles\howston_g6_1968',
    r'Installed\Vehicles\lola_t70_spyder',
    r'Installed\Vehicles\mak-corp_group_c',
    r'Installed\Vehicles\t70 mkiiib',
    r'Installed\Vehicles\toyotacelicagto_1986'
    ]

class Test_test_Path(unittest.TestCase):
    def setUp(self):
        self.rf2dir = test_base.joinpath(test_folder)
        self.content_store = self.rf2dir.joinpath('Userdata')\
            .joinpath('ContentStorage')
        self.installed = self.rf2dir.joinpath('Installed')
        self.test_mkdir()
        for f in DUMMY_FOLDERS:
            self.rf2dir.joinpath(f).mkdir(parents=True, exist_ok=True)

    def test_setup(self):
        _tip = self.rf2dir.joinpath(DUMMY_FOLDERS[-1])
        assert _tip.exists()
        pass

    def test_tearDown(self):
        self.test_mkdir()

    def test_mkdir(self):
        """
        for p in reversed(self.rf2dir.parents):
            print(p)
            #if not Path(p).exists():
            #    Path(p).mkdir() # exist_ok=True)
        """
        self.rf2dir.mkdir(parents=True, exist_ok=True)
        assert self.rf2dir.exists(), self.rf2dir
    def tearDown(self):
        """
        for f in DUMMY_FOLDERS:
            self.rf2dir.joinpath(f).rmdir()
        for f in DUMMY_FOLDERS:
            d = self.rf2dir.joinpath(Path(f).parent)
            if d.exists():
                d.rmdir()
        for f in DUMMY_FOLDERS:
            d = self.rf2dir.joinpath(Path(f).parent.parent)
            if d.exists():
                d.rmdir()
        """
        self.rf2dir.rmdir_tree()
        # Now work down to test_base
        for p in test_folder.parents:
            # All except the . at the end
            if p != Path('.'):
                test_base.joinpath(p).rmdir()

    """
    def test_mkdir(self):
        _cs_locations = self.content_store.joinpath('Locations')
        _cs_vehicles = self.content_store.joinpath('Vehicles')
        try:
            self.content_store.mkdir(parents=False, exist_ok=True)
        except FileNotFoundError:
            raise FileNotFoundError
        except FileExistsError:
            raise FileExistsError
        except Exception as e:
            print(e)
            raise e
    """

if __name__ == '__main__':
    unittest.main()
