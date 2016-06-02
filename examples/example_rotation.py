#!/usr/bin/env/ python
import binpacking
import numpy as np
import matplotlib.pyplot as plt


# items
item_width  = [20,50,40,40,5,30]
item_height = [50,40,20,40,60,30]
item_allow_rotation=[False]*len(item_width)

# bin types
bin_width  = [60]
bin_height = [120]
bin_cost   = [1]

# do not allow rotation
(bins,cost) = binpacking.solve_binpacking(item_width,
										  item_height,
										  item_allow_rotation,
										  bin_width,bin_height,
										  bin_cost,
										  solver='cplex')
	  
binpacking.plot_binpacking(bins)


# allow rotation
item_allow_rotation=[True]*len(item_width)
(bins,cost) = binpacking.solve_binpacking(item_width,
										  item_height,
										  item_allow_rotation,
										  bin_width,bin_height,
										  bin_cost,
										  solver='cplex')
 
binpacking.plot_binpacking(bins)

plt.show()