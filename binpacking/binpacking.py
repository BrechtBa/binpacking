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
"""

References:
	[1] D. Pisinger and M. Sigurd, “The two-dimensional bin packing problem with variable bin sizes and costs,” Discret. Optim., vol. 2, no. 2, pp. 154–167, Jun. 2005.
"""	
	
from __future__ import division
from pyomo.environ import *
import numpy as np
import itertools
import matplotlib.pyplot as plt
import matplotlib.cm
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

	
def solve_binpacking(item_width,item_height,item_allow_rotation,bin_width,bin_height,bin_cost=[],cost_maximum_leftover_width=None,cost_maximum_leftover_height=None,bin_cost_leftover_width=[],bin_cost_leftover_height=[],solver='cplex',options={}):
	"""
	Solves a bin packing problem with variable bins and variable cost
	An addition is made to specify if an item is allowed to rotate 90deg
	
	Parameters:
		item_width:		list, widths of the items
		item_height:	list, heights of the items
		item_allow_rotation: list, True if the item is allowed to rotate 90deg
		bin_width:		list, widths of the bin types
		bin_height:		list, heights of the bin types
		bin_cost:		list, [], cost of each bin type
		cost_maximum_leftover_width: 	Number, cost of the maximum height leftover 
		cost_maximum_leftover_width: 	Number, cost of the maximum height leftover  
		bin_cost_leftover_width: 		list, [], the cost per unit width of the total width which is left over in each bin. Defaults to -0.5 times the total bin cost divided by the bin width
		bin_cost_leftover_height: 		list, [], the cost per unit height of the total height which is left over in each bin. Defaults to -0.5 times the total bin cost divided by the bin height
		timelimit:		number, 20, the maximum MILP computation time in seconds
	
	Returns:
		bins:	list, a dictionary with properties and items for each used bin

	Example:
	
	"""
	
	# Input handling
	#items
	w = item_width
	h = item_height
	n = len(w)
	
	if not len(item_allow_rotation)==len(w):
		r = [0]*n
	else:
		r = [1 if a else 0 for a in item_allow_rotation]
	
		
	
	# bins
	W = bin_width
	H = bin_height
	m = len(W)
	
	if len(bin_cost)==0:
		c = [1]*m
	else:
		c = bin_cost
	
	
	if cost_maximum_leftover_width == None and cost_maximum_leftover_height == None:
		cmaxlw = 0
		cmaxlh = -0.1*max(c)/max(H)
	elif cost_maximum_leftover_width == None:
		cmaxlw = 0
		cmaxlh = cost_maximum_leftover_height
	elif cost_maximum_leftover_height == None:
		cmaxlw = cost_maximum_leftover_width
		cmaxlh = 0
	else:
		cmaxlw = cost_maximum_leftover_width
		cmaxlh = cost_maximum_leftover_height
	
	
	if not len(bin_cost_leftover_width)==len(W):
		clw = [0 for ci,Wi in zip(c,W)]
	else:
		clw = bin_cost_leftover_width
	
	
	if not len(bin_cost_leftover_height)==len(W):
		clh = [0 for ci,Hi in zip(c,H)]
	else:
		clh = bin_cost_leftover_height
	
	
	# convert bins to binary format, each bin can only be used once
	I = range(m)*n
	W = W*n
	H = H*n
	c = c*n
	clw = clw*n
	clh = clh*n 
	
	
	# Create Data dictionary
	data={None:{
		'i':{None: tuple(range(len(w)))},
		'k':{None: tuple(range(len(W)))},
		'w':{(i,): val for i,val in enumerate(w)},
		'h':{(i,): val for i,val in enumerate(h)},
		'ar':{(i,): val for i,val in enumerate(r)},
		'W':{(i,): val for i,val in enumerate(W)},
		'H':{(i,): val for i,val in enumerate(H)},
		'maxW':{None: max(W)},
		'maxH':{None: max(H)},
		'c':{(i,): val for i,val in enumerate(c)},
		'clw':{(i,): val for i,val in enumerate(clw)},
		'clh':{(i,): val for i,val in enumerate(clh)},
		'cmaxlw':{None: cmaxlw},
		'cmaxlh':{None: cmaxlh},
	}}
	
	
	# Create a problem instance and solve
	instance = model.create_instance(data)
	
	# Solve
	optimizer = SolverFactory(solver)
		
	results = optimizer.solve(instance, options=options)

	print( results )
	# Retrieve the results
	f = [[instance.f[i,k].value for i in instance.i] for k in instance.k]

	z = [instance.z[k].value for k in instance.k]

	x = [instance.x[i].value for i in instance.i]
	y = [instance.y[i].value for i in instance.i]
	r = [instance.r[i].value for i in instance.i]
	
	
	lw = [instance.lw[k].value for k in instance.k]
	lh = [instance.lh[k].value for k in instance.k]
	
	mlw = [instance.mlw[k].value for k in instance.k]
	mlh = [instance.mlh[k].value for k in instance.k]	

	
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
	
	
	nCols = int( len(bins)/np.floor(len(bins)**0.5) )
	nRows = int( len(bins)/nCols )
	
	fig, axs = plt.subplots(nRows,nCols)
	
	# chech if axes is iterable
	try:
		some_object_iterator = iter(axs)
	except TypeError, te:
		axs = (axs,)
	
	for bin,ax in zip(bins,axs):
		
		ax.plot([0,0,bin['width'],bin['width'],0],[0,bin['height'],bin['height'],0,0],'k-')
		ax.set_title('bin type {} - cost: {}'.format(bin['index'],bin['cost']))
		ax.set_aspect('equal', adjustable='box')
		
		patches = []
		for item in bin['items']:
			
			patches.append(Polygon([[item['x'],item['y']],[item['x']+item['width'],item['y']],[item['x']+item['width'],item['y']+item['height']],[item['x'],item['y']+item['height']]],closed=True))
			ax.text(item['x']+0.5*item['width'],item['y']+0.5*item['height'],'{}\n({}x{})'.format(item['index'],item['width'],item['height']),horizontalalignment='center',verticalalignment='center')


		p = PatchCollection(patches, cmap=matplotlib.cm.viridis,alpha=0.5)
		p.set_array( np.linspace(0,1,len(patches)) )
		ax.add_collection(p)
	
	plt.draw()
	
	
	
	
	
