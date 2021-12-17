import cProfile
import io
import os
import pstats

import psutil
import unittest

import cellsim


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

tissue = cellsim.Tissue()
print(tissue.matrix)
print(tissue.rows == len(tissue.matrix))
print(tissue.cols == len(tissue.matrix[0]))
print(tissue.CellType)

print("========== String Method ==========")
tissue = cellsim.Tissue(1000, 1000, cellsim.Cell)
tissue = str(tissue)

print("========== Getter and Setter ==========")
tissue = cellsim.Tissue(6, 3, cellsim.Cell)
tissue[2][0] = cellsim.Cell(True)
tissue[2][1] = cellsim.Cell(False)
tissue[2][2] = cellsim.Cell(True)
print(tissue)
print(tissue[2][0])
print(tissue[2][1])
print(tissue[2][2])
tissue[4] = [cellsim.Cell(True), cellsim.Cell(True), cellsim.Cell(True)]
print(tissue)
#
print("========== Seed From Matrix ==========")

tissue = cellsim.Tissue(10, 40, cellsim.Cell)
test_matrix = [[cellsim.Cell(False) for i in range(10)] for j in range(10)]

test_matrix[5][5] = cellsim.Cell(True)
test_matrix[5][6] = cellsim.Cell(True)
test_matrix[5][7] = cellsim.Cell(True)
tissue.seed_from_matrix(test_matrix)
print(tissue)
print(tissue.alive_cells)
#
print("========== Seed From File ==========")

tissue = cellsim.Tissue(10, 40, cellsim.Cancer)
tissue.seed_from_file('tt1.txt', cellsim.Cancer)
print("Alive cells in this tissue", tissue.alive_cells)
print(tissue)
tissue.next_state()
print(tissue)

#
#
print("========== Seed Random==========")
tissue = cellsim.Tissue(10, 10)
tissue.seed_random(0.5, cellsim.Cell)

# Check confluency
print("Confluency is working properly: ", len(tissue.alive_cells) in range(45, 55))

print("========== Next state==========")
print("=== Output Test ===")
input_test = cellsim.Tissue(10, 40, cellsim.Cell)
input_test.seed_from_file('input_test', cellsim.Cell)
print(input_test)
for i in range(100):
    print("time step", i)
    input_test.next_state()
    print(input_test)

print(input_test)

output_test = cellsim.Tissue(10, 40, cellsim.Cell)
output_test = output_test.seed_from_file('output_test.txt', cellsim.Cell)



#
# print("=== BIG INPUT TEST ===")
# tissue = cellsim.Tissue(1000, 1000)
# tissue.seed_random(0.5, cellsim.Cell)
# for i in range(100):
#     # os.system('clear') #will be os.system('cls')
#     tissue.next_state()
#     # print(tissue)
