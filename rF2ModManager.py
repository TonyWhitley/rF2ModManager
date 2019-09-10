"""
Install:
This only has to be done (requiring Admin rights for the symlinks) once.

Move Installed\Locations and Installed\Vehicles
to Userdata\RedirectedContent\Locations & Vehicles

Set up symlinks replacing Installed\Locations and Installed\Vehicles
pointing to Userdata\RedirectedContent\Locations & Vehicles
(in there is a symlink to Userdata\SelectedContent)

There is also Userdata\SelectedContent\Locations & Vehicles

In use:
Given a new list of tracks/cars (to be precise, their folders)
* move any folders in SelectedContent back to RedirectedContent
* move the list from RedirectedContent to SelectedContent

The moment rFactor 2.exe starts running, if SelectedContent is not empty
* rename RedirectedContent to RedirectedContent.IDLE
* rename SelectedContent to RedirectedContent

When rF2 goes to read data it will follow the symlink to
Userdata\RedirectedContent which is now Userdata\SelectedContent

The moment rFactor 2.exe stops running, if RedirectedContent.IDLE exists
* rename RedirectedContent back to SelectedContent
* rename RedirectedContent.IDLE to RedirectedContent

So the directory structure is:
Userdata\RedirectedContent\Locations\track1
                                    \track2 etc.
                           Vehicles\car1
                                   \car2 etc.

Userdata\SelectedContent\Locations\track3
                                  \track4 etc.
                         Vehicles\car3
                                 \car4 etc.

and those two swap over when rF2 is running then back when it stops running.

Also have a repair function that
if RedirectedContent.IDLE exists
* rename RedirectedContent back to SelectedContent
* rename RedirectedContent.IDLE to RedirectedContent
* move any folders in SelectedContent back to RedirectedContent

"""
from pathlib import Path
import psutil
from time import sleep
from _winapi import CreateJunction

class rF2:
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
        self.rf2dir = Path(rf2path).expanduser()
        self.all_content = self.rf2dir.joinpath('Userdata')\
            .joinpath('ContentStorage')
        self.redirected_content = self.all_content.joinpath('RedirectedContent')
        self.installed = self.rf2dir.joinpath('Installed')
        self.selected_content = self.all_content.joinpath('SelectedContent')
        if not self.rf2dir.is_dir():
            return None
        if not self.redirected_content.is_dir():
            self.install()

    def install(self):
        """
        Move Installed\Locations and Installed\Vehicles
        to Userdata\RedirectedContent\Locations & Vehicles

        Set up symlinks replacing Installed\Locations and Installed\Vehicles
        pointing to Userdata\RedirectedContent\Locations & Vehicles
        (in there is a symlink to Userdata\SelectedContent)

        There is also Userdata\SelectedContent\Locations & Vehicles
        """

        _sc_locations = self.selected_content.joinpath('Locations')
        _sc_vehicles = self.selected_content.joinpath('Vehicles')
        try:
            self.all_content.mkdir(parents=False, exist_ok=False)
            self.redirected_content.mkdir(parents=False, exist_ok=False)
            self.selected_content.mkdir(parents=False, exist_ok=False)
            _sc_locations.mkdir(parents=False, exist_ok=False)
            _sc_vehicles.mkdir(parents=False, exist_ok=False)
        except FileNotFoundError:
            raise FileNotFoundError
        except FileExistsError:
            raise FileExistsError
        except Exception as e:
            print(e)
            raise e
        # Move Installed\Locations and Installed\Vehicles
        # to Userdata\RedirectedContent\Locations & Vehicles
        _locations = self.installed.joinpath('Locations')
        _vehicles = self.installed.joinpath('Vehicles')
        _rc_locations = self.redirected_content.joinpath('Locations')
        _rc_vehicles = self.redirected_content.joinpath('Vehicles')
        _locations.rename(_rc_locations)
        _vehicles.rename(_rc_vehicles)

        # symlinks (needs admin) vs. junctions (don't)
        junction = str(_locations)  # Link
        src = str(_rc_locations)    # points to
        #src = str(self.redirected_content)
        CreateJunction(src, junction)

        junction = str(_vehicles)       # Link
        src = str(_rc_vehicles)    # points to
        #src = str(self.redirected_content)
        CreateJunction(src, junction)

        #self.installed.joinpath('Locations').symlink_to(_locations)
        #self.installed.joinpath('Vehicles').symlink_to(_vehicles)

    def select_mod(self, mod):
        """
        Given a new list of tracks/cars (to be precise, their folders)
        * move the list from RedirectedContent to SelectedContent
        """
        _rc_mods = self.redirected_content.joinpath(mod[0])
        _sc_mods = self.selected_content.joinpath(mod[0])
        _rc_mod = _rc_mods.joinpath(mod[1])
        _sc_mod = _sc_mods.joinpath(mod[1])
        if not _rc_mod.is_dir():
            return None
        _rc_mod.rename(_sc_mod)
        return mod

    def unselect_mods(self):
        """
        Move any folders in SelectedContent back to RedirectedContent
        """
        for _type in ['Locations', 'Vehicles']:
            for _sc_mod in self.selected_content.joinpath(_type).iterdir():
                _rc_path = self.redirected_content.joinpath(_type)
                _rc_mod = _rc_path.joinpath(_sc_mod.name)
                _sc_mod.rename(_rc_mod)

    def use_selected_content(self):
        """
        If SelectedContent is not empty
        * rename RedirectedContent to RedirectedContent.IDLE
        * rename SelectedContent to RedirectedContent
        """
        if self.selected_content.glob('**'):
            # SelectedContent is not empty
            _new_name = self.redirected_content.parent.joinpath(
                self.redirected_content.name+'.IDLE')
            self.redirected_content.rename(_new_name)
            self.selected_content.rename(self.redirected_content)

    def stop_using_selected_content(self):
        """
        If RedirectedContent.IDLE exists
        * rename RedirectedContent back to SelectedContent
        * rename RedirectedContent.IDLE to RedirectedContent
        """
        _new_name = self.redirected_content.parent.joinpath(
            self.redirected_content.name+'.IDLE')
        if _new_name.exists():
            self.redirected_content.rename(self.selected_content)
            _new_name.rename(self.redirected_content)
            return True
        return False

    def repair(self):
        """
        if RedirectedContent.IDLE exists
        * rename RedirectedContent back to SelectedContent
        * rename RedirectedContent.IDLE to RedirectedContent
        * move any folders in SelectedContent back to RedirectedContent
        """
        if self.stop_using_selected_content():
            self.unselect_mods()

def main():
    rf2path = r'%ProgramFiles(x86)%\Steam\steamapps\common\rFactor 2'
    #rf2path = r'c:\Temp\dummyRf2'
    mm_o = Mod_manager(rf2path)
    if not mm_o:
        SystemExit(99)
    if not mm_o.select_mod(('Locations', '60sHockenheim')):
        print('Locations 60sHockenheim not found')
    if not mm_o.select_mod(('Vehicles', 'Ferrari_312_67')):
        print('Vehicles Ferrari_312_67 not found')

    rf2_o = rF2()

    while not rf2_o.isRF2running():
        sleep(.2)

    mm_o.use_selected_content()

    while rf2_o.isRF2running():
        sleep(1)

    mm_o.stop_using_selected_content()
    #mm_o.repair()
    mm_o.unselect_mods()



if __name__ == "__main__":
    main()




