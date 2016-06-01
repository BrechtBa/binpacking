#!/usr/bin/env/ python

import binpacking
import numpy as np
import matplotlib.pyplot as plt


# items
item_width  = [20,20,30,18,18, 5, 5,20,16]
item_height = [50,50,50,48,48,26,26,30,28]
item_allow_rotation=[False]*len(item_width)

# bin types
bin_width  = [60]
bin_height = [120]
bin_cost   = [1]
bin_cost_leftover_width   = [-0.02]
bin_cost_leftover_height   = [-0.01]


# solve
(bins,cost) = binpacking.solve_binpacking(item_width,
										  item_height,
										  item_allow_rotation,
										  bin_width,bin_height,
										  bin_cost,
										  bin_cost_leftover_width,
										  bin_cost_leftover_height)
	  
binpacking.plot_binpacking(bins)

plt.show()