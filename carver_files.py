import re
import os
import subprocess

import carver_common

################################################################################
# Function:	 query_files_table_db(db_info)
# Variables: db_info  
# Prints the entire file table from the database
################################################################################
def query_files_table_db(db_info):  
    	db_info["db_cursor"].execute("SELECT * FROM files")
	print_file_query_db(db_info)
	return;

################################################################################
# Function:	 query_name_db(db_info, string)
# Variables: db_info, string
# Searches the database for particular file name
################################################################################
def query_name_db(db_info, string):
	db_query = "SELECT * FROM files WHERE name LIKE ?"
	db_info["db_cursor"].execute(db_query, ('%'+string+'%',))
	print_file_query_db(db_info)
	return;

################################################################################
# Function:	 query_inode_db(db_info, string)
# Variables: db_info, string  
# Searches the database for particular file at a given inode
################################################################################
def query_inode_db(db_info, string):
	db_query = "SELECT * FROM files WHERE inode LIKE ?"
	db_info["db_cursor"].execute(db_query, ('%'+string+'%',))
	print_file_query_db(db_info)
	return;

################################################################################
# Function:	 query_file_number_db(db_info, string)
# Variables: db_info, string 
# Searches the database for particular file at a location in the database
################################################################################
def query_file_number_db(db_info, string):
	db_query = "SELECT * FROM files WHERE file_number LIKE ?"
	db_info["db_cursor"].execute(db_query, ('%'+string+'%',))
	print_file_query_db(db_info)
	return;

################################################################################
# Function:	 print_file_query_db(db_info)
# Variables: db_info, file
# Common function for printing file information from the database
################################################################################
def print_file_query_db(db_info):
	print "\n%-10s %-30s %5s" % ("Index", "File Name", "Location")
	while True:
		file = db_info["db_cursor"].fetchone()
		if file == None:
           		break
		print "%-10s %-30s %5s" % (file[2], file[0], file[1])
	print "\n"
	return;

################################################################################
# Function:	 carve_file(db_info, image, string)
# Variables: db_info, image, string, out_file, icat
# Carves files from the image file a folder within the current working directory
################################################################################
def carve_file(db_info, image, string):
	#icat = icat -o 32 image offset + " > " + output
	db_query = "SELECT * FROM files WHERE name LIKE ?"
	db_info["db_cursor"].execute(db_query,('%'+string+'%',))
	new_directory = image+"_"+string+"_"+str(carver_common.get_time(image))
	carver_common.make_directory(new_directory, image)
	log = open(os.getcwd()+"/"+new_directory+"/log","a")
	while True:
		carve = db_info["db_cursor"].fetchone()
		if carve != None:
			if re.match('.*/', carve[0]):
				out_file = re.sub('.*/','',carve[0])
			else:
				out_file = carve[0]
			icat = "icat -o "+str(carve[3])+" "+image+" "+str(carve[1])+" > "+new_directory+"/"+out_file
			carver_common.ipc_shell(icat)
			hash = carver_common.hashfile(new_directory+"/"+out_file)
			print "File duplicated to "+os.getcwd()+"/"+new_directory+"/"+out_file
			print "\t MD5:  "+hash[0]
			print "\t SHA1: "+hash[1]+"\n"
			try:
				log.write(out_file+"\n\tMD5:  "+hash[0]+"\n\tSHA1: "+hash[1])
			except OSError:
				pass
		else:
			break
	log.close()
	print "\n"
	return;