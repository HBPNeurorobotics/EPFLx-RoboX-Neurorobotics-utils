# class SOM_additional (SOM_solution)

import numpy as np
import pandas as pd
import pylab as pl
import matplotlib.pyplot as plt
import matplotlib as mpl
import time

from matplotlib import collections as mc
from matplotlib import patches
from IPython import display
from IPython import get_ipython


class SOM_additional():

	# Self-Organizing Map mapping the environment depending on the positions visited by the robot
    
	def __init__(self):
		import warnings; warnings.filterwarnings('ignore')



	#########################
	###   Visualization   ###
	#########################
	    
	def visualization(self,lattice,Nn,eta,sigma,trial):
		# Self Organazing Map - Process visualization
		get_ipython().run_line_magic('matplotlib', 'inline')
		    
		# SOM-lattice: centers and edges    
		edges = []    # list of links between centers
		centers = []  # list of centers
		for i in range(Nn):
			for j in range(Nn):
				if i > 0:
					edges.append([(lattice[i-1,j,1], lattice[i-1,j,0]),
                                  (lattice[i,j,1], lattice[i,j,0])])
				if j > 0:
					edges.append([(lattice[i,j-1,1], lattice[i,j-1,0]),
                                      (lattice[i,j,1], lattice[i,j,0])])
				
				centers.append((lattice[i,j,1],lattice[i,j,0]))
                
		Cx,Cy = zip(*centers)
		lc2 = mc.LineCollection(edges, colors='red', linewidths=.8)

		# ENVIRONMENT   
		# walls
		borders = [[(4.8,4.8), (4.8,-4.8)], [(4.8,-4.8), (-4.8,-4.8)],
                  [(-4.8,-4.8), (-4.8,4.8)], [(-4.8,4.8), (4.8,4.8)]]
		lc1 = mc.LineCollection(borders, colors='black', linewidths=1)
		
		# obstracles
		rect1 = patches.Rectangle((-1.0,-3.0), 2., 1., color='black')
		rect2 = patches.Rectangle(( 1.0,-3.0), 1., 3., color='black')
		rect3 = patches.Rectangle((-2.0, 0.0), 1., 2., color='black')
		rect4 = patches.Rectangle((-2.0, 2.0), 3., 1., color='black')
				
		# PLOT (displaying)
		# define figure
		fig = plt.figure(0,figsize=(8, 6))

		# Information board
		fig.suptitle('Trial: {} [sigma: {}, eta: {}]; Map: {}x{}'.format(int(trial), round(sigma,3), round(eta,3), Nn, Nn)) #  (links: {}) , len(edges)
		ax = fig.add_subplot(111)

		# displaying of obstacles
		ax.add_patch(rect1)
		ax.add_patch(rect2)
		ax.add_patch(rect3)
		ax.add_patch(rect4)

		# displaying of walls
		ax.add_collection(lc1)

		# displaying of exploration data
		plt.plot(self.pos[:,1], self.pos[:,0],'b.',alpha=0.1)

		# displaying of SOM-lattice
		ax.add_collection(lc2)               # edges
		plt.plot(Cx, Cy,'ro',markersize=8.0) # centers
		
		# SHOW (figure)
		plt.gca().invert_yaxis()
		ax.axes.get_xaxis().set_visible(False)
		ax.axes.get_yaxis().set_visible(False)

		plt.gca().set_aspect('equal', adjustable='box')
		display.clear_output(wait=True)
		display.display(plt.gcf())



	################################
	###   Upload and Save data   ###
	################################
	    
	def load_data(self,csv_file):
		# exctract and transform data
		states = pd.read_csv(csv_file, delimiter=',',header=0).values
		positions = np.array([pd.to_numeric(states[:,0], errors='coerce'), pd.to_numeric(states[:,1], errors='coerce')]).T
		# Reduce the number of data points
		self.pos = positions[slice(0,positions.shape[0],(positions.shape[0]/1000)),:]
		return self.pos
		        
    
	def save_lattice2(self,lattice):
		# convert it to stacked format using Pandas
		stacked = pd.Panel(lattice.swapaxes(1,2)).to_frame().stack().reset_index()
		stacked.columns = ['x', 'y', 'z', 'value']
		# save to file
		stacked.to_csv('SOM_data_lattice.csv', index=False)

		
	def save_lattice(self,lattice,Nn):
		# prepare data to write
		output = np.zeros((Nn*Nn,4))
		for i in range(Nn):
			for j in range(Nn):
				output[i*Nn+j][:] = [i,j,lattice[i,j,0],lattice[i,j,1]] 
		# save to file
		np.savetxt('SOM_data_lattice.csv', output, delimiter=",", header = "Lattice index X,# Lattice index Y,# Coordinate X,# Coordinate Y")

	def pre_process(self,trials,Nn,video):
		from IPython import display
		from ipywidgets import IntProgress
		viz = ['simulation','visualization','grading']
		video = viz.index(video)
		if(video==2): Nn = 12
		T = time.time()
		f = IntProgress(min=0, max=trials) # instantiate the bar
		display.display(f) # display the bar
		return T,f,Nn
	
	def process(self, lattice, Nn, N_trials, eta, sigma, trial, video, f):
		viz = ['simulation','visualization','grading']
		video = viz.index(video)
		f.value += 1
		self.save_lattice(lattice,Nn)
		if(video or trial==N_trials): 
			if(video<2): self.visualization(lattice,Nn,eta,sigma,trial)
	
	def post_process(self, T, video):
		viz = ['simulation','visualization','grading']
		video = viz.index(video)
		display.clear_output(wait=True)
		if(video<2): print 'Done. Simulation time is ', time.time()-T, '(s).'
