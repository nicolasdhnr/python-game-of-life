import os
import cellsim
import time

tissue = cellsim.Tissue(10,40)
tissue.seed_random(0.5,cellsim.Cancer)
print(tissue)
for i in range(0,100):
    os.system('clear') #will be os.system('cls')
    tissue.next_state()
    print(tissue)
    time.sleep(0.1)
