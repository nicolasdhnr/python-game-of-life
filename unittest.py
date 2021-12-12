import cellsim
import os
import time
import psutil
import cProfile, pstats, io


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


print("==========Tissue==========")

tissue = cellsim.Tissue()
print(tissue.matrix)
print(tissue.rows)
print(tissue.cols)
print(tissue.CellType)


tissue = cellsim.Tissue(10,40,cellsim.Cell)
test_matrix = list()
for i in range(10):
    test_matrix.append([])
    for j in range(40):
        test_matrix[i].append(cellsim.Cell(False))
print(test_matrix)

test_matrix[5][5] = cellsim.Cell(True)
test_matrix[5][6] = cellsim.Cell(True)
test_matrix[5][7] = cellsim.Cell(True)
tissue.seed_from_matrix(test_matrix)
print(tissue)
print(test_matrix[5][6])

tissue = cellsim.Tissue(10, 40, cellsim.Cell)
tissue.seed_from_file('tt1.txt', cellsim.Cell)
print(tissue)

# tissue = cellsim.Tissue(1000,4000)
tissue.seed_random(0.5, cellsim.Cell)
# print(tissue)

tissue = cellsim.Tissue(10,40)
tissue.seed_random(0.5,cellsim.Cell)
print(tissue)
for i in range(0,100):
    os.system('clear') #will be os.system('cls')
    tissue.next_state()
    print(tissue)
    time.sleep(0.1)
