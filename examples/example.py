#!/usr/bin/env/ python

import binpacking
import numpy as np
import matplotlib.pyplot as plt


# items
n = 20
item_width  = [20,20,30,18,18, 5, 5,20,16]
item_height = [50,50,50,48,48,26,26,30,28]

# bin types
bin_width  = [60]
bin_height = [120]
bin_cost   = [1]
leftover_height_cost   = [-0.1]
leftover_width_cost   = [-0.5]

# do not allow rotation
(bins,cost) = binpacking.solve_binpacking(item_width,item_height,bin_width,bin_height,bin_cost=bin_cost,leftover_width_cost=leftover_width_cost,leftover_height_cost=leftover_height_cost,allow_rotation=[False]*n)
binpacking.plot_binpacking(bins)

plt.show()