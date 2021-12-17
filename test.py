def seed_from_matrix(seed_matrix):  # Should this be a class method?
    """ Overwrite the four attribute variables using a single argument.
        :param seed_matrix:
        """
    alive_cells = set()
    matrix = []
    rows = len(seed_matrix)
    cols = len(seed_matrix[0])
    for index, row in enumerate(seed_matrix):
        matrix += [list(tuple(row))]
        print(matrix)
        for j in range(rows):
            if row[j] == 1:
                alive_cells.add((index, j))
    cols = len(matrix)
    rows = len(matrix[0])
    return matrix


seed_matrix = [[1, 2, 3], [1, 2, 5]]
copy = seed_from_matrix(seed_matrix)
copy[1] = 0
print(seed_matrix)
print(copy)

