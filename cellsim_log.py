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
        print("Measuring", fnc.__name__, "time...")
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
        if self.alive:
            return "O"
        else:
            return "."

    @property
    def rule_set(self):
        return {0: False, 1: False, 2: self.alive, 3: True, 4: False, 5: False, 6: False, 7: False, 8: False}

    def change_element(self, state):
        self.alive = state

    def update_cell(self, surroundings):
        alive_cells = sum(1 for row in surroundings for elem in row if elem.alive)
        # Above function does not ignore the center element so:
        if self.alive:
            alive_cells -= 1

        self.alive = self.rule_set[alive_cells]


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

        self.rows = rows
        self.cols = cols

        # CellType Error Checking
        if issubclass(CellType, Cell):
            self.CellType = CellType
        # If the CellType is not a subclass of cell, checks if the CellType is a user defined class (subclass object) and
        # has the required functions and attributes.
        elif issubclass(CellType, object) \
                and all(hasattr(CellType, attr) for attr in ["alive", "is_alive", "update_cell"]) \
                and callable(hasattr(CellType, attr) for attr in ["is_alive", "update_cell"]):
            self.CellType = CellType
        else:
            self.CellType = Cell

        self.matrix = [[CellType() for _ in range(self.cols)] for _ in range(self.rows)]
        self.alive_cells = set()  # Stores the coordinates of alive cells

        # Define whether the assumptions used in "next_state()" will hold:

        # Find the rules of the Cell:
        self.ruleset = {}
        self._death = set()
        self._stasis = set()
        self._backtolife = set()

    def get_rule_set(self):
        alive_cell = self.CellType(True)  # I define only one alive cell and one dead cell for the neighbours of these
        dead_cell = self.CellType(False)
        self.ruleset = {}
        for state in (True, False):
            for living_neighbours in range(0, 9):
                neighbour_count = 0
                test_case_list = []
                for i in range(3):
                    test_case_list.append([])
                    for j in range(3):
                        if neighbour_count < living_neighbours:
                            test_case_list[i].append(alive_cell)
                            neighbour_count += 1
                        else:
                            test_case_list[i].append(dead_cell)

                # Assign the center element to be a dead or alive Cell depending on state:
                test_case_list[1][1] = self.CellType(state)
                center_element = test_case_list[1][1]
                center_element.update_cell(test_case_list)
                self.ruleset[(neighbour_count, state)] = center_element.alive
                self.ruleset = {key: self.ruleset[key] for key in sorted(self.ruleset.keys(), key=lambda ele: ele[0])}

    def find_pattern(self):
        cases = [self._death, self._backtolife, self._stasis]
        for elem in cases:  # Clear all the previous sets.
            elem.clear()

        for i in range(9):
            alive_case = self.ruleset[(i, True)]
            dead_case = self.ruleset[(i, False)]

            if alive_case == True and dead_case == False:
                self._stasis.add(i)
            elif alive_case == True and dead_case == True:
                self._backtolife.add(i)
            elif alive_case == False and dead_case == False:
                self._death.add(i)
            else:
                continue  # One more possibility but we don't want to store it.

    @staticmethod
    def clear_rules(self):
        pass

    def __str__(self):
        return "\n".join(["".join([str(x) for x in row]) for row in self.matrix])

    def __getitem__(self, idx):
        """ Defines the getter for the Tissue class"""
        return self.matrix[idx]

    def __setitem__(self, key, value):
        """ Defines the setter for the Tissue class"""
        try:
            if len(value) == len(self.matrix[key]):
                self.matrix[key] = value

        except IndexError:
            pass

    @time_profile
    def seed_from_matrix(self, seed_matrix):  # Should this be a class method?
        """ Overwrite the four attribute variables using a single argument.
        :param seed_matrix:
        """
        self.matrix = []
        self.alive_cells = set()
        self.rows = len(seed_matrix)
        self.cols = len(seed_matrix[0])
        for index, row in enumerate(seed_matrix):
            self.matrix += [list(tuple(row))]
            for j in range(self.rows):
                if row[j].alive:
                    self.alive_cells.add((index, j))

    @time_profile
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

    def get_neighbours(self, r, c):
        if 0 < r < self.rows - 1:
            ri = (0, -1, 1)  # Center of grid
        elif r > 0:
            ri = (0, -1)  # Selects the last row, so can only find neighbours around.
        else:
            ri = (0, 1)
        ci = (0, -1, 1) if 0 < c < self.rows - 1 else ((0, -1) if c > 0 else (0, 1))
        a = [(r + i, c + j) for i in ri for j in ci if not i == j == 0]
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
        self.get_rule_set()
        self.find_pattern()
        # Maintain set of alive cells straight from the seed.
        row_rng = range(self.rows)

        # Update the border

       

        for i in range(self.rows):  # use map instead
            for j in range(self.cols):
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

        # Linearly search the cells. Is it faster to generate the coordinates before maybe... # TODO: Try this

        main_body_range = range(1, self.rows - 1)

        for row in range(self.rows):
            for col in range(self.cols):
                element = self.matrix[row][col]
                state1 = element.alive
                neighbours = self.get_neighbours(row, col)  # TODO: This is not gonna work...
                count = len(neighbours.intersection(alive_cells_copy))

                # Define conditions to skip:
                if count in self._stasis:
                    continue
                # elif not state1 and count in self._death:
                #     continue
                # elif state1 and count in self._backtolife:
                #     continue

                else:
                    element.alive = self.ruleset[(count, state1)]
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
