import os

import carver_common

def query_partitions_table_db(db_info):  
    	db_info["db_cursor"].execute("SELECT * FROM partitions")
	print_partition_query_db(db_info)
	return;

def query_partition_name_db(db_info, string):
	db_query = "SELECT * FROM partitions WHERE name LIKE ?"
	db_info["db_cursor"].execute(db_query, ('%'+string+'%',))
	print_partition_query_db(db_info)
	return;

def print_partition_query_db(db_info):
	print "\n%10s %10s %10s" % ('Name', 'Start', 'Stop')
	while True:
		file = db_info["db_cursor"].fetchone()
		if file == None:
           		break
		print "%10s %10s %10s" % (file[0], file[2], file[3])	
	return;

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