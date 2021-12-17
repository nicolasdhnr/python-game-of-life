import copy
import os
import time
import psutil
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
    overpopulation = 4
    rule_set = {0: False,1: False,2: 0 ,3: True,4: False,5: False,6: False,7:False,8:False}

    def __init__(self, alive=False):
        # Error Handling
        self.alive = alive

    def __str__(self):
        if self.alive:
            return "O"
        else:
            return "."

    def is_alive(self):
        return self.alive

    def update_cell(self, surroundings):
        alive_cells = sum(1 for row in surroundings for elem in row if elem.is_alive() == True)
        # print(alive_cells)
        # print(self.rule_set.get(alive_cells))
        if self.rule_set.get(alive_cells) != 0:
            self.alive = self.rule_set.get(alive_cells)


# TODO: add this function


class Cancer(Cell):
    def __init__(self, alive=False):
        super().__init__(alive)


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

    def __init__(self, rows=1, cols=1, CellType=Cell):

        self.rows = rows  # TODO: Make this a property - need it to update iff matrix is changed
        self.cols = cols

        # CellType should be a "new-style class" that is, user-defined. Object is the default superclass -> Good check to have that the class is user defined and we are not trying to pass"int"
        # https://stackoverflow.com/questions/54867/what-is-the-difference-between-old-style-and-new-style-classes-in-python

        # Then we need to check if CellType has all the attributes of a Cell necessary to make it work.
        if issubclass(CellType, object) and all(
                hasattr(CellType, attr) for attr in ["alive", "is_alive", "update_cell"]) \
                and callable(hasattr(["is_alive",
                                      "update_cell"])):  # TODO: This should be its own decorator. How do iI get this to check at each function where CellType is called, but ONLY ONCE.
            self.CellType = CellType
        else:
            self.CellType = Cell

        self.matrix = [[CellType() for _ in range(self.cols)] for _ in range(self.rows)]

    # @property
    # def matrix(self):
    #     return self._matrix
    #
    # @matrix.setter
    # def matrix(self, val):
    #     self._matrix = val

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
        #TODO: update rows and columns (make a decorator)

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
        self.CellType = CellType
        self.matrix = [list(map(lambda x: CellType(True) if random() > probability else CellType(False), row)) for row
                       in
                       self.matrix]
        self.rows = len(self.matrix[0])
        self.cols = len(self.matrix)

    def next_state(self):
        def surroundings(input_matrix, row, column):
            """Takes in the current matrix and returns the surroundings of the Cell"""

            # If the coordinates go higher or lower than self.row or self.column, assign a Dead Cell to that location.
            # Make sure in other sections of the code that these cells than never be brought to life.
            # Make sure that custom functions can't bring them to life either and mess everything up.
            def edge_detection(edge, param):
                if edge == 0 or edge == param:
                    return True
                else:
                    return False

            row_edge = edge_detection(row, self.rows - 1)
            column_edge = edge_detection(column, self.cols - 1)
            return [
                [self.CellType(False) if (row_edge and row_idx == row - 1 or column_idx == column - 1 and column_edge
                                          or row_idx == row and column_idx == column)  # Ignoring middle element
                 else input_matrix[column][row] for row_idx in range(row - 1, row + 2)]
                for column_idx in range(column - 1, column + 2)]  # Improve readability

        new_matrix = copy.deepcopy(self.matrix)
        for i in range(self.cols):
            # I really don't want to do this - should set an attribute alive cells and only search through them but yeah.
            for j in range(self.rows):
                print(surroundings(self.matrix, j, i))
                self.matrix[i][j].update_cell(surroundings=surroundings(self.matrix, j, i))


# TODO: CellType check decorator cos I need it everywhere
