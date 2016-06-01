#!/usr/bin/env/ python
######################################################################################
#    Copyright 2015 Brecht Baeten
#    This file is part of binpacking.
#
#    binpacking is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    binpacking is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with binpacking.  If not, see <http://www.gnu.org/licenses/>.
######################################################################################

import cplex
import numpy as np
import itertools
import matplotlib.pyplot as plt
import matplotlib.cm
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection


def solve_binpacking(item_width,item_height,bin_width,bin_height,bin_cost=[],leftover_width_cost=[],leftover_height_cost=[],allow_rotation=[],timelimit=20):
	"""
	Solves a bin packing problem with variable bins and variable cost as described in [1]
	An addition is made to specify if an item is allowed to rotate 90deg
	
	Parameters:
	item_width:		list, widths of the items
	item_height:	list, heights of the items
	bin_width:		list, widths of the bin types
	bin_height:		list, heights of the bin types
	bin_cost:		list, [], cost of each bin type
	leftover_width_cost: 	list, [], the cost per unit width of the total width which is left over in each bin. Defaults to -0.5 times the total bin cost divided by the bin width
	leftover_height_cost: 	list, [], the cost per unit height of the total height which is left over in each bin. Defaults to -0.5 times the total bin cost divided by the bin height
	allow_rotation: list, [], True if the item is allowed to rotate 90deg, (unused for now)
	timelimit:		number, 20, the maximum MILP computation time in seconds
	
	Returns:
	bins:	list, a dictionary with properties and items for each used bin

	References:
	[1] D. Pisinger and M. Sigurd, “The two-dimensional bin packing problem with variable bin sizes and costs,” Discret. Optim., vol. 2, no. 2, pp. 154–167, Jun. 2005.
	"""
	
	############################################################################
	# Input handling
	############################################################################
	# items
	w = item_width
	h = item_height
	n = len(w)
	
	if len(allow_rotation)==0:
		r = [0]*n
	else:
		r = [1 if a else 0 for a in allow_rotation]
	
	
	# bins
	W = bin_width
	H = bin_height
	m = len(W)
	
	if len(bin_cost)==0:
		c = [1]*m
	else:
		c = bin_cost
	
	
	if len(leftover_width_cost)==0:
		cwl = [-0.5*ci/Wi for ci,Wi in zip(c,W)]
	else:
		cwl = leftover_width_cost
	
	
	if len(leftover_height_cost)==0:
		chl = [-0.5*ci/Hi for ci,Hi in zip(c,H)]
	else:
		chl = leftover_height_cost
	
		
		
	# convert bins to binary format, each bin can only be used once
	I = range(m)*n
	W = W*n
	H = H*n
	c = c*n
	cwl = cwl*n
	chl = chl*n
	
	# define the milp
	milp = cplex.Cplex()
	
	############################################################################
	# Variables
	############################################################################
	# l[i,j] is 1 if item i is located left of item j
	milp.variables.add(names=['l[{},{}]'.format(i,j) for i in range(n) for j in range(n)],
					   lb=[0 for i in range(n) for j in range(n)],
					   ub=[1 for i in range(n) for j in range(n)],
					   types = ['B' for i in range(n) for j in range(n)]) 

	# b[i,j] is 1 if item i is located below of j
	milp.variables.add(names=['b[{},{}]'.format(i,j) for i in range(n) for j in range(n)],
					   lb=[0 for i in range(n) for j in range(n)],
					   ub=[1 for i in range(n) for j in range(n)],
					   types = ['B' for i in range(n) for j in range(n)])
					   
	# f[i,k] is 1 if item i is located in bin k
	milp.variables.add(names=['f[{},{}]'.format(i,j) for i in range(n) for j in range(n*m)],
					   lb=[0 for i in range(n) for j in range(n*m)],
					   ub=[1 for i in range(n) for j in range(n*m)],
					   types = ['B' for i in range(n) for j in range(n*m)])
					   
	# z[k] is 1 if bin k is used
	milp.variables.add(names=['z[{}]'.format(j) for j in range(n*m)],
					   lb=[0 for j in range(n*m)],
					   ub=[1 for j in range(n*m)],
					   types = ['B' for j in range(n*m)])				   

	# x[i] is x-coordinate of item i				   
	milp.variables.add(names=['x[{}]'.format(i) for i in range(n)],
					   lb=[0 for i in range(n)],
					   types = ['C' for i in range(n)])				   
					   
	# y[i] is y-coordinate of item i				   
	milp.variables.add(names=['y[{}]'.format(i) for i in range(n)],
					   lb=[0 for i in range(n)],
					   types = ['C' for i in range(n)])
	
	# r[i] is 1 if item i is rotated 90deg
	milp.variables.add(names=['r[{}]'.format(i) for i in range(n)],
					   lb=[0 for i in range(n)],
					   ub=[r[i] for i in range(n)],
					   types = ['B' for i in range(n)])
	
	
	# # leftovers
	# # xl[k] is x-coordinate of the leftover in bin k				   
	# milp.variables.add(names=['xl[{}]'.format(k) for k in range(n*m)],
					   # lb=[0 for i in range(n*m)],
					   # ub=[W[k] for k in range(n*m)],
					   # types = ['C' for i in range(n*m)])
					   
	# # yl[k] is y-coordinate of the leftover in bin k				   
	# milp.variables.add(names=['yl[{}]'.format(k) for k in range(n*m)],
					   # lb=[0 for k in range(n*m)],
					   # ub=[H[k] for k in range(n*m)],
					   # types = ['C' for k in range(n*m)])
					   
	# # wl[k] is width of the leftover in bin k				   
	milp.variables.add(names=['lw[{}]'.format(k) for k in range(n*m)],
					   lb=[0 for i in range(n*m)],
					   ub=[W[k] for k in range(n*m)],
					   types = ['C' for i in range(n*m)])
					   
	# # hl[k] is height of the leftover in bin k				   
	milp.variables.add(names=['lh[{}]'.format(k) for k in range(n*m)],
					   lb=[0 for i in range(n*m)],
					   ub=[H[k] for k in range(n*m)],
					   types = ['C' for i in range(n*m)])
		
	# ll[i,k] is 1 if item i is located left of leftover k
	# milp.variables.add(names=['ll[{},{}]'.format(i,k) for i in range(n) for k in range(m*n)],
					   # lb=[0 for i in range(n) for k in range(m*n)],
					   # ub=[1 for i in range(n) for k in range(m*n)],
					   # types = ['B' for i in range(n) for k in range(m*n)]) 

	# # lb[i,k] is 1 if item i is located below of leftover k
	# milp.variables.add(names=['lb[{},{}]'.format(i,k) for i in range(n) for k in range(m*n)],
					   # lb=[0 for i in range(n) for k in range(m*n)],
					   # ub=[1 for i in range(n) for k in range(m*n)],
					   # types = ['B' for i in range(n) for k in range(m*n)])
		
	
	############################################################################				   
	# Constraints	   
	############################################################################
	# no overlap
	for k in range(n*m):
		for j in range(n):
			for i in range(j):
				milp.linear_constraints.add(lin_expr = [[[ 'l[{},{}]'.format(i,j) , 'l[{},{}]'.format(j,i) , 'b[{},{}]'.format(i,j) , 'b[{},{}]'.format(j,i) , 'f[{},{}]'.format(i,k) , 'f[{},{}]'.format(j,k) ],
														 [  1                     ,  1                     ,  1                     ,  1                     , -1                     , -1                     ]]],
														 senses = 'G',
														 rhs = [-1],
														 names = ['overlap[{},{},{}]'.format(i,j,k)])
	
	# overlap width
	for j in range(n):
		for i in range(n):
			if not i==j:
				milp.linear_constraints.add(lin_expr = [[[ 'x[{}]'.format(i) , 'x[{}]'.format(j) , 'l[{},{}]'.format(i,j) , 'r[{}]'.format(i)],
														 [  1                , -1                ,  max(W)                , -max(W)          ]]],
														 senses = 'L',
														 rhs = [max(W)-w[i]],
														 names = ['overlap width[{},{}]'.format(i,j)])
				
				milp.linear_constraints.add(lin_expr = [[[ 'x[{}]'.format(i) , 'x[{}]'.format(j) , 'l[{},{}]'.format(i,j) , 'r[{}]'.format(i)],
														 [  1                , -1                ,  max(W)                ,  max(W)          ]]],
														 senses = 'L',
														 rhs = [2*max(W)-h[i]],
														 names = ['overlap width rotated[{},{}]'.format(i,j)])
				
	# overlap height
	for j in range(n):
		for i in range(n):
			if not i==j:
				milp.linear_constraints.add(lin_expr = [[[ 'y[{}]'.format(i) , 'y[{}]'.format(j) , 'b[{},{}]'.format(i,j) , 'r[{}]'.format(i)],
														 [  1                , -1                ,  max(H)                , -max(H)          ]]],
														 senses = 'L',
														 rhs = [max(H)-h[i]],
														 names = ['overlap height[{},{}]'.format(i,j)])
														 
				milp.linear_constraints.add(lin_expr = [[[ 'y[{}]'.format(i) , 'y[{}]'.format(j) , 'b[{},{}]'.format(i,j) , 'r[{}]'.format(i)],
														 [  1                , -1                ,  max(H)                ,  max(H)          ]]],
														 senses = 'L',
														 rhs = [2*max(H)-w[i]],
														 names = ['overlap height rotated[{},{}]'.format(i,j)])
														 
	# bin width
	for k in range(n*m):
		for i in range(n):	
			milp.linear_constraints.add(lin_expr = [[[ 'x[{}]'.format(i) , 'f[{},{}]'.format(i,k) , 'r[{}]'.format(i) , 'lw[{}]'.format(k) ],
													 [  1                ,  max(W)                , -max(W)           ,  1                ]]],
													 senses = 'L',
													 rhs = [W[k]-w[i]+max(W)],
													 names = ['bin width[{},{}]'.format(i,k)])
													 
			milp.linear_constraints.add(lin_expr = [[[ 'x[{}]'.format(i) , 'f[{},{}]'.format(i,k) , 'r[{}]'.format(i) , 'lw[{}]'.format(k) ],
													 [  1                ,  max(W)                ,  max(W)           ,  1                ]]],
													 senses = 'L',
													 rhs = [2*W[k]-h[i]+max(W)],
													 names = ['bin width rotated[{},{}]'.format(i,k)])

	# bin height
	for k in range(n*m):
		for i in range(n):	
			milp.linear_constraints.add(lin_expr = [[[ 'y[{}]'.format(i) , 'f[{},{}]'.format(i,k) , 'r[{}]'.format(i) , 'lh[{}]'.format(k) ],
													 [  1                ,  max(H)                , -max(H)           ,  1                ]]],
													 senses = 'L',
													 rhs = [H[k]-h[i]+max(H)],
													 names = ['bin height[{},{}]'.format(i,k)])
													 
			milp.linear_constraints.add(lin_expr = [[[ 'y[{}]'.format(i) , 'f[{},{}]'.format(i,k) , 'r[{}]'.format(i) , 'lh[{}]'.format(k) ],
													 [  1                ,  max(H)                ,  max(H)           ,  1                ]]],
													 senses = 'L',
													 rhs = [2*H[k]-w[i]+max(H)],
													 names = ['bin height rotated[{},{}]'.format(i,k)])
													 
	# every item in a bin
	for i in range(n):													
		milp.linear_constraints.add(lin_expr = [[[ 'f[{},{}]'.format(i,k) for k in range(n*m)],
												 [  1                     for k in range(n*m)]]],
												 senses = 'G',
												 rhs = [1],
												 names = ['item in a bin[{}]'.format(i)])
			
	# an item can not be in a bin which is not used
	for k in range(n*m):
		for i in range(n):		
			milp.linear_constraints.add(lin_expr = [[[ 'f[{},{}]'.format(i,k) , 'z[{}]'.format(k) ],
													 [  1                     , -1                   ]]],
													 senses = 'L',
													 rhs = [0],
													 names = ['unused bin[{},{}]'.format(i,k)])
	
	############################################################################		
	# Objective
	############################################################################
	
	milp.objective.set_linear( [('z[{}]'.format(k) ,c[k])   for k in range(n*m)]
							  +[('lw[{}]'.format(k),cwl[k])  for k in range(n*m)]
							  +[('lh[{}]'.format(k),chl[k])  for k in range(n*m)])
		
		
		
		
		
	# set solver parameters
	milp.parameters.timelimit.set(timelimit)
	milp.parameters.mip.tolerances.mipgap.set(0.001)


	# solve	
	milp.solve()


	############################################################################		
	# get the solution
	############################################################################
	f = [milp.solution.get_values(['f[{},{}]'.format(i,k) for i in range(n)]) for k in range(n*m)]

	z = milp.solution.get_values(['z[{}]'.format(k) for k in range(n*m)])

	x = milp.solution.get_values(['x[{}]'.format(i) for i in range(n)])
	y = milp.solution.get_values(['y[{}]'.format(i) for i in range(n)])
	r = milp.solution.get_values(['r[{}]'.format(i) for i in range(n)])
	
	# parse the solution to a readable format
	bins = []
	cost = 0
	
	for k in range(n*m):
		if z[k] > 0:
			# bin k is used
			bin = {'index':I[k],'width':W[k],'height':H[k],'cost':c[k],'items':[]}
			cost = cost + c[k]
			
			for i in range(n):
				if f[k][i] > 0:
					# item i is in bin k
					if r[i]:
						# the item is rotated
						bin['items'].append({'index':i,'width':h[i],'height':w[i],'x':x[i],'y':y[i]})
					else:
						bin['items'].append({'index':i,'width':w[i],'height':h[i],'x':x[i],'y':y[i]})
			
			bins.append(bin)
	
	
	return (bins,cost)

	
	
