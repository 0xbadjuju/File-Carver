import os

import carver_common

################################################################################
# Function:	 query_partitions_table_db(db_info)
# Variables: db_info  
# Prints the entire partition table from the database
################################################################################
def query_partitions_table_db(db_info):  
    	db_info["db_cursor"].execute("SELECT * FROM partitions")
	print_partition_query_db(db_info)
	return;

################################################################################
# Function:	 query_partition_name_db(db_info, string)
# Variables: db_info 
# Searches database for a given partition name
################################################################################
def query_partition_name_db(db_info, string):
	db_query = "SELECT * FROM partitions WHERE name LIKE ?"
	db_info["db_cursor"].execute(db_query, ('%'+string+'%',))
	print_partition_query_db(db_info)
	return;

################################################################################
# Function:	 print_partition_query_db(db_info)
# Variables: db_info, partition
# Common function for printing partition information from the database
################################################################################
def print_partition_query_db(db_info):
	print "\n%-10s %-10s %-10s" % ('Name', 'Start', 'Stop')
	while True:
		partition = db_info["db_cursor"].fetchone()
		if partition == None:
           		break
		print "%-10s %-10s %-10s" % (partition[0], partition[2], partition[3])	
	return;

################################################################################
# Function:	 carve_partition(db_info, image, string)
# Variables: db_info, string, image, carve, dd_command
# Carves a single partition from the image using dd
################################################################################
def carve_partition(db_info, image, string):
	db_info["db_cursor"].execute("SELECT * FROM partitions")
	db_query = "SELECT * FROM partitions WHERE name LIKE ?"
	db_info["db_cursor"].execute(db_query,('%'+string+'%',))
	carve = db_info["db_cursor"].fetchone()
	dd_command = "dd if="+image+" of="+carve[0]+".carved bs=512 skip="+str(carve[2])+" count="+str((carve[3]-carve[2]))
	print "Running "+dd_command
	carver_common.ipc_shell(dd_command)
	print "Partition duplicated to "+os.getcwd()+"/"+carve[0]+".dd"
	return;