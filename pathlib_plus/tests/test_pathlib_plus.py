from os.path import expandvars
import unittest
from pathlib_plus.pathlib_plus import Path

TREE = [
    '1',
    '2/2_1',
    '3/3_1/3_1_1',
    ]

class Test_pathlib_plus(unittest.TestCase):
    def setUp(self):
        self._root = Path('%temp%')
        self._root = self._root.joinpath('test_pathlib_plus')

    def test_expandvars(self):
        p = '%temp%'
        path_o = Path(p)
        assert str(path_o.expandvars()) == expandvars(p)

    def test_symlink_to_junction(self):
        self._root = self._root.expandvars()
        target = self._root.joinpath('target')
        target.mkdir(parents=True, exist_ok=True)
        _file = target.joinpath('TestFile.txt')
        _text = 'Hello world'
        _file.write_text(_text)

        src = self._root.joinpath('source')
        print(str(src), str(target))
        src.symlink_to(target, junction=True)
        _file = src.joinpath('TestFile.txt')
        assert _file.exists()
        assert _file.read_text() == _text, _file.read_text()

        self._root.rmdir_tree(files_too=True)

    def test_rmdir_tree(self):
        self._root = self._root.expandvars()
        # Create bare tree
        for d in TREE:
            self._root.joinpath(d).mkdir(parents=True, exist_ok=True)
        assert self._root.joinpath(TREE[-1]).exists()
        self._root.rmdir_tree()
        assert not self._root.exists()

    def test_rmdir_tree_files(self):
        self._root = self._root.expandvars()
        # Create bare tree
        for d in TREE:
            self._root.joinpath(d).mkdir(parents=True, exist_ok=True)
        assert self._root.joinpath(TREE[-1]).exists()

        _file = self._root.joinpath(TREE[-1]).joinpath('TestFile.txt')
        _text = 'Hello world'
        _file.write_text(_text)
        assert _file.exists()
        assert _file.read_text() == _text, _file.read_text()

        # Can't delete tree with files
        with self.assertRaises(Exception):
            self._root.rmdir_tree(files_too=False)
        assert _file.exists()

        # Unless files_too requests it
        self._root.rmdir_tree(files_too=True)
        assert not self._root.exists()

if __name__ == '__main__':
    unittest.main()
