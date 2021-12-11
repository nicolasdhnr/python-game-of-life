import copy

import cellsim
import os
import time
import psutil
import cProfile, pstats, io


#  ====================================Profilers =============================================
# Time profiler
def time_profile(fnc):
    """A decorator that uses cProfile to profile a function"""

    def inner(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval

    return inner


# Space profiler
def process_memory():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss


def space_profile(func):
    def wrapper(*args, **kwargs):
        mem_before = process_memory()
        result = func(*args, **kwargs)
        mem_after = process_memory()
        print("{}:consumed memory: {:,}".format(
            func.__name__,
            mem_before, mem_after, mem_after - mem_before))

        return result

    return wrapper


# ===============================================Start of Code=====================================================

class Cell:
    """

    """

    def __init__(self, alive=False):
        # Error Handling
        self.alive = alive

    @property
    def living_neighbours(self):
        pass

    def __str__(self):
        if self.alive:
            return "O"
        else:
            return "."

    def is_alive(self):
        return self.alive

    def update_cell(self):
        pass


# TODO: add this function


class Cancer(Cell):
    def __init__(self, alive=False):
        super().__init__(alive)

    def update_cell(self):
        pass


# TODO: Add this function


# @time_profile
@space_profile
class Tissue:
    """"
    """

    def __init__(self, rows=1, cols=1,
                 CellType=Cell):  # idk if this is the right way to do it - what if cell is defined after ?
        self.rows = rows
        self.cols = cols
        if issubclass(CellType,
                      object):  # CellType should be a "new-style class" that is, user-defined. https://stackoverflow.com/questions/54867/what-is-the-difference-between-old-style-and-new-style-classes-in-python
            # TODO: Should also have the attributes of a cell or cancer cell. Object is default superclass

            self.CellType = CellType
        else:
            self.CellType = Cell

        self.matrix = []

    def __str__(self):

        tissue_str = ""  # TODO: Better Variable names
        for row in self.matrix:
            tissue_str += f'{"".join(map(lambda x: str(x), row))}\n'  # might not be most efficient way to convert everything.
        return tissue_str

    def __getitem__(self, idx):
        """ Defines the getter for the Tissue Class"""
        return self.matrix[idx]

    def __setitem__(self, key, value):
        """ Defines the setter for the Tissue Class"""
        self.matrix[key] = value

    # Should this be a class method?

    def seed_from_matrix(self, seed_matrix):
        # TODO: Enforce the arguments of seed matrix to be valid
        self.matrix = copy.deepcopy(seed_matrix)

    def seed_from_file(self, filename, CellType=Cell):
        """ This function takes a filename and CellType as input and changes the self.matrix attribute to seed.

        :argument

        :return
        """
        # TODO: Include relative path of filename.
        self.matrix = []  # Is this going to modify all instances too? Do we want it to? Should we use .clear()?
        if ".txt" not in filename:
            self.matrix = []
        else:
            try:
                with open(filename, "r", encoding="utf-8") as f:  # TODO: Add support for different paths.
                    # Read file, into a list without any leading or trailing spaces.
                    temp = f.readlines()
                    for elem in temp:
                        self.matrix.append(list(
                            map(lambda x: CellType(False) if x == "." else CellType(True), elem.replace("\n", ""))))
                    # TODO: error handling if its something other than those 2 in there or remove them from the file. Code not robust enough here.
                    del temp

            except IOError:
                self.matrix = []

# TODO: CellType check decorator cos I need it everywhere
