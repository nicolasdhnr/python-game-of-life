import cellsim_log
import os
import time
import psutil
import cProfile, pstats, io
import copy


# ========== Profilers ==========

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


# print("==========Tissue==========")
#
# tissue = cellsim.Tissue()
# print(tissue.matrix)
# print(tissue.rows)
# print(tissue.cols)
# print(tissue.CellType)
#
#
tissue = cellsim_log.Tissue(10, 40, cellsim_log.Cell)
test_matrix = list()
for i in range(10):
    test_matrix.append([])
    for j in range(40):
        test_matrix[i].append(cellsim_log.Cell(False))
print(test_matrix)

test_matrix[5][5] = cellsim_log.Cell(True)
test_matrix[5][6] = cellsim_log.Cell(True)
test_matrix[5][7] = cellsim_log.Cell(True)
# tissue.seed_from_matrix(test_matrix)
# print(tissue)

#
# tissue = cellsim.Tissue(10, 40, cellsim.Cell)
# tissue.seed_from_file('tt1.txt', cellsim.Cell)
# print(tissue)
#
# # tissue = cellsim.Tissue(1000,4000)
# tissue.seed_random(0.5, cellsim.Cell)
# # print(tissue)

tissue = cellsim_log.Tissue(10, 10)

tissue.seed_random(0.5, cellsim_log.Cell)
# print(tissue.cells_of_interest)


for i in range(6):
    # os.system('clear') #will be os.system('cls')
    tissue.next_state()
    print(tissue)



#     time.sleep(0.1)
# t1 = time.time()
# copy.deepcopy([i for i in range(100)])
# t2 = time.time()
# print(t2 - t1)
#
# t1 = time.time()
# a = [i for i in range(100)]
# b = list(tuple([i for i in range(100)]))
# print(id(a[2]), id(b[2]))

# t2 = time.time()
# print(t2 - t1)
# print(id(a[2]), id(b[2]))
# a[2] = "lmao"
# print(b[2])
# print(id(a[2]), id(b[2]))

def surroundings(input_matrix, row, column):
    """Takes in the current matrix and returns the surroundings of the Cell"""

    # If the coordinates go higher or lower than self.row or self.column, assign a Dead Cell to that location.
    # Make sure in other sections of the code that these cells than never be brought to life.
    # Make sure that custom functions can't bring them to life either and mess everything up.
    return [[input_matrix[i][j] for i in range(row - 1, row + 2)] for j in range(column - 1, column + 2)]