################################################################################
# define the bin packing abstract model
################################################################################
model = AbstractModel()

# define sets
model.i = Set(doc='set of items')
model.k = Set(doc='set of all bins, every bin type times the number of items')

#model.ij =  Set(dimen=2, rule=lambda model: [(i,j) for i in model.i for j in model.i if j<i ])

# define parameters
model.w = Param(model.i, doc='item widths')
model.h = Param(model.i, doc='item heights')
model.ar = Param(model.i, doc='allow item rotation')

model.W = Param(model.k, doc='bin widths')
model.H = Param(model.k, doc='bin heights')

model.maxW = Param(doc='maximum bin width')
model.maxH = Param(doc='maximum bin height')

model.c = Param(model.k, doc='bin costs')
model.clw = Param(model.k, doc='bin width leftover costs')
model.clh = Param(model.k, doc='bin height leftover costs')
model.cmaxlw = Param(doc='bin width leftover costs')
model.cmaxlh = Param(doc='bin height leftover costs')


# define variables
model.l = Var(model.i, model.i, domain=Boolean, doc='l[i,j] is 1 if item i is on the left of item j')
model.b = Var(model.i, model.i, domain=Boolean, doc='b[i,j] is 1 if item i is below item j')

model.f = Var(model.i, model.k, domain=Boolean, doc='f[i,k] is 1 if item i is in bin k')
model.z = Var(model.k, domain=Boolean, doc='z[k] is 1 if bin k is used')

model.x = Var(model.i, domain=NonNegativeReals, doc='x[i] is the x-coordinate of item i')
model.y = Var(model.i, domain=NonNegativeReals, doc='y[i] is the y-coordinate of item i')

model.r = Var(model.i, domain=Boolean, doc='r[i] is 1 item i is rotated 90deg')

model.lw = Var(model.k, domain=NonNegativeReals, doc='lw[k] is the unused width in bin k')
model.lh = Var(model.k, domain=NonNegativeReals, doc='lh[k] is the unused height in bin k')

model.mlw = Var(model.k, domain=Boolean, doc='mlw[k] is 1 if lwk == maxlw')
model.mlh = Var(model.k, domain=Boolean, doc='mlw[k] is 1 if lwk == maxlw')

model.maxlw = Var(domain=NonNegativeReals, doc='maxlw is the maximum of lw')
model.maxlh = Var(domain=NonNegativeReals, doc='maxlh is the maximum of lh')


# define constraints
model.ConstraintNoOverlap = Constraint(model.i,model.i,model.k,
	rule=lambda model,i,j,k: model.l[i,j] + model.l[j,i] + model.b[i,j] + model.b[j,i] + (1 - model.f[i,k]) + (1 - model.f[j,k]) >= 1 if i < j else Constraint.Feasible
)

