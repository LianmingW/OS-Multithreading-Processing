import time
from collections import deque
from statistics import mean

# Class object that stores the PCB information
class PCB:
	def __init__(self,arrival_time,proc,pid,state,priority,interruptable,est_tot_time,est_remain_time):
		self.arrival_time = arrival_time
		self.proc = proc
		self.pid = pid
		self.state = state
		self.priority = priority
		self.interruptable = interruptable
		self.est_tot_time = int(est_tot_time)
		self.est_remain_time = int(est_remain_time)
		self.wait_time = 0
		self.turn_around_time = 0

	def __str__(self):
		string = (self.arrival_time,self.proc,self.pid,self.state,self.priority,self.interruptable,str(self.est_tot_time),str(self.est_remain_time))
		return ','.join(string)

# Scheduler class with process_list and ready_queue buit in, also records number of context switches
class Scheduler:
	def __init__(self,process_list):
		self.process_list = process_list
		self.ready_queue = deque()
		self.number_of_switch = 0

# "Subclass" of scheduler, where the process are actually being executed
class CPU(Scheduler):
	# Current_time records time elapsed
	# Current proc is the process being executed by CPU, initially none
	# A finished process list to store finished process information
	def __init__(self,process_list):
		super().__init__(process_list)
		self.current_time = 0
		self.next_proc = None
		self.current_proc = None
		self.finished_process = []

# If process arrives at the current time, add them to the queue, as the process_list is sorted by the arrival time, no process will be missed
	def check_arrival_time(self):
		if int(self.next_proc.arrival_time) == self.current_time:
				self.process_list.pop(0)
				self.ready_queue.append(self.next_proc)
				if self.process_list:
					self.next_proc = self.process_list[0]

# Increment the stat in the process list
	def increment_stat(self,amount):
		for process in self.ready_queue:
						process.wait_time += amount
						process.turn_around_time += amount

	def print_stat(self):
		# means returns average, we calculate the respective stats based on the finished process queue, those line would only be reached when all process are done running
		average_turnaround = round(mean([process.turn_around_time for process in self.finished_process]) , 3)
		average_wait_time = round(mean([process.wait_time for process in self.finished_process]),3)
		longest_wait_time = max([process.wait_time for process in self.finished_process])

		print("The average_turnaround_time is: "+ str(average_turnaround))
		print("The average_wait_time is: " + str(average_wait_time))
		print("The longest_wait_time is: " + str(longest_wait_time))
		print("Number of Context Switches is: "  + str(self.number_of_switch))
		print("Total time spent: "+ str(self.current_time))

