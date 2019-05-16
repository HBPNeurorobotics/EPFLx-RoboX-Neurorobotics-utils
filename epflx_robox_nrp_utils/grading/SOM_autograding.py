import numpy as np 
import pandas as pd
import os, fnmatch
import time
import importlib
import csv
import operator
import signal

from IPython.display import clear_output



class SOM_autograding():
    

	def __init__(self):
		
		import warnings; warnings.filterwarnings('ignore')
		
		# initialize the parameters of test (Map size and Number of trials)
		self.N = 1
		self.L = 12
		self.tau = 100.0
		self.limit = 120 # (s) only integer value
		
		self.user = {}
		self.message = ""
		self.varis = np.zeros((3))
		self.vours = np.zeros((3))
		self.notes = np.zeros((3))

		

	########################################################
	'''     Mode 2 - Evaluate ONE submitted solution     '''
	########################################################

	def grade_one_function(self, funcname):
		score = []
		func, self.user = self.user_function(funcname)
		self.message = ""
		
		#try: 
		SOM = self.upload_solution(func,True); load = True
		#except: score = "FAILED uploading..."; load = False
		
		if(load):
			for t in range(3):
				# define name of file with test-data
				test = 'NRP_test'+str(t+1)+'_robot_position.csv'
				script_path = os.path.dirname(os.path.abspath( __file__ ))
				test = os.path.join(script_path,test)
				text = 'Grading process: Test '+str(t+1)+'/3...'
				print text #test
			
			
				variF = 2000.0
				for e in range(self.N):
					#print "Epoche", e
				
					# initialize crucial requirement from student's function
					# Function is compiling (work) and simulating within time limit (inlim)
					work = True; inlim = True
				
					# Evaluation of function based on one of tests
					# Function gives back a final variation achieved during a test  
				
					# import student's function and test data
					try: som = SOM('grading',test) # som = SOM(Nn x Nn (lattice), tau, visualization, data file)
					except: work = False
				
					# set simulation time limit for the cases script doesn't work properly:
					# 1) script consists of endless loop
					# 2) script is simulating for a very long time
					signal.signal(signal.SIGALRM, self.handler)
					signal.alarm(int(self.limit))
					T = time.time()
					
					# run simulation of test
					try: som.run_som()
					except Exception, exc: inlim = False
					signal.alarm(0) # disable alarm
				
					# Challenge if script was simulating properly during all simulation time
					# if script was interrupted because of time limit, the current result had been saved for evaluation and grading (work = True)
					# if script was interrupted before time limit it means there is another error of simulation (work = False)
					if(time.time()-T < self.limit and inlim==False): work = False; inlim = True

					# calculate variation of given test result
					if(work):     # Script was working properly or not (within time limit or not) 
						# Estimate SOM by test
						from epflx_robox_nrp_utils.SOM.SOM_evaluation import SOM_evaluation
						somev = SOM_evaluation(test)
						vF, Nn = somev.run_evaluation()
						if(Nn==self.L): variF = min(vF,variF)
						else: variF = 1212.0
					else:         # Script doesn't work / doesn't work properly
						# put punished value
						variF = 1000.0

					
					
				if(variF < 1000.0):	
					if(inlim): 			self.message += str(t+1) + ") Program worked properly and it has been estimated.  "
					else: 				self.message += str(t+1) + ") Program had been interrupted by time limit but a current result was estimated.  "
				elif(variF == 1212.0): 	self.message += str(t+1) + ") Program is working properly, but SOM size is not 8x8.  "
				elif(variF == 1000.0): 	self.message += str(t+1) + ") Program failed during simulation.  "
				else: 					self.message += str(t+1) + ") Cannot upload solution function.  "

				# Notes
				#print t, " : ", variF
				score.append(variF)
				#time.sleep(5)
				clear_output()
			
		# Save grading
		###print self.message
		return score



	#############################################
	###     Mode 2 - Additional functions     ###
	#############################################

	# extract function and student's names from file name
	def user_function(self, name):
		func = name.replace(".py", "")
		user = func.replace("SOM_", "")
		user = user.replace("_", " ")
		return func, user


	# upload function with student's solution
	def upload_solution(self, func, rank):
		module = importlib.import_module(func)
		SOM = getattr(module, 'SOM')
		return SOM


	# define that test simulation time is over
	def handler(self, signum, frame):
		raise Exception("End of time")
		
