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

def carve_file(db_info, image, string):
	#icat = icat -o 32 image offset + " > " + output
	db_query = "SELECT * FROM files WHERE name LIKE ?"
	db_info["db_cursor"].execute(db_query,('%'+string+'%',))
	carve = db_info["db_cursor"].fetchone()
	out_file = re.sub('.*/','',carve[0])
	icat = "icat -o "+str(carve[3])+" "+image+" "+str(carve[1])+" > "+out_file
	carver_common.ipc_shell(icat)
	print "File duplicated to "+os.getcwd()+"/"+out_file
	return;