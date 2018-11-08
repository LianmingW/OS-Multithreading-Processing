import threading
from threading import Lock,Thread

# Merge Functions
def merge_files(filename,mutex):
# Lock when entering the critical region
	mutex.acquire()
	print(threading.current_thread(), "now merging files")
	merge = []
	try:
		# Open the main_data file and the new data file
		with open('main_data_file.txt','r') as mainfile, open(filename,'r') as infile:
			#Because we have \n in our data files, we get rid of that by split the input and only take the first element
			#This is possiblle as we only have int\n in each line, so the first element is definitely our input data
			for line in infile:
				merge.append(line.split()[0])
								
			for line in mainfile:
				merge.append(line.split()[0])
			#Sort the result in ascending order
			merge.sort(key=int)
			#Write the result back to our main_file				
			with open('main_data_file.txt','w') as outfile:
				for elt in merge:
					outfile.write(elt)
					outfile.write("\n")
	except:
		print("Error occurs when merge data!")
		
	# The finally keyword release the lock even if exceptions are thrown, make sure we release the lock
	finally:			
		print(filename,"successfully merged!")
		mutex.release()




filenames =[

	'new_data_1.txt',
	'new_data_2.txt',
	'new_data_3.txt',
]
# Main data
main_data = [
1,
3,
4,
9,
17,
23,
26,
27,
29,
31,
33,
34,
44,
47,
53,
56,
57,
61,
67,
69,
70,
71,
74,
77,
79,
80,
84,
85,
87,
97
]


if __name__ == '__main__':
	# we overwrite main file with it's initial value so we don't need to edit the main file each time we run this program
	with open("main_data_file.txt","w+") as outfile:
		for elt in main_data:
			outfile.write(str(elt))
			outfile.write("\n")

	mutex = Lock()
	# Create 3 threads and run them simutaniously each with the access to critical region, so race condition would occur without lock
	try: 
		mutex.acquire()
		t1 = Thread(target = merge_files, args = (filenames[0],mutex))
		t2 = Thread(target = merge_files, args = (filenames[1],mutex))
		t3 = Thread(target = merge_files, args = (filenames[2],mutex))
		t1.start()
		t2.start()
		t3.start()
	except:
		print("Error in creating threads!")
	# Finally keyword enable us to release the lock even if exception occured, so we don't waste the CPU time to check the lock after excecption
	finally:
		mutex.release()

	# Terminate the threads after finishing work
	t1.join()
	t2.join()
	t3.join()




