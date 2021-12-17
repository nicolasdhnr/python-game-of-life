import os
import psutil
import cProfile, pstats, io
from random import random


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
        self._revive = set()

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
        cases = [self._death, self._revive, self._stasis]
        for elem in cases:  # Clear all the previous sets.
            elem.clear()

        for i in range(9):
            alive_case = self.ruleset[(i, True)]
            dead_case = self.ruleset[(i, False)]

            if alive_case == True and dead_case == False:
                self._stasis.add(i)
            elif alive_case == True and dead_case == True:
                self._revive.add(i)
            elif alive_case == False and dead_case == False:
                self._death.add(i)
            else:
                continue  # One more possibility but we don't want to store it.

    def clear_attributes(self):
        # reset the attributes
        self.matrix = []
        self.rows = 0
        self.cols = 0
        self.CellType = Cell

        # reset the rule_set
        self.ruleset = {}
        self._death = set()
        self._stasis = set()
        self._revive = set()

        # Reset the alive cells:
        self.alive_cells = set()

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
    def seed_from_matrix(self, seed_matrix):
        """ Overwrite the four attribute variables using a single argument.

        :param seed_matrix:
        """

        self.clear_attributes()
        self.get_rule_set()
        self.find_pattern()

        self.rows = len(seed_matrix)
        self.cols = len(seed_matrix[0])
        for index, row in enumerate(seed_matrix):
            self.matrix += [list(tuple(row))]
            for j in range(self.rows):
                if row[j].alive:
                    self.alive_cells.add((index, j))

    @time_profile
    def seed_from_file(self, filename, CellType=Cell):
        """ This function takes a filename and CellType as input and changes the "self.matrix" attribute to seed.

        """

        self.clear_attributes()
        self.get_rule_set()
        self.find_pattern()

        if ".txt" not in filename:
            self.matrix = []
        else:
            try:
                with open(filename, "r", encoding="utf-8") as f:  # TODO: Add support for different paths.
                    file_lines = f.readlines()
                    for row_index, row in enumerate(file_lines):
                        self.matrix += [
                            list(map(lambda x: CellType(False) if x == "." else CellType(True), row.replace("\n", "")))]
                        for col_index in range(int(len(row)) - 1):
                            if self.matrix[row_index][col_index]:
                                self.alive_cells.add((row_index, col_index))

                self.rows = len(self.matrix)
                self.cols = len(self.matrix[0])

            except IOError:
                pass

        # TODO: Override attributes

    # TODO: Change ">" depending on whether it is probability of being alive or dead.

    @time_profile
    def seed_random(self, probability, CellType):
        # We want to avoid having to call __init__ at each iteration of the coming loop so we define the two possible states

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

        self.rows = len(self.matrix)
        self.cols = len(self.matrix[0])

    def get_neighbours(self, r, c):

        if 0 < r < self.rows - 1:
            ri = (0, -1, 1)  # Center of grid
        elif r > 0:
            ri = (0, -1)  # Selects the last row, so can only find neighbours around.
        else:
            ri = (0, 1)
        ci = (0, -1, 1) if 0 < c < self.rows - 1 else ((0, -1) if c > 0 else (0, 1))
        a = [[r + i, c + j] for i in ri for j in ci if not i == j == 0]
        return a

    @staticmethod
    def alive_neighbour_count(list_of_neighbours, alive_cells_copy):
        neighbours_set = set([tuple(x) for x in list_of_neighbours])
        neighbour_count = len(neighbours_set.intersection(alive_cells_copy))
        return neighbour_count

    def update_element(self, row, col, count):
        state1 = self.matrix[row][col].alive
        self.matrix[row][col].alive = self.ruleset[(count, state1)]

    @time_profile
    @space_profile
    def next_state(self):
        """
        :
        """
        alive_cells_copy = self.alive_cells.copy()

        # This handles all the edges of the Tissue matrix
        for row in range(0, self.rows, self.rows - 1):
            for col in range(0, self.cols, self.cols - 1):
                neighbours = self.get_neighbours(row, col)
                count = self.alive_neighbour_count(neighbours, alive_cells_copy)
                self.update_element(row, col, count)

        # Update the "main body"
        neighbours = self.get_neighbours(1, 1)
        for row in range(1, self.rows - 1):
            for neighbour in neighbours:
                neighbour[0] += 1

            for col in range(1, self.cols - 1):
                cell = self.matrix[row][col]
                state1 = cell.alive
                count = len(set([tuple(x) for x in neighbours]).intersection(alive_cells_copy))

                # Define conditions to skip:
                if count in self._stasis:
                    continue
                elif not state1 and count in self._death:
                    continue
                elif state1 and count in self._revive:
                    continue

                else:
                    cell.alive = self.ruleset[(count, state1)]
                    state2 = cell.alive
                    diff = (state2 != state1)
                    if diff:
                        if state2:
                            self.alive_cells.add((row, col))

                        else:
                            self.alive_cells.discard((row, col))
            for neighbour in neighbours:
                neighbour[1] += 1
