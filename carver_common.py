import subprocess
import datetime
import sqlite3
import hashlib
import os
import re

################################################################################
# Function:	 ipc_shell(shell_command)
# Variables: shell_command, std_out, std_err, error  
# Passes commands to a shell to be processed
################################################################################
def ipc_shell(shell_command):
	try:
		sub_process = subprocess.Popen( shell_command, shell=True, stdout=subprocess.PIPE )
		(std_out, std_err) = sub_process.communicate()
	except OSError as error:
		print "Command Failed:", error, " ", std_err
	std_out = std_out.splitlines()
	return std_out;

################################################################################
# Function:	 hashfile(image)
# Variables: image, md5, sha1, file_to_hash, digest
# Hashes a file using md5 and sha1 and returns the hashes in a tuple
################################################################################
def hashfile(image):
	md5 = hashlib.md5()
	sha1 = hashlib.sha1()
	file_to_hash = open(image, "rb")
	while True:
		file_chunk = file_to_hash.read(128)
		if not file_chunk:
			break
		md5.update(file_chunk)
		sha1.update(file_chunk)
	digest = (md5.hexdigest(), sha1.hexdigest()) #make immutable
	return digest;

################################################################################
# Function:	 new_db(db_name)
# Variables: db_info  
# Creates a new database with 2 tables, file and partitions
################################################################################
def new_db(db_name):
	if os.path.exists(db_name):
		print "File Exists"
	else:
		db_info = {"db_connect":"","db_cursor":""}
		db_info["db_connect"] = sqlite3.connect(db_name+".db")
 		db_info["db_cursor"] = db_info["db_connect"].cursor()
		db_info["db_cursor"].execute("""CREATE TABLE files(name text, inode int, file_number int, offset int)""")
		db_info["db_cursor"].execute("""CREATE TABLE partitions(name text, boot text, start int, end int, blocks int, id int, system text)""")
	return db_info;

################################################################################
# Function:	 open_db(db_name)
# Variables: db_info  
# Opens an existing database for use
################################################################################
def open_db(db_name):
	db_info = {"db_connect":"","db_cursor":""}
	if os.path.exists(db_name+".db"): 
		db_info["db_connect"] = sqlite3.connect(db_name+".db")
		db_info["db_cursor"] = db_info["db_connect"].cursor()
	else:
		print "No Such File\n"
	return db_info;

################################################################################
# Function:	 insert_list_db(db_info, image)
# Variables: db_info , image, line, partition_info 
# Populates the database with partition information
################################################################################
def insert_list_db(db_info, image):
	partitions = ipc_shell("fdisk -l "+image)
	partitions = partitions[9:]
	for line in partitions:
		line = line.split()
		partition_info = [(line[0], line[1], line[2], line[3], line[4], line[5], line[6])]
		db_info["db_cursor"].executemany("INSERT INTO partitions VALUES (?,?,?,?,?,?,?)", partition_info)
		db_info["db_connect"].commit()
		insert_file_list_db(db_info,image,line[2])
	return;

################################################################################
# Function:	 query_partitions_table_db(db_info)
# Variables: db_info, image, offset, single_file, file_info
# Populates the database with file information
################################################################################
def insert_file_list_db(db_info, image, offset):
	iteration = 0
	sub_process = subprocess.Popen( "fls -prlo "+offset+" "+image, shell=True, stdout=subprocess.PIPE )
	while True:
		single_file = sub_process.stdout.readline()
		if single_file != '':
			single_file = single_file.split()
			if single_file[0] == 'r/r':
				iteration+=1
				if single_file[1] == "*":
					single_file[2] = re.sub(":", "",single_file[2])
					file_info = [(single_file[3], single_file[2], iteration, offset)]
				else:
					single_file[1] = re.sub(":", "",single_file[1])
					file_info = [(single_file[2], single_file[1], iteration, offset)]
				db_info["db_cursor"].executemany("INSERT INTO files VALUES (?,?,?,?)", file_info)
				db_info["db_connect"].commit()
		else:
			break
	return;

################################################################################
# Function:	 make_directory(path)
# Variables: path
# Creates folders for file output
################################################################################
def make_directory(path, image):
	if not os.path.exists(path):
		try:
			os.makedirs(path)
		except OSError:
			pass

################################################################################
# Function:	 get_time(image)
# Variables: image, time, folder
# Returns the current time in YYYYMMDDHHMM format, intended for foldernames
################################################################################
def get_time(image):
	time = datetime.datetime.now()
	folder = str(time.year) + str(time.month) + str(time.day) + str(time.hour) + str(time.minute)
	return folder;