# class SARSA_additional

import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import collections as mc
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib import colors
import random
import pylab as pl
from IPython import display
from IPython.display import clear_output
import math
import time
import csv
import os

from ast import literal_eval


class SARSA_additional():
    
	def __init__(self):
    
		import warnings; warnings.filterwarnings('ignore')
		self.testfile = 'SOM_data_lattice.csv'
		self.lattice = {}
		self.pos = {}
        
		self.edges = {}
		self.centers = {}
		self.test = {}

		# imdata
		self.Nn = {}
		self.Trial = {}
		self.Run = {}
		# actdata
		self.x_position = {}
		self.y_position = {}
		self.x_position_old = {}
		self.y_position_old = {}
		# Rdata
		self.reward_position = {}
		self.s_goal = [0,0]
		# Qdata
		self.Qdata = {}
		
        


	########################################################################
	#	SOM analysis
	########################################################################

	### Main analysis program
	def run_processing(self):
		self.test = False
		self.input = True
		# SOM pre-processing
		self.upload_positions()
		self.upload_lattice()
		self.net_details()

		# SOM analyse (to generate maze and reward)
		## maze
		self.guide = np.zeros((self.Nn,self.Nn,4))
		states = self.rewarded_states()
		actions = self.rewarded_actions(states)

		# visualization (Maze: 2 Modes; Reward: Table)
		self.visualization1(states,actions)	# Mode 1
		self.visualization2(states,actions,self.test)	# Mode 2
		reward = self.reward_goal(states)
		choice = self.choice_data(states,actions)

		return reward, choice
    

	### Test analysis program
	def test_analysis(self,goal,testfile):
		self.input = False
		self.s_goal = goal
		self.testfile = testfile
		# SOM pre-processing
		#self.upload_positions()
		self.upload_lattice(self.testfile)
		self.net_details()

		# SOM analyse (to generate maze and reward)
		## maze
		states = self.rewarded_states()
		actions = self.rewarded_actions(states)

		## reward
		reward = self.reward_goal(states)
		choice = self.choice_data(states,actions)

		#return self.Nn, self.lattice, self.pos, reward



	def eva_analysis(self,testfile):
		self.testfile = testfile
		#self.upload_positions()
		self.upload_lattice(self.testfile)
		self.net_details()

		# SOM analyse (to generate maze and reward)
		## maze
		states = self.rewarded_states()
		actions = self.rewarded_actions(states)

		Reward, reward_pos = self.upload_reward()
		self.upload_Qvalue() 

		return self.Nn, states, actions, Reward, reward_pos, self.Q


	
	##################################################################################
	#####                 B.1. SOM analysis for Maze visualization               #####
	##################################################################################
	
	### Define centers and links of SOM
	def net_details(self):
		# SOM-MAP: centers and edges    
		self.edges = []    # list of links between centers
		self.centers = []  # list of centers
		for i in range(self.Nn):
			for j in range(self.Nn):
				if i > 0: self.edges.append([(self.lattice[i-1,j,0], self.lattice[i-1,j,1]),
                                                             (self.lattice[i,j,0],   self.lattice[i,j,1])])
				if j > 0: self.edges.append([(self.lattice[i,j-1,0], self.lattice[i,j-1,1]),
                                                             (self.lattice[i,j,0],   self.lattice[i,j,1])])
				self.centers.append((self.lattice[i,j,0],self.lattice[i,j,1]))
        
	### Define centers on the internal walls
	def rewarded_states(self):
		# Internal wall outlines - description:
		#	rect1 = patches.Rectangle((-3.0,-1.0), 1., 2., color='black')
		#	rect2 = patches.Rectangle((-3.0, 1.0), 3., 1., color='black')
		#	rect3 = patches.Rectangle(( 0.0,-2.0), 2., 1., color='black')
		#	rect4 = patches.Rectangle(( 2.0,-2.0), 1., 3., color='black')

		act_pos = np.ones((self.Nn**2))
		for i,center in enumerate(self.centers):
			#rect1
			lx0 = -3.0; lx1 = -2.0; ly0 = -1.0; ly1 = 1.0;
			if((center[0]>=lx0)&(center[0]<=lx1)) & ((center[1]>=ly0)&(center[1]<=ly1)): act_pos[i] = 0.0
			#rect2
			lx0 = -3.0; lx1 = 0.0; ly0 = 1.0; ly1 = 2.0;
			if((center[0]>=lx0)&(center[0]<=lx1)) & ((center[1]>=ly0)&(center[1]<=ly1)): act_pos[i] = 0.0
			#rect3
			lx0 = 0.0; lx1 = 2.0; ly0 = -2.0; ly1 = -1.0;
			if((center[0]>=lx0)&(center[0]<=lx1)) & ((center[1]>=ly0)&(center[1]<=ly1)): act_pos[i] = 0.0
			#rect4
			lx0 = 2.0; lx1 = 3.0; ly0 = -2.0; ly1 = 1.0;
			if((center[0]>=lx0)&(center[0]<=lx1)) & ((center[1]>=ly0)&(center[1]<=ly1)): act_pos[i] = 0.0
		return act_pos
        

	### Define links crossed the internal walls
	def rewarded_actions(self,states):
		# Evaluation: links
		wall = [[(-3.0,-1.0),(-3.0, 2.0)], [(-2.0,-1.0),(-2.0, 2.0)], [( 0.0, 1.0),( 0.0, 2.0)],
                        [(-3.0, 2.0),( 0.0, 2.0)], [(-3.0, 1.0),( 0.0, 1.0)], [(-3.0,-1.0),(-2.0,-1.0)],
                        [( 3.0, 1.0),( 3.0,-2.0)], [( 2.0, 1.0),( 2.0,-2.0)], [( 0.0,-1.0),( 0.0,-2.0)],
                        [( 3.0,-2.0),( 0.0,-2.0)], [( 3.0,-1.0),( 0.0,-1.0)], [( 3.0, 1.0),( 2.0, 1.0)]];

		results = []
		for i,edge in enumerate(self.edges):
			result = False
			for w in range(len(wall)):
				# check if link cross a wall
				result += self.cross(edge, wall[w])
				# check if one of centers is on a wall
				idx0 = self.centers.index(edge[0]) 
				idx1 = self.centers.index(edge[1])
				if(states[idx0]+states[idx1]==0): result = True
			# add info into list
			results.append(result)
		return results

	### Define the crossing
	def cross(self, link, wall):
		v1 = (wall[1][0]-wall[0][0])*(link[0][1]-wall[0][1]) -\
			 (wall[1][1]-wall[0][1])*(link[0][0]-wall[0][0]);
		v2 = (wall[1][0]-wall[0][0])*(link[1][1]-wall[0][1]) -\
			 (wall[1][1]-wall[0][1])*(link[1][0]-wall[0][0]);
		v3 = (link[1][0]-link[0][0])*(wall[0][1]-link[0][1]) -\
			 (link[1][1]-link[0][1])*(wall[0][0]-link[0][0]);
		v4 = (link[1][0]-link[0][0])*(wall[1][1]-link[0][1]) -\
			 (link[1][1]-link[0][1])*(wall[1][0]-link[0][0]);
		return (v1*v2<0) & (v3*v4<0)


	##################################################################################
	#####                        B.1. Input of Goal position                     #####
	##################################################################################
	
	# Define reward as each Q(x,y,a)
	def reward_goal(self,states):
		if(self.input):
			while True:
				print; print		'==================================================================================================================='

				try:
					self.s_goal = input('Goal coordinates (format = [vertical,horizontal], example = [0,0]):');
					print 		 '==================================================================================================================='; print
					if(states[self.Nn*self.s_goal[0]+self.s_goal[1]] == 1.0): break
					print "Goal cannot be in the wall. You have to change the goal position."
				except: 
					print 		 '==================================================================================================================='; print
					print "Input is incorrect, please, use an example to make correct input."
		else:
			self.s_goal = self.s_goal

		return self.s_goal
	

	##################################################################################
	#####                       B.1. List of possible action                     #####
	##################################################################################

	# Define reward as each Q(x,y,a)
	def choice_data(self,states,actions):
		# define possible actions
		reward = []
		for i in range(self.Nn):
			for j in range(self.Nn):
				acts = []
				for a in range(4):
					if  (a == 0): ish =  1; jsh =   0;
					elif(a == 1): ish = -1; jsh =   0;
					elif(a == 2): ish =  0; jsh =   1;
					elif(a == 3): ish =  0; jsh =  -1;

					able = self.availability(i,j,i+ish,j+jsh,actions)
					if(able==0.0): acts.append(a)
				reward.append(acts)

		# Representation of possible actions
		def color_negative(val):
			color = {len(val)==9.0: 'cornsilk', len(val)%2==0.0: 'lime', len(val)==2.0: 'papayawhip'}.get(True, 'oldlace')
			return 'background-color: %s' % color

		def border_negative(val):
			color = {len(val)>=9.0: 'none', len(val)==2.0: 'solid solid solid solid', \
				 val.find("[0,1]") > -1: 'none solid none solid', \
				 val.find("[0,2]") > -1: 'solid none none solid', \
				 val.find("[0,3]") > -1: 'solid solid none none', \
				 
				 val.find("[1,2]") > -1: 'none none solid solid', \
				 val.find("[1,3]") > -1: 'none solid solid none', \
				 
				 val.find("[2,3]") > -1: 'solid none solid none', \
				 
				 val.find("[0]") > -1: 'solid solid none solid', \
				 val.find("[1]") > -1: 'none solid solid solid', \
				 val.find("[2]") > -1: 'solid none solid solid', \
				 val.find("[3]") > -1: 'solid solid solid none', \
				 
				 val.find("[0,1,2]") > -1: 'none none none solid', \
				 val.find("[1,2,3]") > -1: 'none none solid none', \
				 val.find("[0,1,3]") > -1: 'none solid none none', \
				 val.find("[0,2,3]") > -1: 'solid none none none'}.get(True, 'none')
			return 'border-style: %s' % color
		
		output = np.chararray((self.Nn,self.Nn), itemsize=10)
		for i in range(self.Nn):
			for j in range(self.Nn):
				output[i][j] = '['+','.join(str(e) for e in reward[i*self.Nn+j])+']'
				if(i==self.s_goal[0] and j==self.s_goal[1]): output[i][j] = ' ' + output[i][j]
				
		#print "self.test: ", self.testfile
		if(self.testfile=='SOM_data_lattice.csv'): print 'Possible actions to choose: 0 - Down; 1 - Up; 2 - Right; 3 - Left.'
		df = pd.DataFrame(output); df.columns.name = 'Actions';
		df.to_csv('SOM_possible_actions.csv')
		df = df.style.applymap(border_negative).applymap(color_negative).set_properties(**{'width': '100px', 'border': '3px 1px black solid !important',  'color': 'black !important'});
		if(self.testfile=='SOM_data_lattice.csv'): display.display(df)

		return reward
	

	# Define the punishment at Q(x,y,a)
	def availability(self, x0, y0, x1, y1, actions):
		Cx,Cy = zip(*self.centers)
		if  (0 <= x1 < self.Nn) & (0 <= y1 < self.Nn):
			idx0 = x0*self.Nn+y0; idx1 = x1*self.Nn+y1;
			edge0 = [(Cx[idx0],Cy[idx0]),(Cx[idx1],Cy[idx1])]
			edge1 = [(Cx[idx1],Cy[idx1]),(Cx[idx0],Cy[idx0])]

			idx = -1
			try: idx = self.edges.index(edge0)
			except: idx = idx
			try: idx = self.edges.index(edge1)
			except: idx = idx

			if(idx >= 0):
				if(actions[idx] == False):  return 0.0
				else:  return -1.0
			else:  return -1.0
		else:  return -1.0


	########################################################################
	#	Visualization functions
	########################################################################

	def visualization_main(self, video=1, simdata=[], actdata=[], Rdata=[], Sdata=[], Qdata=[]):
		self.test = True

		# imdata
		self.Nn = simdata[0]
		self.Trial = simdata[1]
		self.Run = simdata[2]
		# actdata
		self.x_position = actdata[0]
		self.y_position = actdata[1]
		self.x_position_old = actdata[2]
		self.y_position_old = actdata[3]
		# Rdata
		self.reward_position = Rdata
		# Sdata
		self.start_position = Sdata
		# Qdata
		self.Qdata = Qdata

		self.upload_positions()
		self.upload_lattice()
		self.net_details()
		states = self.rewarded_states()
		actions = self.rewarded_actions(states)
		
		if(video == 1): self.visualization1(states,actions)
		if(video == 2): self.visualization2(states,actions,self.test)


	###########################################################################
    
	def visualization1(self,states,actions):

		#------------------------ FIGURE ------------------------###
		get_ipython().run_line_magic('matplotlib', 'inline')

		# --- plot
		fig1 = plt.figure(0,figsize=(8, 6))
		if(self.test):
			fig1.suptitle('Trial: {}; Episode: {}; Q({},{}): {}'.format(int(self.Trial),\
						  int(self.Run), self.x_position, self.y_position, self.Qdata.round(4)))
		else:
			fig1.suptitle('Adapted SOM for SARSA implementation (Reds are unavailable).')

		# --- sub-plot
		ax = fig1.add_subplot(111)
		if(self.test):
			ax.set_title('Action: ({},{}) --> ({},{})'.format(self.x_position_old,\
						  self.y_position_old,self.x_position,self.y_position))

		#---------------------- ENVIRONMENT ---------------------###
		# --- outlines
		borders = [[(4.8,4.8), (4.8,-4.8)], [(4.8,-4.8), (-4.8,-4.8)],
                    [(-4.8,-4.8), (-4.8,4.8)], [(-4.8,4.8), (4.8,4.8)]]
		lc1 = mc.LineCollection(borders, colors='black', linewidths=1)     # create line collections
		ax.add_collection(lc1)

		# --- obstracles
		rect1 = patches.Rectangle((-1.0,-3.0), 2., 1., color='black')
		rect2 = patches.Rectangle(( 1.0,-3.0), 1., 3., color='black')
		rect3 = patches.Rectangle((-2.0, 0.0), 1., 2., color='black')
		rect4 = patches.Rectangle((-2.0, 2.0), 3., 1., color='black')

		ax.add_patch(rect1)
		ax.add_patch(rect2)
		ax.add_patch(rect3)
		ax.add_patch(rect4)

		# --- exploration
		plt.plot(self.pos[:,1], self.pos[:,0],'b.',alpha=0.1)

		#-------------------------- SOM -------------------------###
		# --- actions
		Yedges = []; Nedges = []
		for i,edge in enumerate(self.edges):
			if(actions[i]): Nedges.append([(edge[0][1],edge[0][0]),(edge[1][1],edge[1][0])])
			else: Yedges.append([(edge[0][1],edge[0][0]),(edge[1][1],edge[1][0])]) 
        
		lc2 = mc.LineCollection(Nedges, colors='magenta', linewidths=.8)
		lc3 = mc.LineCollection(Yedges, colors='green', linewidths=.8)

		ax.add_collection(lc2)
		ax.add_collection(lc3)

		# --- states
		Cx,Cy = zip(*self.centers)
		for i,center in enumerate(self.centers):
			if(states[i] == 1.0): plt.plot(Cy[i], Cx[i],'o',color='lime',markersize=8.0)
			else: plt.plot(Cy[i], Cx[i],'o',color='magenta',markersize=8.0)

		#------------------------ POINTS ------------------------###

		if(self.test):
			# --- goal
			Gind = self.reward_position[0]*self.Nn + self.reward_position[1]
			plt.plot(Cy[Gind], Cx[Gind],'o',color='gold',markersize=25.0)
			# --- start
			Sind = self.start_position[0]*self.Nn + self.start_position[1]
			plt.plot(Cy[Sind], Cx[Sind],'ro', alpha = 0.4, markersize=25.0)
			# --- agent
			Cind = self.x_position_old*self.Nn + self.y_position_old
			plt.plot(Cy[Cind], Cx[Cind],'ro',markersize=15.0)
			# --- agent-reward
			if(self.reward_position[0] == self.x_position and self.reward_position[1] == self.y_position): 
				plt.plot(Cy[Gind], Cx[Gind],'o',color='brown',markersize=25.0); time.sleep(3)

		#----------------------- SETTINGS -----------------------###
		plt.gca().invert_yaxis()
		ax.axes.get_xaxis().set_visible(False)
		ax.axes.get_yaxis().set_visible(False)
		plt.gca().set_aspect('equal', adjustable='box')
		if(self.test):
			display.clear_output(wait=True)
			display.display(plt.gcf())
		else:
			plt.show()
			print '==================================================================================================================='
			#raw_input('Maze created based on your SOM solution. Visualization mode 1.\n\nPress Enter to continue... ')
			#display.clear_output(wait=True)


	###########################################################################

	def visualization2(self,states,actions,test,goal=None):

		#------------------------ FIGURE ------------------------###
		get_ipython().run_line_magic('matplotlib', 'inline')

		# --- plot
		fig2 = plt.figure(0,figsize=(8, 6))
		if(self.test):
			fig2.suptitle('Trial: {}; Episode: {}; Q({},{}): {}'.format(int(self.Trial),\
						  int(self.Run), self.x_position, self.y_position, self.Qdata.round(4)))
		else:
			fig2.suptitle('Your maze for SARSA implementation.')

		# --- sub-plot
		ax = fig2.add_subplot(111)
		if(test):
			ax.set_title('Action: ({},{}) --> ({},{})'.format(self.x_position_old,\
						  self.y_position_old,self.x_position,self.y_position))

		#---------------------- ENVIRONMENT ---------------------###

		# --- Major ticks
		ax.set_xticks(np.arange(0, self.Nn, 1));
		ax.set_yticks(np.arange(0, self.Nn, 1));

		# --- Labels for major ticks
		ax.set_xticklabels(np.arange(0, self.Nn, 1));
		ax.set_yticklabels(np.arange(0, self.Nn, 1));

		# --- Minor ticks
		ax.set_xticks(np.arange(-.5, self.Nn, 1), minor=True);
		ax.set_yticks(np.arange(-.5, self.Nn, 1), minor=True);

		# --- Gridlines based on minor ticks
		ax.grid(which='minor', color='k', alpha = 0.2, linestyle='-', linewidth=1)

		# --- Environment size
		ax.set_xlim(-0.5, self.Nn-0.5)
		ax.set_ylim(-0.5, self.Nn-0.5)
		ax.invert_yaxis()

		#----------------------- OBSTRACLES ---------------------###
		# --- Internal walls
		idx = 0
		for i in range(self.Nn):
			for j in range(self.Nn):
				if i > 0:
					if(actions[idx]):
						x1 = (i-1)+0.5; y1 = (j)+0.5;
						x2 = (i)-0.5;   y2 = (j)-0.5;
						ax.plot([y1,y2],[x1,x2],'k',linestyle='-', linewidth=3)
					idx += 1
				if j > 0:
					if(actions[idx]):
						x1 = (i)+0.5;   y1 = (j-1)+0.5;
						x2 = (i)-0.5;   y2 = (j)-0.5;
						ax.plot([y1,y2],[x1,x2],'k',linestyle='-', linewidth=3)
					idx += 1

		for i in range(self.Nn):
			for j in range(self.Nn):
				if(states[self.Nn*i+j] == 0.0): 
					rectB = patches.Rectangle((j-0.5, i-0.5), 1.0, 1.0, color='black')
					ax.add_patch(rectB)

		#------------------------- POINTS -----------------------###
		if(self.test):
			# --- goal
			rect1 = patches.Rectangle((self.reward_position[1]-0.5,\
									   self.reward_position[0]-0.5), 1.0, 1.0, color='lime')
			ax.add_patch(rect1)
			# --- agent
			rect2 = patches.Rectangle((self.y_position-0.25,\
									   self.x_position-0.25), 0.5, 0.5, color='red')
			ax.add_patch(rect2)
			# --- start
			#rect3 = patches.Rectangle((self.y_position-0.25,\
			#						   self.x_position-0.25), 0.5, 0.5, color='orange')
			#ax.add_patch(rect3)
 		
		elif(goal!=None): 
			# --- goal
			rect1 = patches.Rectangle((goal[1]-0.5,goal[0]-0.5), 1.0, 1.0, color='lime')
			ax.add_patch(rect1)

		#----------------------- SETTINGS -----------------------###
		plt.gca().set_aspect('equal', adjustable='box')
		if(self.test):
			display.clear_output(wait=True)
			display.display(plt.gcf())
		else:
			plt.show()
			#raw_input('Maze adapted from your SOM soulution. Visualization mode 2.\n\nPress Enter to continue... ')
			#display.clear_output(wait=True)



	def latency(self, latency, N_trials, Nn):
		plt.figure(0,figsize=(16, 9))
		plt.title('Red line is an expected maximum latency.', fontsize=18)
		plt.plot(latency[0::1],'b')
		plt.axhline(y=2*Nn, linewidth=4, color='r')
		plt.xlim(0,int(N_trials))
		plt.ylim(0,Nn*Nn)
		plt.xlabel('Trial (index number)', fontsize=14)
		plt.ylabel('Latency (number of episodes)',fontsize=14)
		plt.show()
		time.sleep(1)
		display.clear_output(wait=True)
		


	########################################################################
	#	Input functions
	########################################################################

	def upload_positions(self):
		# exctract and transform data
		states = pd.read_csv('robot_positions.csv', delimiter=',',header=0).values
		positions = np.array([pd.to_numeric(states[:,0], errors='coerce'),\
							  pd.to_numeric(states[:,1], errors='coerce')]).T
		# Reduce the number of data points
		self.pos = positions[slice(0,positions.shape[0],1000),:]
		N = self.pos.shape[0]
		return self.pos


	def upload_lattice(self,Lfile='SOM_data_lattice.csv'):
		# load data of som-lattice from csv 
		if(self.testfile != 'SOM_data_lattice.csv'): Lfile = self.testfile
		with open(Lfile) as f:
			reader = csv.reader(f)
			next(reader) # skip header
			data = [r for r in reader]
		# calculate Nn
		self.Nn = int(math.sqrt(len(data)))
		# re-create lattice
		self.lattice = np.zeros((self.Nn,self.Nn,2))
		for i,line in enumerate(data):
			x = int(float(line[0])); y = int(float(line[1]))
			self.lattice[x,y,0] = line[2]
			self.lattice[x,y,1] = line[3]
		return self.lattice

	
	def upload_reward(self):
		# load data of som-lattice from csv 
		with open("SOM_possible_actions.csv") as f:
			reader = csv.reader(f)
			next(reader) # skip header
			data = [r for r in reader]
		# calculate Nn
		self.Nn = len(data)
		# re-create Reward
		Reward = []
		for i,line in enumerate(data):
			reward = []
			for j in range(1,self.Nn+1):
    				if(len(line[j])%2==0)and(len(line[j])>2):
        				reward_position = [i,j-1]; line[j] = line[j].replace(" [", "[")
    				cell =  line[j]
    				cell =  literal_eval(cell)
				reward.append(cell)
    			Reward.append(reward)
		return Reward, reward_position
	
	
	
	def upload_Qvalue(self):        
		# load data of som-lattice from csv 
		with open("SARSA_data_Qvalue.csv") as f:
			reader = csv.reader(f)
			next(reader) # skip header
			data = [r for r in reader]
		# calculate Nn
		self.Nn = int(math.sqrt(len(data)/4))
		# re-create lattice
		self.Q = np.zeros((self.Nn,self.Nn,4))
		for i,line in enumerate(data):
			z = line[0]; y = line[1]; x = line[2];
			self.Q[x,y,z] = line[3]


	########################################################################
	#	Output functions
	########################################################################
	
	### Q-VALUE
	
	def save_Qvalue(self,Q):
		# convert it to stacked format using Pandas
		stacked = pd.Panel(Q.swapaxes(1,2)).to_frame().stack().reset_index()
		stacked.columns = ['Direction', 'Coordinate X', 'Coordinate Y', 'Q-value']
		# save to disk
		stacked.to_csv('SARSA_data_Qvalue.csv', index=False)
        
	
	def print_Qvalue(self,Q,goal,actions,csv_file='SOM_data_lattice.csv'):
					
		def background_gradient(s, m, M, cmap='PuBu', low=0, high=0, goal=0.0):
			rng = M - m
			norm = colors.Normalize(m - (rng * low),
			M + (rng * high))
			normed = norm(s.values)
			gnorm = norm(goal)
			x = plt.cm.get_cmap(cmap)(0.0);  cb = colors.rgb2hex(x)
			x = plt.cm.get_cmap(cmap)(gnorm); gb = colors.rgb2hex(x)
			c = [colors.rgb2hex(x) for x in plt.cm.get_cmap(cmap)(normed)]
			return [ 'background-color: black' if color==cb else 'background-color: lime' if color==gb else 'background-color: %s' % color for color in c ]
		
		def border_negative(val):
			vali = (val - np.round(val,6))*10**6
			vali = np.round(vali,4)
			color = {vali == 0.4321: 'none', vali==val: 'solid solid solid solid', \
				 vali == 0.21: 'none solid none solid', \
				 vali == 0.31: 'solid none none solid', \
				 vali == 0.41: 'solid solid none none', \
				 
				 vali == 0.32: 'none none solid solid', \
				 vali == 0.42: 'none solid solid none', \
				 
				 vali == 0.43: 'solid none solid none', \
				 
				 vali == 0.1: 'solid solid none solid', \
				 vali == 0.2: 'none solid solid solid', \
				 vali == 0.3: 'solid none solid solid', \
				 vali == 0.4: 'solid solid solid none', \
				 
				 vali == 0.321: 'none none none solid', \
				 vali == 0.432: 'none none solid none', \
				 vali == 0.421: 'none solid none none', \
				 vali == 0.431: 'solid none none none'}.get(True, 'none')
			return 'border-style: %s' % color

		heatmap = np.zeros((Q.shape[0],Q.shape[0]))
		for i in range(Q.shape[0]):
			for j in range(Q.shape[0]):
				ind = np.argmax(Q[i,j,:])
				heatmap[i,j] = max(Q[i,j,:])
		
		outheat = np.zeros((Q.shape[0],Q.shape[0]), dtype=float)
		for i in range(Q.shape[0]):
			for j in range(Q.shape[0]):
				act = actions[i][j]
				num = 0
				for l in range(len(act)):
				    num = num + (act[l]+1)*10**l
				
				heat = heatmap[i][j]
				heat = np.round(heat,6)
				heat = heat + num*10**(-(6+len(act)))
				outheat[i,j] = heat
				
		outheat[goal[0],goal[1]] = outheat[goal[0],goal[1]]+(np.random.randint(2,size=1)*2-1)*0.9
		gvalue  = outheat[goal[0],goal[1]]
		
		if(csv_file=='SOM_data_lattice.csv'): print "You can see just below the table of average expected reward (Q-value) at each possible state. This table represents that expected reward is increasing as you move closer to the goal at the same time states within 'walls' don't have any expected reward, bacause they cannot be reached. Also, you can see that expected reward in the state of goal is less than on previous states. The reason is that making step from the goal state to anyother you will be one step away from goal again as well as on other such positions."
				
		df = pd.DataFrame(outheat); df.columns.name = 'Q';
		df = df.style.applymap(border_negative).apply(background_gradient, cmap='PuBu', m=df.min().min(), M=df.max().max(),low=0,high=0.2, goal=gvalue).set_properties(**{'width': '100px', 'border': '3px 1px black solid !important', 'color': 'black !important'});
		if(csv_file=='SOM_data_lattice.csv'): display.display(df)

			
	def sarsa_preparation(self,trials,visualization):
		from IPython import display
		from ipywidgets import IntProgress
		mode = ['simulation','environment', 'square_maze', 'latency', 'grading']
		
		
		# ERROR: there are only two available modes: 'simualtion' or 'visualization' 
		visualization = mode.index(visualization)
		
		
		video = visualization
		#if(video==2): Nn = 12
		T = time.time()
		f = IntProgress(min=0, max=trials) # instantiate the bar
		display.display(f) # display the bar
		return T,f
			
		
	def visualization(self, Nn, trial, N_trials, Q, latency_list, latency, visualization, simdata, actdata, Rdata, Sdata, Qdata, f):
		mode = ['simulation','environment', 'square_maze', 'latency', 'grading']
		
		# ERROR: there isn't any available mode with this name 
		# Program cannot define an index for further processing
		visualization = mode.index(visualization)
		# 1) 'simulation' - only simulation of SOM training
		# 2) 'vizualization' - visualize and update a current SOM state 
		
		video = visualization
		#f.value += 1
		
		# Add latency of last trial and visualize latency 
		if(trial%1000==0 or trial==N_trials): self.save_Qvalue(Q)
		latency_list.append(latency)
		
		if(video == 3):
			# visualization of training bumped into a w
			if(0 < video < 3): 
				self.visualization_main(video, simdata, actdata, Rdata, Sdata, Qdata)
			# visualization of latency
			if(video == 3):
				if(trial%int(N_trials/25)==0 or trial==N_trials-1):    
					self.latency(latency_list,N_trials,Nn)
					time.sleep(0.5)
			
		if((trial+1)%1000==0 or trial==N_trials):f.value += 1000 # signal to increment the progress bar
           
		return latency_list
		

	def maze_visualization(self, Nn, trial, N_trials, latency_list, visualization, simdata, actdata, Rdata, Sdata, Qdata):
		mode = ['simulation','environment', 'square_maze', 'latency', 'grading']
		
		# ERROR: there isn't any available mode with this name 
		# Program cannot define an index for further processing
		visualization = mode.index(visualization)
		# 1) 'simulation' - only simulation of SOM training
		# 2) 'vizualization' - visualize and update a current SOM state 
		
		video = visualization
		
		# visualization of training bumped into a w
		if(0 < video < 3): 
			self.visualization(video, simdata, actdata, Rdata, Sdata, Qdata)
		# visualization of latency
		if(video == 3):
			if(trial%int(N_trials/25)==0 or trial==N_trials-1):    
				self.latency(latency_list,N_trials,Nn)
				time.sleep(0.5)
		
		
	def display_results(self, visualization, T, Q, reward_position, Actions, csv_file):
		mode = ['simulation','environment', 'square_maze', 'latency', 'grading']
		self.Q = Q
		self.reward_position = reward_position
		self.Actions = Actions
		self.csv_file = csv_file
		
		
		# ERROR: there are only two available modes: 'simualtion' or 'visualization' 
		visualization = mode.index(visualization)
		
		
		video = visualization
		#display.clear_output(wait=True)
		self.print_Qvalue(self.Q, self.reward_position, self.Actions, self.csv_file)
		if(video < 4): print 'Done. Simulation time is ', time.time()-T, '(s).'
