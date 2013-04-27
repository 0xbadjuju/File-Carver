import re
import os
import subprocess

import carver_common

def query_files_table_db(db_info):  
    	db_info["db_cursor"].execute("SELECT * FROM files")
	print_file_query_db(db_info)
	return;

def query_name_db(db_info, string):
	db_query = "SELECT * FROM files WHERE name LIKE ?"
	db_info["db_cursor"].execute(db_query, ('%'+string+'%',))
	print_file_query_db(db_info)
	return;

def query_inode_db(db_info, string):
	db_query = "SELECT * FROM files WHERE inode LIKE ?"
	db_info["db_cursor"].execute(db_query, ('%'+string+'%',))
	print_file_query_db(db_info)
	return;

def query_file_number_db(db_info, string):
	db_query = "SELECT * FROM files WHERE file_number LIKE ?"
	db_info["db_cursor"].execute(db_query, ('%'+string+'%',))
	print_file_query_db(db_info)
	return;


def print_file_query_db(db_info):
	print "\n%-10s %-30s %5s" % ("Index", "File Name", "Inode")
	while True:
		file = db_info["db_cursor"].fetchone()
		if file == None:
           		break
		print "%-10s %-30s %5s" % (file[2], file[0], file[1])
	return;

def insert_file_list_db(db_info, image):
	iteration = 0
	sub_process = subprocess.Popen( "fls -prlo 32 "+image, shell=True, stdout=subprocess.PIPE )
	while True:
		single_file = sub_process.stdout.readline()
		if single_file != '':
			single_file = single_file.split()
			if single_file[0] == 'r/r':
				iteration+=1
				if single_file[1] == "*":
					single_file[2] = re.sub(":", "",single_file[2])
					file_info = [(single_file[3], single_file[2], iteration)]
				else:
					single_file[1] = re.sub(":", "",single_file[1])
					file_info = [(single_file[2], single_file[1], iteration)]
				db_info["db_cursor"].executemany("INSERT INTO files VALUES (?,?,?)", file_info)
				db_info["db_connect"].commit()
		else:
			break
	return;

def carve_file(db_info, image, string):
	#icat = icat -o 32 image offset + " > " + output
	db_query = "SELECT * FROM files WHERE name LIKE ?"
	db_info["db_cursor"].execute(db_query,('%'+string+'%',))
	carve = db_info["db_cursor"].fetchone()
	out_file = re.sub('.*/','',carve[0])
	icat = "icat -o 32 "+image+" "+str(carve[1])+" > "+out_file
	carver_common.ipc_shell(icat)
	print "File duplicated to "+os.getcwd()+"/"+out_file
	return;