def plot_binpacking(bins):
	"""
	plots the packing
	
	Parameters:
	bins:	list, a dictionary with properties and items for each used bin
	"""
	for bin in bins:
		fig,ax = plt.subplots()
		plt.title('bin type {} - cost: {}'.format(bin['index'],bin['cost']))
		plt.plot([0,0,bin['width'],bin['width'],0],[0,bin['height'],bin['height'],0,0],'k-')
		plt.axis('equal')
		
		patches = []
		for item in bin['items']:
			
			patches.append(Polygon([[item['x'],item['y']],[item['x']+item['width'],item['y']],[item['x']+item['width'],item['y']+item['height']],[item['x'],item['y']+item['height']]],closed=True))
			plt.text(item['x']+0.5*item['width'],item['y']+0.5*item['height'],'{}\n({}x{})'.format(item['index'],item['width'],item['height']),horizontalalignment='center',verticalalignment='center')


		p = PatchCollection(patches, cmap=matplotlib.cm.viridis,alpha=0.5)
		p.set_array( np.linspace(0,1,len(patches)) )
		ax.add_collection(p)
	
	plt.draw()
	
if __name__ == '__main__':
	# items
	w = [10,20,20,20,20,40,40]
	h = [20,10,20,20,20,20,20]
	r = [True,False,False,False,False,False,False]
	
	# bin types
	W = [30,40]
	H = [30,40]
	c = [9,16]
	cl = [7,10]
	(bins,cost) = solve_binpacking(w,h,W,H,c,cl,r)
	plot_binpacking(bins)
	
	plt.axis('equal')
	plt.show()