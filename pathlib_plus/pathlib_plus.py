from os.path import expandvars
from pathlib import Path as _Path_, _windows_flavour, _posix_flavour
import os
from _winapi import CreateJunction

"""
Subclassing trickery from
https://codereview.stackexchange.com/questions/162426/subclassing-pathlib-path

"""

class Path(_Path_):
    """ Subclass of pathlib Path to add useful methods """
    _flavour = _windows_flavour if os.name == 'nt' else _posix_flavour
    def rmdir_tree(self, files_too=False):
        """
        Delete the branches from the path
        If files_too then files in the branches too.
        """
        # Depth-first search
        def _recurse(_p, _files_too):
            if _p.is_dir():
                for b in _p.iterdir():
                    _recurse(b, files_too)
                try:
                    _p.rmdir()
                except Exception as e:
                    print(e)
                    raise e
            elif _files_too:
                _p.unlink()
        _recurse(self, files_too)

    def expandvars(self):
        """ mysteriously not available in pathlib """
        return Path(expandvars(str(self)))

    def symlink_to(self, src_path, dest_path, junction=False):
        """
        If junction and:
        * on Windows
        * to a folder
        create a junction point, with the advantage that admin rights are
        not required
        """
        if junction and os.name == 'nt' and dest_path.isdir():
            CreateJunction(src_path, dest_path)
        else:
            symlink_to(src_path, dest_path)

    def walk(self):
        """
        Should be here, no?
        """
        pass