model.ConstraintOverlapWidth = Constraint(model.i,model.i,
	rule=lambda model,i,j: model.x[i] + model.w[i] - model.x[j] - model.maxW*(1-model.l[i,j]) - model.maxW*model.r[i] <= 0
)
model.ConstraintOverlapWidthRotated = Constraint(model.i,model.i,
	rule=lambda model,i,j: model.x[i] + model.h[i] - model.x[j] - model.maxW*(1-model.l[i,j]) - model.maxW*(1-model.r[i]) <= 0
)


model.ConstraintOverlapHeight = Constraint(model.i,model.i,
	rule=lambda model,i,j: model.y[i] + model.h[i] - model.y[j] - model.maxH*(1-model.b[i,j]) - model.maxH*model.r[i] <= 0
)
model.ConstraintOverlapHeightRotated = Constraint(model.i,model.i,
	rule=lambda model,i,j: model.y[i] + model.w[i] - model.y[j] - model.maxH*(1-model.b[i,j]) - model.maxH*(1-model.r[i]) <= 0
)


model.ConstraintBinWidth = Constraint(model.i,model.k,
	rule=lambda model,i,k: model.x[i] + model.w[i] - model.maxW*(1-model.f[i,k]) - model.maxW*model.r[i] + model.lw[k] <= model.W[k]
)
model.ConstraintBinWidthRotated = Constraint(model.i,model.k,
	rule=lambda model,i,k: model.x[i] + model.h[i] - model.maxW*(1-model.f[i,k]) - model.maxW*(1-model.r[i]) + model.lw[k] <= model.W[k]
)


model.ConstraintBinHeight = Constraint(model.i,model.k,
	rule=lambda model,i,k: model.y[i] + model.h[i] - model.maxH*(1-model.f[i,k]) - model.maxH*model.r[i] + model.lh[k] <= model.H[k]
)
model.ConstraintBinHeightRotated = Constraint(model.i,model.k,
	rule=lambda model,i,k: model.y[i] + model.w[i] - model.maxH*(1-model.f[i,k]) - model.maxH*(1-model.r[i]) + model.lh[k] <= model.H[k]
)

model.ConstraintEveryItem = Constraint(model.i,
	rule=lambda model,i: sum(model.f[i,k] for k in model.k) >= 1
)

model.ConstraintUnusedBins = Constraint(model.i,model.k,
	rule=lambda model,i,k: model.f[i,k] <= model.z[k]
)

model.ConstraintAllowRotation = Constraint(model.i,
	rule=lambda model,i: model.r[i] <= model.ar[i]
)

	
model.ConstraintMaximumWidth = Constraint(model.k,
	rule=lambda model,k: model.maxlw <= model.lw[k] + (1-model.mlw[k])*model.maxW
)
model.ConstraintMaximumHeigth = Constraint(model.k,
	rule=lambda model,k: model.maxlh <= model.lh[k] + (1-model.mlh[k])*model.maxH
)

model.ConstraintOneMaximumWidth = Constraint(
	rule=lambda model: sum(model.mlw[k] for k in model.k) == 1
)
model.ConstraintOneMaximumHeight = Constraint(
	rule=lambda model: sum(model.mlh[k] for k in model.k) == 1
)

model.ConstraintMaximumWidthIsUsedBin = Constraint(model.k,
	rule=lambda model,k: model.mlw[k] <= model.z[k]
)
model.ConstraintMaximumHeightIsUsedBin = Constraint(model.k,
	rule=lambda model,k: model.mlh[k] <= model.z[k]
)


# define the objective
model.Objective = Objective(
	rule=lambda model: sum(model.z[k]*model.c[k] + model.lw[k]*model.clw[k] + model.lh[k]*model.clh[k] for k in model.k) + model.maxlw*model.cmaxlw  + model.maxlh*model.cmaxlh
)

	
	
	
	
if __name__ == '__main__':

	# Basic example
	# items
	item_width = [10,20,20,20,20,40,40]
	item_height = [20,10,20,20,20,20,20]
	item_allow_rotation = [False]*len(item_width)
	
	# bin types
	bin_width = [30,40]
	bin_height = [30,40]
	bin_cost = [9,16]
	
	# solve
	(bins,cost) = solve_binpacking(item_width,
								   item_height,
								   item_allow_rotation,
								   bin_width,
								   bin_height,
								   bin_cost)
	# plot							   
	plot_binpacking(bins)
	
	plt.show()