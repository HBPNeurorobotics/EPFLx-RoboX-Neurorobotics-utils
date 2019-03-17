# class SARSA_additional

import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import collections as mc
from matplotlib import patches
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


class SARSA_additional():
    
	def __init__(self):
    
		import warnings; warnings.filterwarnings('ignore')
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
		#reward = self.reward_data(states,actions)

		# visualization (Maze: 2 Modes; Reward: Table)
		self.visualization1(states,actions)	# Mode 1
		self.visualization2(states,actions,self.test)	# Mode 2
		reward = self.reward_goal(states,reward)
		choice = self.choice_data(states,actions)

		## reward
		self.save_reward(reward)
		self.print_reward(reward)			# Table

		return reward, choice
    

	### Test analysis program
	def test_analysis(self,goal,test):
		self.input = False
		self.s_goal = goal
		# SOM pre-processing
		self.upload_positions()
		self.upload_lattice(test)
		self.net_details()

		# SOM analyse (to generate maze and reward)
		## maze
		states = self.rewarded_states()
		actions = self.rewarded_actions(states)

		## reward
		#reward = self.reward_data(states,actions)
		reward = self.reward_goal(states,reward)
		choice = self.choice_data(states,actions)
		self.save_reward(reward)
		#self.print_reward(reward)			# Table

		#return self.Nn, self.lattice, self.pos, reward



	def eva_analysis(self):
		self.upload_positions()
		self.upload_lattice()
		self.net_details()

		# SOM analyse (to generate maze and reward)
		## maze
		states = self.rewarded_states()
		actions = self.rewarded_actions(states)

		Reward, reward_pos = self.upload_reward()
		self.upload_Qvalue() 

		return self.Nn, states, actions, Reward, reward_pos, self.Q


	### Define centers and links of SOM
	def net_details(self):
		# SOM-MAP: centers and edges    
		self.edges = [] # list of links between centers
		self.centers = [] # list of centers
		for i in range(self.Nn):
			for j in range(self.Nn):
				if i > 0:
					self.edges.append([(self.lattice[i-1,j,0], self.lattice[i-1,j,1]),
                                  (self.lattice[i,j,0], self.lattice[i,j,1])])
				if j > 0:
					self.edges.append([(self.lattice[i,j-1,0], self.lattice[i,j-1,1]),
                                      (self.lattice[i,j,0], self.lattice[i,j,1])])

				self.centers.append((self.lattice[i,j,0],self.lattice[i,j,1]))
        

	### Define centers on the internal walls
	def rewarded_states(self):
		# Internal wall outlines:
		#	rect1 = patches.Rectangle((-3.0,-1.0), 1., 2., color='black')
		#	rect2 = patches.Rectangle((-3.0, 1.0), 3., 1., color='black')
		#	rect3 = patches.Rectangle(( 0.0,-2.0), 2., 1., color='black')
		#	rect4 = patches.Rectangle(( 2.0,-2.0), 1., 3., color='black')

		act_pos = np.ones((self.Nn**2))
		for i,center in enumerate(self.centers):
			#rect1
			lx0 = -3.0; lx1 = -2.0; ly0 = -1.0; ly1 = 1.0;
			if((center[0]>=lx0)&(center[0]<=lx1)) & ((center[1]>=ly0)&(center[1]<=ly1)):
				act_pos[i] = 0.0
			#rect2
			lx0 = -3.0; lx1 = 0.0; ly0 = 1.0; ly1 = 2.0;
			if((center[0]>=lx0)&(center[0]<=lx1)) & ((center[1]>=ly0)&(center[1]<=ly1)):
				act_pos[i] = 0.0
			#rect3
			lx0 = 0.0; lx1 = 2.0; ly0 = -2.0; ly1 = -1.0;
			if((center[0]>=lx0)&(center[0]<=lx1)) & ((center[1]>=ly0)&(center[1]<=ly1)):
				act_pos[i] = 0.0
			#rect4
			lx0 = 2.0; lx1 = 3.0; ly0 = -2.0; ly1 = 1.0;
			if((center[0]>=lx0)&(center[0]<=lx1)) & ((center[1]>=ly0)&(center[1]<=ly1)):
				act_pos[i] = 0.0
		
		return act_pos
        

	### Define links crossed the internal walls
	def rewarded_actions(self,states):
		# Evaluation: links
		wall = [[(-3.0,-1.0),(-3.0, 2.0)],
                [(-2.0,-1.0),(-2.0, 2.0)],
                [( 0.0, 1.0),( 0.0, 2.0)],

                [(-3.0, 2.0),( 0.0, 2.0)],
                [(-3.0, 1.0),( 0.0, 1.0)],
                [(-3.0,-1.0),(-2.0,-1.0)],

                [( 3.0, 1.0),( 3.0,-2.0)],
                [( 2.0, 1.0),( 2.0,-2.0)],
                [( 0.0,-1.0),( 0.0,-2.0)],

                [( 3.0,-2.0),( 0.0,-2.0)],
                [( 3.0,-1.0),( 0.0,-1.0)],
                [( 3.0, 1.0),( 2.0, 1.0)]];

		results = []
		Cx,Cy = zip(*self.centers)
		for i,edge in enumerate(self.edges):
			result = False
			for w in range(len(wall)):
				result += self.cross(edge, wall[w])

				idx0 = self.centers.index(edge[0])
				idx1 = self.centers.index(edge[1])

				if(states[idx0]+states[idx1]==0):
					result = True


			results.append(result)
		return results

	### Define the crossing
	def cross(self,link,wall):
		v1 = (wall[1][0]-wall[0][0])*(link[0][1]-wall[0][1]) -\
			 (wall[1][1]-wall[0][1])*(link[0][0]-wall[0][0]);
		v2 = (wall[1][0]-wall[0][0])*(link[1][1]-wall[0][1]) -\
			 (wall[1][1]-wall[0][1])*(link[1][0]-wall[0][0]);
		v3 = (link[1][0]-link[0][0])*(wall[0][1]-link[0][1]) -\
			 (link[1][1]-link[0][1])*(wall[0][0]-link[0][0]);
		v4 = (link[1][0]-link[0][0])*(wall[1][1]-link[0][1]) -\
			 (link[1][1]-link[0][1])*(wall[1][0]-link[0][0]);
		return (v1*v2<0) & (v3*v4<0)



	########################################################################
	#	Reward matrix generation
	########################################################################

    # Define reward as each Q(x,y,a)
	def reward_data(self,states,actions):
		reward = np.zeros((self.Nn,self.Nn,4))
		for i in range(self.Nn):
			for j in range(self.Nn):
				for a in range(4):
					if  (a == 0): ish =  1; jsh =   0;
					elif(a == 1): ish = -1; jsh =   0;
					elif(a == 2): ish =  0; jsh =   1;
					elif(a == 3): ish =  0; jsh =  -1;

					able = self.availability(i,j,i+ish,j+jsh,actions)
					reward[i,j,a] = able 

		for i in range(self.Nn):
			for j in range(self.Nn):
				if(max(reward[i,j,:])==-1.0): 
					states[self.Nn*i+j] = 0.0

		return reward

    # Define reward as each Q(x,y,a)
	def choice_data(self,states,actions):
		reward = [] #np.zeros((self.Nn,self.Nn,4))
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

		def color_negative(val):
			color = {len(val)==2.0: 'darkorange', len(val)==9.0: 'sandybrown'}.get(True, 'orange')
			return 'background-color: %s' % color

		output = np.chararray((self.Nn,self.Nn), itemsize=10)
		for i in range(self.Nn):
			for j in range(self.Nn):
				output[i][j] = '['+','.join(str(e) for e in reward[i*self.Nn+j])+']'

		import pandas as pd
		print 'Possible actions to choose: 0 - Down; 1 - Up; 2 - Right; 3 - Left.'
		df = pd.DataFrame(output); df.columns.name = 'Actions';
		df = df.style.applymap(color_negative).set_properties(**{'width': '100px'});
		display.display(df)

		return reward
	
	
	
	
	
    # Define reward as each Q(x,y,a)
	def reward_goal(self,states,reward):
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


		#if(reward[self.s_goal[0]-1,self.s_goal[1],0] == 0.0): reward[self.s_goal[0]-1,self.s_goal[1],0] = 1.0
		#if(reward[self.s_goal[0]+1,self.s_goal[1],1] == 0.0): reward[self.s_goal[0]+1,self.s_goal[1],1] = 1.0
		#if(reward[self.s_goal[0],self.s_goal[1]-1,2] == 0.0): reward[self.s_goal[0],self.s_goal[1]-1,2] = 1.0
		#if(reward[self.s_goal[0],self.s_goal[1]+1,3] == 0.0): reward[self.s_goal[0],self.s_goal[1]+1,3] = 1.0

		return self.s_goal
    
    # Define the punishment at Q(x,y,a)
	def availability(self,x0,y0,x1,y1,actions):
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
    

    # Define the punishment at Q(x,y,a)
	def available_positions(self,reward):
		avpos = [[] for _ in range(self.Nn**2)]
		for i in range(self.Nn):
			for j in range(self.Nn):
				if(reward[i,j,0] >= 0.0): avpos[i*self.Nn+j].append(0)
				if(reward[i,j,1] >= 0.0): avpos[i*self.Nn+j].append(1)
				if(reward[i,j,2] >= 0.0): avpos[i*self.Nn+j].append(2)
				if(reward[i,j,3] >= 0.0): avpos[i*self.Nn+j].append(3)
		return avpos
    


	########################################################################
	#	Visualization functions
	########################################################################

	def visualization(self, video=1, simdata=[], actdata=[], Rdata=[], Sdata=[], Qdata=[]):
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
			fig1.suptitle('Adapted SOM for SARSA implementation. (Reds are punished)')

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


	def upload_lattice(self,Lfile="SOM_data_lattice.csv"):
		# load data of som-lattice from csv 
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
		with open("SARSA_data_reward.csv") as f:
			reader = csv.reader(f)
			next(reader) # skip header
			data = [r for r in reader]
		# calculate Nn
		self.Nn = int(math.sqrt(len(data)/4))
		# re-create Reward
		Reward = np.zeros((self.Nn,self.Nn,4))
		for i,line in enumerate(data):
			z = line[0]; y = line[1]; x = line[2];
			Reward[x,y,z] = line[3]
			if(Reward[x,y,z] == 1):
				if(int(z)==0): reward_position = [int(x)+1,int(y)]
				if(int(z)==1): reward_position = [int(x)-1,int(y)]
				if(int(z)==2): reward_position = [int(x),int(y)+1]
				if(int(z)==3): reward_position = [int(x),int(y)-1]
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

	### REWARD
	def save_reward(self,reward):
		# convert it to stacked format using Pandas
		stacked = pd.Panel(reward.swapaxes(1,2)).to_frame().stack().reset_index()
		stacked.columns = ['Direction', 'Coordinate X', 'Coordinate Y', 'Reward']
		# save to disk
		stacked.to_csv('SARSA_data_reward.csv', index=False)

	def print_reward(self,reward):
		def highlight_max(s):
			return ['background-color: black' if (v==-1.0) else 'background-color: gold' if (v==1.0) else '' for v in s]
		
		def color_negative(val):
			color = 'white' if val < 0 else 'black'
			return 'color: %s' % color
		
		print "Reward matrix is generated for your maze. Reward structure:"
		
		df = pd.DataFrame(reward[:,:,0]); df.columns.name = 'DOWN_____'; 
		df = df.style.applymap(color_negative).apply(highlight_max).set_properties(**{'width': '100px'}); display.display(df)
		
		df = pd.DataFrame(reward[:,:,1]); df.columns.name = 'UP________'; 
		df = df.style.applymap(color_negative).apply(highlight_max).set_properties(**{'width': '100px'}); display.display(df)
		
		df = pd.DataFrame(reward[:,:,2]); df.columns.name = 'RIGHT_____'; 
		df = df.style.applymap(color_negative).apply(highlight_max).set_properties(**{'width': '100px'}); display.display(df)
		
		df = pd.DataFrame(reward[:,:,3]); df.columns.name = 'LEFT______'; 
		df = df.style.applymap(color_negative).apply(highlight_max).set_properties(**{'width': '100px'}); display.display(df)
		
		raw_input('Press Enter to finish... ')
		clear_output()

	### Q-VALUE
	def save_Qvalue(self,Q):
		# convert it to stacked format using Pandas
		stacked = pd.Panel(Q.swapaxes(1,2)).to_frame().stack().reset_index()
		stacked.columns = ['Direction', 'Coordinate X', 'Coordinate Y', 'Q-value']
		# save to disk
		stacked.to_csv('SARSA_data_Qvalue.csv', index=False)
        
	def print_Qvalue(self,Q,goal):
		print "Result. Navigation heatmap:"
		#print "Up:\n", 
		#for i in range(Q.shape[0]):
		#	print ["%12.8f"% (q) for i,q in enumerate(Q[i,:,0])]

		#print
		#print "Down:\n", 
		#for i in range(Q.shape[0]):
		#	print ["%12.8f"% (q) for i,q in enumerate(Q[i,:,1])]

		#print
		#print "Right:\n", 
		#for i in range(Q.shape[0]):
		#	print ["%12.8f"% (q) for i,q in enumerate(Q[i,:,2])]

		#print
		#print "Left:\n", 
		#for i in range(Q.shape[0]):
		#	print ["%12.8f"% (q) for i,q in enumerate(Q[i,:,3])]


		
		def color_negative(val):
			color = 'black' if val == 0 else 'black'
			return 'color: %s' % color
		
		heatmap = np.zeros((Q.shape[0],Q.shape[0]))
		for i in range(Q.shape[0]):
			for j in range(Q.shape[0]):
				ind = np.argmax(Q[i,j,:])
				if(ind==0): heatmap[i+1,j] = max(Q[i,j,:])
				if(ind==1): heatmap[i-1,j] = max(Q[i,j,:])
				if(ind==2): heatmap[i,j+1] = max(Q[i,j,:])
				if(ind==3): heatmap[i,j-1] = max(Q[i,j,:])
				#heatmap[i,j] = max(Q[i,j,:])

		def background_gradient(s, m, M, cmap='PuBu', low=0, high=0, goal=[0,0]):
			rng = M - m
			norm = colors.Normalize(m - (rng * low),
			M + (rng * high))
			normed = norm(s.values)
			c = [colors.rgb2hex(x) for x in plt.cm.get_cmap(cmap)(normed)]
			bg = ['background-color: %s' % color for color in c]
			print type(bg), bg
			return ['background-color: %s' % color for color in c]
				
		#heatmap[goal[0],goal[1]] = math.inf
		df = pd.DataFrame(heatmap); df.columns.name = 'Q';
		df = df.style.applymap(color_negative).apply(background_gradient, cmap='PuBu', m=df.min().min(), M=df.max().max(),low=0,high=0.2, goal=goal)
		display.display(df)
