"""
New, simpler method:
The moment rFactor 2.exe starts running move Installed\Locations and Vehicles
somewhere else.  Take the list of tracks/cars (to be precise, their folders)
and move them *back* to Installed.

When rF2 goes to read data it will find only the selected mods.

The moment rFactor 2.exe stops running, move the remainder back Installed and
things are back as they were.

Also have a repair function that moves everything back to Installed

"""
from pathlib_plus.pathlib_plus import Path
import os
import psutil
from subprocess import Popen, call
import sys
from time import sleep

from configIni import Config

class rF2_check:
    rf2_pid = None          # Once we've found rF2 running
    rf2_pid_counter = 0     # Counter to check if running
    rf2_running = False

    def __init__(self):
        self.__find_rf2_pid()

    ###########################################################
    def __find_rf2_pid(self):
        """ Find the process ID for rfactor2.exe.  Takes a while """
        for pid in psutil.pids():
            try:
                p = psutil.Process(pid)
            except psutil.NoSuchProcess:
                continue
            if p.name().lower().startswith('rfactor2.exe'):
                self.rf2_pid = pid
                break

    ###########################################################
    # Access functions

    def isRF2running(self, find_counter=200, found_counter=5):
        """
        Both "rFactor 2 Launcher" and "rf2" processes are found
        whether it's the launcher or the game that's running BUT
        rfactor2.exe is only present if the game is running.
        Beacuse this takes some time, control how often it's checked using:
        find_counter: how often to check if rF2 is not running
        found_counter: how often to check once rF2 is running
        """
        if self.rf2_pid_counter == 0: # first time
            self.rf2_pid_counter = find_counter
        if self.rf2_pid:
            if self.rf2_pid_counter >= found_counter:
                self.rf2_pid_counter = 0
                try:
                    p = psutil.Process(self.rf2_pid)
                except psutil.NoSuchProcess:
                    self.rf2_pid = None
                    return False
                if p.name().lower().startswith('rfactor2.exe'):
                    self.rf2_running = True
        else:
            if self.rf2_pid_counter >= find_counter:
                self.rf2_pid_counter = 0
                self.__find_rf2_pid()
                self.rf2_running = False
        self.rf2_pid_counter += 1
        return self.rf2_running

class Mod_manager():
    def __init__(self, rf2path):
        self.rf2dir = Path(rf2path).expandvars()
        self.content_store = self.rf2dir.joinpath('Userdata')\
            .joinpath('ContentStorage')
        self.installed = self.rf2dir.joinpath('Installed')
        if not self.rf2dir.is_dir():
            return None

    def setup(self):
        """
        Move Installed\Locations and Installed\Vehicles
        to Userdata\ContentStorage\Locations & Vehicles
        """

        _cs_locations = self.content_store.joinpath('Locations')
        _cs_vehicles = self.content_store.joinpath('Vehicles')
        try:
            self.content_store.mkdir(parents=True, exist_ok=True)
        except FileNotFoundError:
            raise FileNotFoundError
        except FileExistsError:
            raise FileExistsError
        except Exception as e:
            print(e)
            raise e
        if 0:
            # Move Installed\Locations and Installed\Vehicles
            # to Userdata\ContentStorage\Locations & Vehicles
            _locations = self.installed.joinpath('Locations')
            _vehicles = self.installed.joinpath('Vehicles')
            _locations.rename(_cs_locations)
            _vehicles.rename(_cs_vehicles)
        else:
            # Method 3: create Userdata\ContentStorage\Locations & Vehicles
            # containing links to selected mods in Installed\Locations & Vehicles
            _cs_locations.mkdir(parents=True, exist_ok=True)
            _cs_vehicles.mkdir(parents=True, exist_ok=True)

    def select_mod(self, mod):
        """
        Given a new list of tracks/cars (to be precise, their folders)
        * move the list from ContentStorage to Installed
        """
        _ins_path = self.installed.joinpath(mod[0])
        _cs_path = self.content_store.joinpath(mod[0])
        _ins_mod = _ins_path.joinpath(mod[1])
        _cs_mod = _cs_path.joinpath(mod[1])
        if 0:
            if not _cs_mod.is_dir():
                return None
            if not _ins_path.is_dir():
                _ins_path.mkdir(parents=True, exist_ok=True)
            _cs_mod.rename(_ins_mod)
        else: # Method 3
            _cs_mod.symlink_to(_ins_mod, junction=True)
        return mod

    def unselect_mods(self):
        """
        Move any folders in ContentStorage back to Installed
        """
        for _type in ['Locations', 'Vehicles']:
            for _cs_mod in self.content_store.joinpath(_type).iterdir():
                _ins_path = self.installed.joinpath(_type)
                _ins_mod = _ins_path.joinpath(_cs_mod.name)
                _cs_mod.rename(_ins_mod)
            # Tidy up, remove the directory
            self.content_store.joinpath(_type).rmdir()
        self.content_store.rmdir()


    def repair(self):
        """
        * move any folders in SelectedContent back to Installed
        """
        self.unselect_mods()

class Mod_manager_app:
    def cmd_line(self, config_file_name):
        self._CONFIG_O = Config(config_file_name)
        self._rf2path = Path(self._CONFIG_O.get_rfactor_folder()).expandvars()
        #self._rf2path = r'c:\Temp\dummy Rf2'
        self._mm_o = Mod_manager(self._rf2path)
        if not self._mm_o:
            SystemExit(99)
        return Path(self._rf2path)    # for unit test

    def wait_for_rf2_to_start(self):
        self.rf2_o = rF2_check()

        #call('"c:/Program Files(x86)/Steam/steam" -applaunch 365960')
        print('\nWaiting for rFactor 2 to start...')

        while not self.rf2_o.isRF2running():
            sleep(.2)

        print('\nrFactor 2 started')

    def set_up(self):
        self._mm_o.setup()
        for location in self._CONFIG_O.get_locations():
            if not self._mm_o.select_mod(('Locations', location)):
                print(f'Locations {location} not found')

        for vehicle in self._CONFIG_O.get_vehicles():
            if not self._mm_o.select_mod(('Vehicles', vehicle)):
                print(f'Vehicles {vehicle} not found')
        # for unit test:
        return(self._CONFIG_O.get_locations(), self._CONFIG_O.get_vehicles())

    def start_rf2_single_player(self):
        self.rf2_o = rF2_check()
        _pop = os.getcwd()  # save current directory
        os.chdir(self._rf2path)
        cmd = '"' + str(self._rf2path) + \
            r'\Bin64\rFactor2.exe"  +singleplayer +path="."'
        print(cmd)
        call(cmd) # actually, it doesn't return until rf2 exits
        os.chdir(_pop)

    def wait_for_rf2_to_exit(self):
        print('\nWaiting for rFactor 2 to exit...')
        while self.rf2_o.isRF2running():
            sleep(1)

        print('\nrFactor 2 exited')

    def tear_down(self):
        #self._mm_o.repair()
        self._mm_o.unselect_mods()

def main():
    mm_mgr_o = Mod_manager_app()
    mm_mgr_o.cmd_line(sys.argv[1])
    #mm_mgr_o.wait_for_rf2_to_start()
    mm_mgr_o.set_up()
    mm_mgr_o.start_rf2_single_player()
    mm_mgr_o.wait_for_rf2_to_exit()
    mm_mgr_o.tear_down()

if __name__ == "__main__":
    main()




