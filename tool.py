#!/usr/bin/python

import subprocess
import sys
import re
import os
import hashlib
import sqlite3

def ipc_shell(shell_command):
	try:
		sub_process = subprocess.Popen( shell_command, shell=True, stdout=subprocess.PIPE )
		(std_out, std_err) = sub_process.communicate()
	except OSError as error:
		print "Command Failed:", error
	std_out = std_out.splitlines()
	return std_out;

def hashfile():
	md5 = hashlib.md5()
	sha1 = hashlib.sha1()
	file_to_hash = open(sys.argv[1], "rb")
	while True:
		file_chunk = file_to_hash.read(128)
		if not file_chunk:
			break
		md5.update(file_chunk)
		sha1.update(file_chunk)
	digest = (md5.hexdigest(), sha1.hexdigest()) #make immutable
	return digest;

def carve_file(db_info, string):
	#icat = icat -o 32 image offset + " > " + output
	db_query = "SELECT * FROM files WHERE name LIKE ?"
	db_info["db_cursor"].execute(db_query,('%'+string+'%',))
	carve = db_info["db_cursor"].fetchone()
	out_file = re.sub('.*/','',carve[0])
	icat = "icat -o 32 "+sys.argv[1]+" "+str(carve[1])+" > "+out_file
	ipc_shell(icat)
	print "File duplicated to "+os.getcwd()+"/"+out_file
	return;

def carve_partition(db_info, string):
	db_info["db_cursor"].execute("SELECT * FROM partitions")
	db_query = "SELECT * FROM partitions WHERE name LIKE ?"
	db_info["db_cursor"].execute(db_query,('%'+string+'%',))
	carve = db_info["db_cursor"].fetchone()
	dd = "if="+sys.argv[1]+" of="+carve[0]+".dd skip="+str(carve[2])+"count="+str((carve[3]-carve[2]))
	print dd
	print "Running"
	ipc_shell(dd)
	print "Partition duplicated to "+os.getcwd()+"/"+carve[0]+".dd"
	return;

def new_db(db_name):
	db_info = {"db_connect":"","db_cursor":""}
	db_info["db_connect"] = sqlite3.connect(db_name+".db")
	db_info["db_cursor"] = db_info["db_connect"].cursor()
	try:
		db_info["db_cursor"].execute("""CREATE TABLE files(name text, inode int, file_number int)""")
		db_info["db_cursor"].execute("""CREATE TABLE partitions(name text, boot text, start int, end int, blocks int, id int, system text)""")
	except OSError as error:
		print "Table Exists"
	return db_info;

def open_db(db_name):
	db_info = {"db_connect":"","db_cursor":""}
	db_info["db_connect"] = sqlite3.connect(db_name+".db")
	db_info["db_cursor"] = db_info["db_connect"].cursor()
	return db_info;

def query_files_table_db(db_info):  
    	db_info["db_cursor"].execute("SELECT * FROM files")
	print_file_query_db(db_info)
	return;

def query_partitions_table_db(db_info):  
    	db_info["db_cursor"].execute("SELECT * FROM partitions")
	print_partition_query_db(db_info)
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

def query_partition_name_db(db_info, string):
	db_query = "SELECT * FROM partitions WHERE name LIKE ?"
	db_info["db_cursor"].execute(db_query, ('%'+string+'%',))
	print_partition_query_db(db_info)
	return;

def print_file_query_db(db_info):
	while True:
		file = db_info["db_cursor"].fetchone()
		if file == None:
           		break
		print "%3s %-30s %5s" % (file[2], file[0], file[1])
	return;

def print_partition_query_db(db_info):
	while True:
		file = db_info["db_cursor"].fetchone()
		if file == None:
           		break
		print "%10s %10s %10s" % ('Name', 'Start', 'Stop')
		print "%10s %10s %10s" % (file[0], file[2], file[3])	
	return;

def insert_file_list_db(db_info):
	fls = "fls -prlo 32 "+sys.argv[1]
	file_list = ipc_shell(fls)
	iteration = 0
	for single_file in file_list:
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
	return;

