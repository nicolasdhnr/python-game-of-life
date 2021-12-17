import cProfile
import io
import os
import pstats

import psutil
import unittest

import cellsim_log


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


# ===============================================Tissue Test=====================================================
print("==========Generating a matrix ==========")

tissue = cellsim_log.Tissue()
print(tissue.matrix)
print(tissue.rows == len(tissue.matrix))
print(tissue.cols == len(tissue.matrix[0]))
print(tissue.CellType)

print("========== String Method ==========")
tissue = cellsim_log.Tissue(1000, 1000,cellsim_log.Cell)
tissue = str(tissue)


print("========== Getter and Setter ==========")
tissue = cellsim_log.Tissue(6,3,cellsim_log.Cell)
tissue[2][0] = cellsim_log.Cell(True)
tissue[2][1] = cellsim_log.Cell(False)
tissue[2][2] = cellsim_log.Cell(True)
print(tissue)
print(tissue[2][0])
print(tissue[2][1])
print(tissue[2][2])
tissue[4] = [cellsim_log.Cell(True), cellsim_log.Cell(True),cellsim_log.Cell(True)]
print(tissue)

print("========== Seed From Matrix ==========")

tissue = cellsim_log.Tissue(10, 40, cellsim_log.Cell)
test_matrix = [[cellsim_log.Cell(False) for i in range(1000)] for j in range(1000)]

test_matrix[5][5] = cellsim_log.Cell(True)
test_matrix[5][6] = cellsim_log.Cell(True)
test_matrix[5][7] = cellsim_log.Cell(True)
tissue.seed_from_matrix(test_matrix)
print(tissue.alive_cells)


#
# tissue = cellsim.Tissue(10, 40, cellsim.Cell)
# tissue.seed_from_file('tt1.txt', cellsim.Cell)
# print(tissue)
#
# # tissue = cellsim.Tissue(1000,4000)
# tissue.seed_random(0.5, cellsim.Cell)
# # print(tissue)

tissue = cellsim_log.Tissue(1000, 1000)

tissue.seed_random(0.5, cellsim_log.Cell)
# print(tissue.cells_of_interest)


for i in range(5):
    # os.system('clear') #will be os.system('cls')
    tissue.next_state()
    # print(tissue)


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
