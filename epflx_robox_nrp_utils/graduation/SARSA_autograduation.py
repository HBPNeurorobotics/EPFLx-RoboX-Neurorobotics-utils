import numpy as np 
import pandas as pd
import os, fnmatch, shutil
import time
import importlib
import csv
import operator
import signal

from IPython.display import clear_output


class SARSA_autograduation():
    

	def __init__(self):
    
		import warnings; warnings.filterwarnings('ignore')
		from epflx_robox_nrp_utils.SARSA.SARSA_evaluation import SARSA_evaluation
		self.sarsaev = SARSA_evaluation()
		from epflx_robox_nrp_utils.SARSA.SARSA_additional import SARSA_additional
		self.sarsaad = SARSA_additional()

		# initialize the parameters of test (Map size and Number of trials)
		self.N = 1
		self.tau = 100.0
		self.limit = 120.0 # only integer value

		self.user = {}
		self.G = [[2,7],[6,7],[7,7]]
		self.varis = np.zeros((3))
		self.vours = np.zeros((3))
		self.notes = np.zeros((3))


	
	########################################################
	'''     Mode 2 - Evaluate ONE submitted solution     '''
	########################################################

	def graduate_one_function(self, funcname):
		score = []
		func, self.user = self.user_function(funcname)
		self.message = ""
		
		# upload solution
		try: SARSA = self.upload_solution(func,True); load = True
		except: score = "FAILED uploading..."; load = False
		
		if(load):
			for t in range(3):
				self.goal = self.G[t]
				test = 'SOM_test'+str(t+1)+'_lattice.csv'
				script_path = os.path.dirname(os.path.abspath( __file__ ))
				test = os.path.join(script_path,test)
				self.sarsaad.test_analysis(self.goal,test)
				text = 'Test '+str(t+1)+'/3...'
				print text #test

				sumwayF = 0.0
				for e in range(1):
					# initialize crucial requirement from student's function
					# Function is compiling (work) and simulating within time limit (inlim)
					work = True; inlim = True

					# Evaluation of function based on one of tests
					# Function gives back a final variation achieved during a test  

					# import student's function and test data
					#try: 
					sarsa = SARSA(4,test) # sarsa = SARSA(Nn x Nn (lattice), tau, visualization, data file)
					#except: work = False

					# set simulation time limit for the cases script doesn't work properly:
					# 1) script consists of endless loop
					# 2) script is simulating for a very long time
					signal.signal(signal.SIGALRM, self.handler)
					signal.alarm(int(self.limit))
					T = time.time()

					# run simulation of test
					try: sarsa.run_sarsa()
					except Exception, exc: inlim = False
					signal.alarm(0) # disable alarm

					# Challenge if script was simulating properly during all simulation time
					# if script was interrupted because of time limit, the current result had been saved for evaluation and graduation (work = True)
					# if script was interrupted before time limit it means there is another error of simulation (work = False)
					if(time.time()-T < self.limit and inlim==False): work = False; inlim = True

					# calculate variation of given test result
					if(work):     # Script was working properly or not (within time limit or not) 
						# Estimate SARSA by test
						from epflx_robox_nrp_utils.SARSA.SARSA_evaluation import SARSA_evaluation
						sarsaev = SARSA_evaluation()
						fastwayF, longwayF, overwayF, neverwayF = sarsaev.run_evaluation(0,test)
						sumwayF = 1*fastwayF+(1-0.55+longwayF/max(overwayF,0.01))*longwayF+0*neverwayF
					else:         # Script doesn't work / doesn't work properly
						# put punished value
						fastwayF=0.001; longwayF=0.001; overwayF=0.001; neverwayF=0.001;
						sumwayF = 1*fastwayF+(1-0.55+longwayF/max(overwayF,0.01))*longwayF+0*neverwayF

				if(work):
					if(inlim): 	self.message += str(t+1) + ") Program worked properly and it has been estimated.  "
					else: 		self.message += str(t+1) + ") Program had been interrupted by time limit but a current result was estimated.  "
				else: 			self.message += str(t+1) + ") Program failed during simulation.  "
				
				# Notes
				score.append(sumwayF)
				clear_output()
		
		# Save evaluation
		#print self.message
		#time.sleep(20)
		return score


	
	#############################################
	###     Mode 2 - Additional functions     ###
	#############################################

	# extract function and student's names from file name
	def user_function(self, name):
		func = name.replace(".py", "")
		user = func.replace("SARSA_", "")
		user = user.replace("_", " ")
		return func, user
		

	# upload function with student's solution
	def upload_solution(self, func, rank):
		module = importlib.import_module(func)
		SARSA = getattr(module, 'SARSA')
		return SARSA


	# define that test simulation time is over
	def handler(self, signum, frame):
		raise Exception("end of time")