def insert_partition_list_db(db_info):
	partitions = ipc_shell("fdisk -l "+sys.argv[1])
	partitions = partitions[9:]
	for line in partitions:
		line = line.split()
		partition_info = [(line[0], line[1], line[2], line[3], line[4], line[5], line[6])]
		db_info["db_cursor"].executemany("INSERT INTO partitions VALUES (?,?,?,?,?,?,?)", partition_info)
		db_info["db_connect"].commit()
	return;

def main_menu():
	while True:
		choice = raw_input("\
		1. Open Database \n\
		2. Print Database Contents \n\
		3. Search Files Database \n\
		4. Carve File \n\
		5. Carve Partition \n\
		6. Exit \nSelection: ")

		if re.match('^Populate|1$', choice, re.IGNORECASE):
			while True:
				choice = raw_input("New or Existing Database? ")
				if re.match('^new|1$', choice, re.IGNORECASE):
					db_info = new_db(raw_input("Database Name? "))
					insert_file_list_db(db_info)
					insert_partition_list_db(db_info)
					break
				elif re.match('^old|existing|2$', choice, re.IGNORECASE):
					db_info = open_db(raw_input("Database Name? "))
					break
				else:
					print "Bad Input"
			print "Database Populated"
		elif re.match('^Print|2$', choice, re.IGNORECASE):
			query_files_table_db(db_info)
			query_partitions_table_db(db_info)
		elif re.match('^Search|3$', choice, re.IGNORECASE):
			while True:
				type = raw_input("Type of Search? \n\t\t1. By Name \n\t\t2. By Inode \nSelection: ")
				if re.match('^Name|1$', type, re.IGNORECASE):
					query_name_db(db_info, raw_input("\nString to search for? "))
					break
				elif re.match('^Inode|2$', type, re.IGNORECASE):
					query_inode_db(db_info, raw_input("\nString to search for? "))
					break
				else:
					print "Bad Input"
		elif re.match('^File|4$', choice, re.IGNORECASE):
			while True:
				type = raw_input("Carve By: \n\t\t1. By Name \n\t\t2. By Inode \n\t\t3. File Number \n\t\t4. Back \nSelection: ")
				if re.match('^Name|1$', type, re.IGNORECASE):
					query_name_db(db_info, raw_input("\nString to search for? "))
					if re.match('^Yes|Y$', raw_input("\nContinue? "), re.IGNORECASE):
						carve_file(db_info, string)
						break
				elif re.match('^Inode|2$', type, re.IGNORECASE):
					query_inode_db(db_info, raw_input("\nString to search for? "))
					if re.match('^Yes|Y$', raw_input("\nContinue? "), re.IGNORECASE):
						carve_file(db_info, string)
						break
				elif re.match('^Number|3$', type, re.IGNORECASE):
					query_file_number_db(db_info, raw_input("\nString to search for? "))
					if re.match('^Yes|Y$', raw_input("\nContinue? "), re.IGNORECASE):
						carve_file(db_info, string)
						break
				elif re.match('^Back|4$', type, re.IGNORECASE):
					break
				else:
					print "Bad Input"
		elif re.match('^Partition|5$', choice, re.IGNORECASE):
			query_partitions_table_db(db_info)
			while True:
				slice = raw_input("Carve By: \n\t\t1. By Name \n\t\t2. By Sector \n\t\t3. Back \nSelection: ")
				if re.match('^Name|1$', slice, re.IGNORECASE):
					string = raw_input("\nPartition name? ")
					query_partition_name_db(db_info, string)
					if re.match('^Yes|Y$', raw_input("\nContinue? "), re.IGNORECASE):
						carve_partition(db_info, string)
					break
				elif re.match('^Sector|2$', slice, re.IGNORECASE):
					start = raw_input("\nStart Sector? ")
					stop = raw_input("\nStop Sector? ")
					carve_partition(db_info, start, stop)
					#query check input
					break
				elif re.match('^Back|3$', slice, re.IGNORECASE):
					break
				else:
					print "Bad Input"
		elif re.match('^Exit|6$', choice, re.IGNORECASE):
			break
		else:
			print "Bad Input"	

def main():
	original_digest = hashfile()

	main_menu()

	final_digest = hashfile()
	if original_digest != final_digest:
		print "\n\n\n Warning File Altered \n\n\n"
	else:
		print "File Unaltered"
	return;

if __name__ == "__main__":
	main()
