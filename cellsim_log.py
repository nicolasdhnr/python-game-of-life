import copy

import cellsim_linear
import os
import time
# import psutil
import cProfile, pstats, io


# TODO: DON'T IMPORT WHOLE MODULE

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


# def space_profile(func):
#     def wrapper(*args, **kwargs):
#         mem_before = process_memory()
#         result = func(*args, **kwargs)
#         mem_after = process_memory()
#         print("{}:consumed memory: {:,}".format(
#             func.__name__,
#             mem_before, mem_after, mem_after - mem_before))
#
#         return result
#
#     return wrapper


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


@time_profile
# @space_profile
class Tissue:
    """Represents the space in which the cell grows.
        Attributes:
            row (int):
            cols (int):
            CellType (Cell, Cancer or other valid type):

        Methods:
            init:
            str:
            getitem:
            setitem:
            seed_from_matrix:
            seed_from_file

    """

    # TODO: Should check if the CellType has all the required attributes.
    def __init__(self, rows=1, cols=1, CellType=Cell):
        # idk if this is the right way to do it - what if cell is defined after ?
        self.rows = rows
        self.cols = cols

        # CellType should be a "new-style class" that is, user-defined. Object is the default superclass -> Good check to have that the class is user defined and we are not trying to pass"int"

        # https://stackoverflow.com/questions/54867/what-is-the-difference-between-old-style-and-new-style-classes-in-python
        if issubclass(CellType, object):

            self.CellType = CellType

        else:
            self.CellType = Cell

        self.matrix = [[CellType() for _ in range(self.cols)] for _ in range(self.rows)]

    def __str__(self):
        tissue_str = ""
        for row in self.matrix:
            tissue_str += f'{"".join(map(lambda x: str(x), row))}\n'  # might not be most efficient way to convert everything.
        return tissue_str

    def __getitem__(self, idx):
        """ Defines the getter for the Tissue class"""
        return self.matrix[idx]

    def __setitem__(self, key, value):
        """ Defines the setter for the Tissue class"""
        self.matrix[key] = value

    def seed_from_matrix(self, seed_matrix):  # Should this be a class method?
        """ Overwrite the four attribute variables using a single argument.
        :param seed_matrix:
        """
        # TODO: Enforce the arguments of seed matrix to be valid:
        # TODO: rows and columns should update.

        self.matrix = copy.deepcopy(seed_matrix)
        self.cols = len(self.matrix)
        self.rows = len(self.matrix[0])  # Check if this overrides properly

    def seed_from_file(self, filename, CellType=Cell):
        """ This function takes a filename and CellType as input and changes the self.matrix attribute to seed.

        :argument

        :return
        """
        # TODO: Include relative path of filename.
        self.matrix.clear()  # Is this going to modify all instances too? Do we want it to? Should we use .clear()?
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

    # TODO: Change ">" depending on whether it is probability of being alive or dead.
    # TODO: Try opti with for loop or list comprehension
    def seed_random(self, probability, CellType):
        # We want to avoid having to call __init__ at each iteration of the coming loop so we define the two possible states:

        from random import random
        # Might be a better way to do this.

        # This line will override the values in self.matrix in 2 steps:
        # - The list comprehension selects each row of the matrix
        # - The lambda function is applied to each element of the row. It calls the random method of the random module.
        # which returns a float from 0 to 1. if this number is bigger than the PROBABILITY OF BEING DEAD, then CellType
        # will be instantiated as alive. Otherwise, CellType is instantiated as Dead.

        self.matrix = [list(map(lambda x: CellType(True) if random() > probability else CellType(False), row)) for row in
                       self.matrix]

# TODO: CellType check decorator cos I need it everywhere
