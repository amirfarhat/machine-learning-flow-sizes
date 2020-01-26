import time as pytime
import timeit
import numpy as np

# def my_func():
# 	print('doing')
# 	pytime.sleep(0.5)
# 	return 5

# def runner_func():
# 	print(pytime.time())
# 	my_func()
# 	print(pytime.time())

# time = timeit.timeit(runner_func, number=10)
# print(time)


x = [1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0]
OldMax = max(x)
OldMin = min(x)
OldRange = (OldMax - OldMin)  

NewMin = 0
NewMax = 1
NewRange = (NewMax - NewMin)  

new = []
for v in x:
	new_v = (((v - OldMin) * NewRange) / OldRange) + NewMin
	new.append(new_v)

print(new)
