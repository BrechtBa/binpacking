#!/usr/bin/env/ python
import binpacking
import numpy as np
import matplotlib.pyplot as plt


# items
item_width  = [20,50,30,40,5,30]
item_height = [50,50,20,40,60,30]
item_allow_rotation=[False]*len(item_width)

# bin types
bin_width  = [60]
bin_height = [120]
bin_cost   = [1]
bin_cost_leftover_width   = [-0.01]
bin_cost_leftover_height   = [-0.02]


# solve using cplex
(bins,cost) = binpacking.solve_binpacking(item_width,
										  item_height,
										  item_allow_rotation,
										  bin_width,bin_height,
										  bin_cost,
										  bin_cost_leftover_width,
										  bin_cost_leftover_height,
										  solver='cplex')
	  
binpacking.plot_binpacking(bins)


# solve using glpk
(bins,cost) = binpacking.solve_binpacking(item_width,
										  item_height,
										  item_allow_rotation,
										  bin_width,bin_height,
										  bin_cost,
										  bin_cost_leftover_width,
										  bin_cost_leftover_height,
										  solver='glpk',
										  options={'mipgap':0.5})
	  
binpacking.plot_binpacking(bins)

plt.show()