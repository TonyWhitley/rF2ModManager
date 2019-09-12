from os.path import expandvars
import unittest
from pathlib_plus.pathlib_plus import Path

TREE = [
    '1',
    '2/2_1',
    '3/3_1/3_1_1',
    ]

class Test_pathlib_plus(unittest.TestCase):
    def test_expandvars(self):
        p = '%temp%'
        path_o = Path(p)
        assert str(path_o.expandvars()) == expandvars(p)

    def test_rmdir_tree(self):
        _root = Path('%temp%')
        _root = _root.joinpath('test_pathlib_plus')
        _root = _root.expandvars()
        # Create bare tree
        for d in TREE:
            _root.joinpath(d).mkdir(parents=True, exist_ok=True)
        assert _root.joinpath(TREE[-1]).exists()
        _root.rmdir_tree()
        assert not _root.exists()

    def test_rmdir_tree_files(self):
        _root = Path('%temp%')
        _root = _root.joinpath('test_pathlib_plus')
        _root = _root.expandvars()
        # Create bare tree
        for d in TREE:
            _root.joinpath(d).mkdir(parents=True, exist_ok=True)
        assert _root.joinpath(TREE[-1]).exists()

        _file = _root.joinpath(TREE[-1]).joinpath('TestFile.txt')
        _text = 'Hello world'
        _file.write_text(_text)
        assert _file.exists()
        assert _file.read_text() == _text, _file.read_text()

        # Can't delete tree with files
        with self.assertRaises(Exception):
            _root.rmdir_tree(files_too=False)
        assert _file.exists()

        # Unless files_too requests it
        _root.rmdir_tree(files_too=True)
        assert not _root.exists()

if __name__ == '__main__':
    unittest.main()