# No Preemption algorithms
	def No_Preemption(self,mode):
		# The first process
		self.next_proc = self.process_list[0]
		# While there is process to enter the queue, there is process in the queue, there is a process running in CPU, keep the CPU running
		while self.process_list or self.ready_queue or self.current_proc:
			# If process arrives at the current time, add them to the queue, as the process_list is sorted by the arrival time, no process will be missed
			self.check_arrival_time()
			# If there is nothing run by the CPU and there are process in the ready queue, sort the queue by different modes, so the next process we pop from queue would fit the criteria
			if self.current_proc is None and self.ready_queue:
				if mode == "SJN":
					self.ready_queue = deque(sorted(self.ready_queue,key = shortest_job))
				elif mode == "Priority":
					self.ready_queue = deque(sorted(self.ready_queue,key = priority))
				self.current_proc = self.ready_queue.popleft()
			# If there is process running by CPU and remain time is not 0, decrement the remain time, increment the turn around time. Also adjust the wait time and turn around time
			# for all process in the ready queue respectively
			if self.current_proc and self.current_proc.est_remain_time != 0:
				self.current_proc.est_remain_time -=1
				self.current_proc.turn_around_time +=1
				if self.ready_queue:
					self.increment_stat(1)
			# If a process finishes running, we increment the number of context switches and increment stats accordingly, then we add the process to finished process list and set 
			# current running process to none
			if self.current_proc and self.current_proc.est_remain_time == 0:
				print(self.current_proc.proc + " is finished at time: " + str(self.current_time) + " with turn_around_time: " + str(self.current_proc.turn_around_time))
				self.number_of_switch +=1
				self.current_time +=2
				# Make sure we don't miss a process because of context switching 
				self.check_arrival_time()
				if self.ready_queue:
					self.increment_stat(2)
				self.finished_process.append(self.current_proc)
				self.current_proc = None

			# No matter what happens after each cycle, increment the current time
			self.current_time += 1
		# Print the stat when all process finished running
		self.print_stat()
		with open("./data.txt","a") as outfile:
			outfile.write("No_Preemption,{},{}\n".format(mode,round(mean([process.wait_time for process in self.finished_process]),3)))

	# Round Robin methods
	def Round_Robin(self,mode,quanta):
		# A variable that keep tracks of the current quanta
		current_quanta = quanta
		self.next_proc = self.process_list[0]
		# While there is process to enter the queue, there is process in the queue, there is a process running in CPU, keep the CPU running
		while self.process_list or self.ready_queue or self.current_proc:
			# If process arrives at the current time, add them to the queue, as the process_list is sorted by the arrival time, no process will be missed
			self.check_arrival_time()

			# Add new process from the ready queue to CPU if CPU is free
			if self.current_proc is None and self.ready_queue:
				if mode == "SRTN":
					self.ready_queue = deque(sorted(self.ready_queue,key = shortest_remaining))
				elif mode == "Priority":
					self.ready_queue = deque(sorted(self.ready_queue,key = priority))
				self.current_proc = self.ready_queue.popleft()

			# If current quanta is 0 and current process isn't finsihed, and there is process in queue(so if there is only one process left, we just keep it running, doesn't trigger
			# context switch) we trigger the context switch
			if current_quanta == 0 and self.ready_queue and self.current_proc.est_remain_time !=0:
				# Add the current process back to the queue
				self.ready_queue.append(self.current_proc)
				# increment context switch number and current_time
				# To not miss job in between context switch, we check arrival time
				self.number_of_switch +=1
				self.current_time +=2
				self.check_arrival_time()
				# Reset the quanta to original and increment_stat, change the current proc to none
				current_quanta = quanta
				self.increment_stat(2)
				self.current_proc = None

			# If there is still quanta left, adjust the stat accordingly, also decrement the current_quanta by 1
			if self.current_proc and self.current_proc.est_remain_time != 0:
				self.current_proc.est_remain_time -=1
				self.current_proc.turn_around_time +=1
				current_quanta -= 1
				if self.ready_queue:
					self.increment_stat(1)

			# If curr process finish running, reset quanta, put curr process into finished, adjust stats accordingly, set curr_process to none
			if self.current_proc and self.current_proc.est_remain_time == 0:
				print(self.current_proc.proc + " is finished at time: " + str(self.current_time) + " with turn_around_time: " + str(self.current_proc.turn_around_time))
				self.number_of_switch +=1
				self.current_time +=2
				if self.ready_queue:
					self.increment_stat(2)
				current_quanta = quanta
				self.finished_process.append(self.current_proc)
				self.current_proc = None

			self.current_time += 1

		self.print_stat()
		with open("./data.txt","a") as outfile:
			outfile.write("Round_Robin,{},{},{}\n".format(mode,quanta,round(mean([process.wait_time for process in self.finished_process]),3)))



rrmode = ["FCFS","SRTN","Priority"]
No_Preemption_mode = ["FCFS","SJN","Priority","RR"]


# Comparators, return in a list form, so if the first parameter is the same, we check their arrival time next
def shortest_job(process):
	return process.est_tot_time,process.arrival_time

def priority(process):
	return process.priority,process.arrival_time

def shortest_remaining(process):
	return process.est_remain_time,process.arrival_time

# Main function
def main():
	with open("./processes_3.txt") as infile:
		lines = infile.read().split('\n')

	# list of processes (not including the header line).
		process_list = []
	# I don't know why their is an empty line at the end of "lines", causing error, so I added -1 to get rid of that.
	# Make data a PCB object, and push them into the process list
		for line in lines[1:-1]:
			var = line.split(',')
			pcb = PCB(*var)
			process_list.append(pcb)

		cpu = CPU(process_list)

		# Selections
		selection = input("Enter your selection:")
		if (selection in ["FCFS","fcfs"]):
			cpu.No_Preemption("FCFS")
		elif(selection in ["SJN","sjn"]):
			cpu.No_Preemption("SJN")
		elif(selection in ["Priority","priority"]):
			cpu.No_Preemption("Priority")
		elif(selection in ["RR","rr"]):
			quanta = int(input("Enter the quanta: "))
			mode = input("Enter your mode: ")
			if (mode in ["FCFS","fcfs"]):
				cpu.Round_Robin(mode,quanta)
			elif(mode in ["SRTN","srtn"]):
				cpu.Round_Robin("SRTN",quanta)
			elif(mode in ["Priority","priority"]):
				cpu.Round_Robin("Priority",quanta)
			else:
				print("Please select from belowing modes:")
				print(rrmode)
		else:
			print("Please select from belowing modes:")
			print(No_Preemption_mode)




if __name__ == '__main__':
	main()




