from random import random

# ===============================================Start of Code=====================================================

class Cell:
    """ CellType to be added to Tissue matrix (defined below).
    The state of the Cell is determined by its number of living neighbours in the matrix.
    The set of rules it obeys depending on the neughbour count are as follows:
        Cell dies if it has four or more alive neighbours.

    """

    def __init__(self, alive=False):
        # TODO: Error Handling
        self.alive = alive
        self._marker = "O"

    def is_alive(self):
        return self.alive

    def __str__(self):
        if self.alive:
            return self._marker
        else:
            return "."

    @property
    def rule_set(self):
        return {0: False, 1: False, 2: self.alive, 3: True, 4: False, 5: False, 6: False, 7: False, 8: False}

    def update_cell(self, surroundings):
        alive_cells = sum(1 for row in surroundings for elem in row if elem.alive)
        # Above function does not ignore the center element so:
        if self.alive:
            alive_cells -= 1

        self.alive = self.rule_set[alive_cells]


class Cancer(Cell):
    def __init__(self, alive=False):
        super().__init__(alive)
        self._marker = "X"

    @property
    def rule_set(self):
        return {0: False, 1: False, 2: self.alive, 3: True, 4: self.alive, 5: False, 6: False, 7: False, 8: False}


class Tissue:
    """Represents the space in which the cell grows.
        Attributes:
            row (int): Number of rows
            cols (int): Number of col
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

        # Find the rules of the Cell:
        self.ruleset = {}  # Will be used to contain a tuple as a key and
        self._death = set()
        self._stasis = set()
        self._revive = set()

    # ====================== Creating a Dictionary of rules for each CellType =================================
    def get_rule_set(self):
        """ Updates the attributes "self.ruleset" with the outputs of the cell.alive. The structure of the dictionary
        generated is the following {key: value}
        - key (tuple = (int, bool)): The first element (int) is the number of neighbours of the cell.}
                                    The second element (Bool) contains the current state of the cell (alive or dead)

        - value (Boolean) : How the cell should be updated given its current surroundings.

        The ruleset dictionary will be used to update the state of the cell.

        """
        alive_cell = self.CellType(True)
        dead_cell = self.CellType(False)

        # Generates 18 3x3 matrices to encompass all the possibilities for the surroundings of the cell.
        # Store the outputs of the update_cell method given these surroundings in the ruleset dictionary.

        for state in (True, False):
            for living_neighbours in range(0, 9):
                neighbour_count = 0
                test_matrix = []  # The matrix to be inputted into update_cell of the CellType.
                for i in range(3):
                    test_matrix.append([])
                    for j in range(3):
                        if neighbour_count < living_neighbours:
                            test_matrix[i].append(alive_cell)
                            neighbour_count += 1
                        else:
                            test_matrix[i].append(dead_cell)

                # Assign the center element to be a dead or alive Cell depending on state:
                test_matrix[1][1] = self.CellType(state)
                center_element = test_matrix[1][1]
                center_element.update_cell(test_matrix)
                self.ruleset[(neighbour_count, state)] = center_element.alive

                # Sort the dictionary to access its values slightly faster.
                self.ruleset = {key: self.ruleset[key] for key in sorted(self.ruleset.keys(), key=lambda ele: ele[0])}

    def find_pattern(self):
        """ Updates self._stasis, self._death, self._revive.

        Each cell in the tissue can only react to its surroundings in one of three ways:
        Stasis, Death and Revival. Given the information contained in the ruleset, this function deduces what number
        of neighbours yields each of these states, and updates the corresponding sets
        (self._stasis, self._death, self._revive)
        """

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
        """ Clears all the instance attributes before seeding"""
        # reset the attributes
        self.matrix = []
        self.rows = 0
        self.cols = 0
        self.CellType = Cell

        # reset the attributes associated to the ruleset
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

    def seed_from_matrix(self, seed_matrix):
        """ Overwrites the four attribute variables given an input seed_matrix.

        Arguments:
            seed_matrix (list): Nested list 2D array containing Cell of objects.

        """

        self.clear_attributes()

        self.CellType = seed_matrix[0][0].__class__

        self.get_rule_set()
        self.find_pattern()

        self.rows = len(seed_matrix)
        self.cols = len(seed_matrix[0])

        for index, row in enumerate(seed_matrix):
            self.matrix += [
                list(tuple(row))]  # This is to circumvent using deepcopy. Generates a new object that will not
            # alter seed matrix.

            for j in range(self.rows):
                if row[j].alive:
                    self.alive_cells.add((index, j))

    def seed_from_file(self, filename, CellType=Cell):
        """Given an input filename, reads from corresponding file and creates a matrix of cell objects.

        File must only contain "." and another character of choice.
        Arguments:
            Filename (string) - Name of file to be found or relative path. 
        """

        self.clear_attributes()

        self.CellType = CellType

        self.get_rule_set()
        self.find_pattern()

        try:
            with open(filename, "r", encoding="utf-8") as f:
                file_lines = f.readlines()
                for row_index, row in enumerate(file_lines):
                    # Every time "." is encountered, assign a dead cell to that location in the matrix.
                    self.matrix += [
                        list(map(lambda x: self.CellType(False) if x == "." else self.CellType(True),
                                 row.replace("\n", "")))]

                    # Look through the matrix and add the coordinates of alive cells as tuples.
                    for col_index in range(int(len(row)) - 1):
                        if self.matrix[row_index][col_index].alive:
                            self.alive_cells.add((row_index, col_index))

            self.rows = len(self.matrix)
            self.cols = len(self.matrix[0])

        except IOError:
            pass



    def seed_random(self, probability, CellType):
        """ Updates the matrix with dead or alive cells pseudo-randomly, according to confluency.

        Arguments:

        """

        self.clear_attributes()
        self.CellType = CellType
        self.get_rule_set()
        self.find_pattern()

        for i in range(self.rows):
            for j in range(self.cols):
                if random() < probability:
                    self.matrix[i][j] = CellType(True)
                    self.alive_cells.add((i, j))

                else:
                    self.matrix[i][j] = CellType(False)

        self.rows = len(self.matrix)
        self.cols = len(self.matrix[0])

    def get_neighbours(self, r, c):

        if 0 < r < self.rows:
            ri = (0, -1, 1)  # Center of grid
        elif r > 0:
            ri = (0, -1)  # Selects the last row, so can only find neighbours around.
        else:
            ri = (0, 1)
        ci = (0, -1, 1) if 0 < c < self.cols else ((0, -1) if c > 0 else (0, 1))
        a = [[r + i, c + j] for i in ri for j in ci if not i == j == 0]
        return a

    @staticmethod
    def alive_neighbour_count(list_of_neighbours, alive_cells_copy):
        neighbours_set = set([tuple(x) for x in list_of_neighbours])
        neighbour_count = len(neighbours_set.intersection(alive_cells_copy))
        return neighbour_count

    def update_element(self, row, col, count):
        state1 = self.matrix[row][col].alive
        cell = self.matrix[row][col]
        cell.alive = self.ruleset[(count, state1)]
        state2 = cell.alive
        diff = (state2 != state1)
        if diff:
            if state2:
                self.alive_cells.add((row, col))

            else:
                self.alive_cells.discard((row, col))

    @time_profile
    def next_state(self):
        """
        :
        """
        alive_cells_copy = self.alive_cells.copy()

        # This handles all the edges of the Tissue matrix
        for row in range(0, self.rows, self.rows - 1):
            for col in range(1, self.cols - 1):
                neighbours = self.get_neighbours(row, col)
                count = self.alive_neighbour_count(neighbours, alive_cells_copy)
                self.update_element(row, col, count)

        # This handles the top and bottom row of the tissue matrix
        for row in range(0, self.rows):
            for col in range(0, self.cols, self.cols - 1):
                neighbours = self.get_neighbours(row, col)
                count = self.alive_neighbour_count(neighbours, alive_cells_copy)
                self.update_element(row, col, count)

        # Update the "main body"
        for row in range(1, self.rows - 1):
            neighbours = self.get_neighbours(row, 1)

            for col in range(1, self.cols - 1):
                cell = self.matrix[row][col]
                state1 = cell.alive
                count = len(set([tuple(x) for x in neighbours]).intersection(alive_cells_copy))

                for neighbour in neighbours:
                    neighbour[1] += 1

                # Define conditions to skip:
                if count in self._stasis:
                    continue
                elif not state1 and count in self._death:
                    continue
                elif state1 and count in self._revive:
                    continue

                else:
                    self.update_element(row, col, count)