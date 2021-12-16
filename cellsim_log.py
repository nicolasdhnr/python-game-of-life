import copy
import os
import time
import psutil
import cProfile, pstats, io

# TODO: DON'T IMPORT WHOLE MODULE

#  ====================================Profilers =============================================
# Time profiler
import temp as temp


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
        # TODO: Error Handling
        self.alive = alive

    def is_alive(self):
        return self.alive

    def __str__(self):
        if self.is_alive():
            return "O"
        else:
            return "."

    @property
    def rule_set(self):
        return {0: False, 1: False, 2: self.is_alive(), 3: True, 4: False, 5: False, 6: False, 7: False, 8: False}

    def change_element(self, state):
        self.alive = state

    def update_cell(self, surroundings):
        alive_cells = sum(1 for row in surroundings for elem in row if elem.is_alive())
        # print(self.rule_set.get(alive_cells))
        self.alive = self.rule_set[alive_cells]


# TODO: add this function


class Cancer(Cell):
    def __init__(self, alive=False):
        super().__init__(alive)


# TODO: Add this function


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
        # if issubclass(CellType, object) and all(
        #        hasattr(CellType, attr) for attr in ["alive", "is_alive", "update_cell"]) \
        #       and callable(hasattr(["is_alive",
        #                  "update_cell"])):  # TODO: This should be its own decorator. How do iI get this to check at each function where CellType is called, but ONLY ONCE.
        self.CellType = CellType
        # else:
        #     self.CellType = Cell

        self.matrix = [[CellType() for _ in range(self.cols)] for _ in range(self.rows)]

        @classmethod
        def tuple_matrix(self):
            return tuple(self.matrix)

        self.time_step = 0
        self.alive_cells = set()

    def __str__(self):
        tissue_str = ""
        for row in self.matrix:
            tissue_str += f'{"".join(map(lambda x: self.CellType.__str__(x), row))}\n'  # mtehright not be most efficient way to convert everything
        return tissue_str

    def __getitem__(self, idx):
        """ Defines the getter for the Tissue class"""
        return self.matrix[idx]

    def __setitem__(self, key, value):
        """ Defines the setter for the Tissue class"""
        # TODO: error handling here so you can't add non celltype and maybe not outside the grid
        if value == self.CellType(True):
            self.alive_cells.add()

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
        self.matrix.clear()

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
        # TODO: Override attributes

    # TODO: Change ">" depending on whether it is probability of being alive or dead.
    # TODO: Try opti with for loop or list comprehension

    @staticmethod
    def surroundings(input_matrix, row, column):
        """Takes in the current matrix and returns the surroundings of the Cell"""

        # If the coordinates go higher or lower than self.row or self.column, assign a Dead Cell to that location.
        # Make sure in other sections of the code that these cells than never be brought to life.
        # Make sure that custom functions can't bring them to life either and mess everything up.
        return [
            [input_matrix[i][j] if (0 < i < self.rows - 1 and 0 < j < self.cols - 1 and i != j) else self.CellType(
                False) for i in
             range(row - 1, row + 2)] for j in range(column - 1, column + 2)]

    @staticmethod
    def get_neighbours(r, c):
        rng_r = range(r - 1, r + 2)
        rng_c = range(c - 1, c + 2)
        a = [(i, j) for i in rng_r for j in rng_c]  # TODO might be faster if i define static method
        del a[5] # 5th element is always (c, r). Also del is faster than .remove
        return set(a)

    @time_profile
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

        # Maintain set of alive cells straight from the seed.
        # Update the border

        # Update the rows
        for i, row in enumerate(self.matrix):
            for j, status in enumerate(row):  # TODO: Am I taking negative indexes?
                if random() > probability:
                    self.matrix[i][j] = CellType(True)
                    self.alive_cells.add((i, j))

                else:
                    self.matrix[i][j] = CellType(False)

        # self.matrix = [list(map(lambda x: CellType(True) if random() > probability else CellType(False), row)) for row in self.matrix] - This is 3 times faster than above...
        self.rows = len(self.matrix)
        self.cols = len(self.matrix[0])

    @time_profile
    @space_profile
    def next_state(self):
        # Store alive cells in a set.
        # Class property is set of alive cells but only called once.
        # Boundary condition is dead cells.
        # Set of alive. Each new turn del. based on rule set of cell; Set an attribute in each cell that returns a flag if one
        # Interpret booleans as an int with astype.

        # We want to create a "Fake outline" of dead cells for the grid,
        # to avoid having to isolate the columns with if statements.
        # Dead cells on the outline will all be the same object to avoid extra space consumption and time to instantiate:

        # dead_cell = self.CellType(False)
        # outline_row = [dead_cell] * (self.cols + 2)
        # temp_str = str(self).split("\n")

        # TODO: gets fucked up as states go on

        # tmp_matrix = [[self.CellType(False) if x == "." else self.CellType(True) for x in elem] for elem in temp_str]
        # Add row
        # tmp_matrix = [outline_row] + [[dead_cell] + row + [dead_cell] for row in tmp_matrix] + [outline_row] # TODO: Need to fix the neighbourr problem cos they are prolly fcked up rn
        alive_cells_copy = self.alive_cells.copy()

        # TODO: Try with map, try to replace double for loop.
        # Linearly search the cells. Is it faster to generate the coordinates before maybe... # TODO: Try this
        for row in range(1, self.rows - 1):
            for col in range(1, self.cols - 1):
                element = self.matrix[row][col]
                state1 = element.alive
                neighbours = self.get_neighbours(row, col) #TODO: This is not gonna work...
                count = len(neighbours.intersection(self.alive_cells))

                if not state1 and (count == 0): # TODO: is this a good assumption to make
                    continue

                # if self.CellType == Cell or self.CellType == Cancer and count == 3:
                #     continue
                else:
                    element.alive = element.rule_set[count]
                    state2 = element.alive
                    diff = (state2 != state1)
                    if diff:
                        if state2:
                            self.alive_cells.add((row, col))

                        else:
                            self.alive_cells.discard((row, col))

        # instead of recreating update tmp matrix with changes

        # self.time_step += 1

        # set de toutes les cellules vivantes et leurs neighbours - a chaque iteration, rajouter les cellules qui ont change de state au set (comment track)

        # TODO: CellType check decorator cos I need it everywhere

        # Idea 1 : matrix check for each neighbour -> time out .
        # Idea 2: check is neighbours of neighbours are in the set. If not continue.
