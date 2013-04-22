#!/usr/bin/python

import subprocess
import sys
import re
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
	db_query = "SELECT * FROM files WHERE name LIKE %"+string+"%"
	db_info["db_cursor"].execute(db_query)
	carve = db_info["db_cursor"].fetchone()
	icat = "icat -o 32 "+sys.argv[1]+" "+carve[1]+" > "+carve[2]
	ipc_shell(icat)
	return;

def carve_partition():
	dd = "if="+sys.argv[1]+" of="
	return;

def new_db(db_name):
	db_info = {"db_connect":"","db_cursor":""}
	db_info["db_connect"] = sqlite3.connect(db_name+".db")
	db_info["db_cursor"] = db_info["db_connect"].cursor()
	db_info["db_cursor"].execute("""CREATE TABLE files(name text, inode text, file_number text)""")
	return db_info;

def open_db():
	db_name = raw_input("Database Name? ")
	db_info = {"db_connect":"","db_cursor":""}
	db_info["db_connect"] = sqlite3.connect(db_name+".db")
	db_info["db_cursor"] = db_info["db_connect"].cursor()
	return db_info;

def query_row_db(db_info, db_row):  
    	db_info["db_cursor"].execute("SELECT * FROM files")
	while True:
		file = db_info["db_cursor"].fetchone()
		if file == None:
           		break
		print "%3s %-30s %5s" % (file[2], file[0], file[1])
	return;

def query_db(db_info, string):
	db_query = "SELECT * FROM files WHERE name LIKE ?"
	db_info["db_cursor"].execute(db_query, ('%'+string+'%',))
	while True:
		file = db_info["db_cursor"].fetchone()
		if file == None:
           		break
		print "%3s %-30s %5s" % (file[2], file[0], file[1])
	return;

def insert_file_list(db_info):
	fls = "fls -prlo 32 "+sys.argv[1]
	file_list = ipc_shell(fls)
	iteration = 0
	for single_file in file_list:
		single_file = single_file.split()
		if single_file[0] == 'r/r':
			iteration+=1
			if single_file[1] == "*":
				file_info = [(single_file[3], single_file[2], iteration)]
			else:
				file_info = [(single_file[2], single_file[1], iteration)]
			db_info["db_cursor"].executemany("INSERT INTO files VALUES (?,?,?)", file_info)
			db_info["db_connect"].commit()
	return;

def main():
	fdisk 	= "fdisk -l "+sys.argv[1]
	#original_digest = hashfile()
	
	while True:
		choice = raw_input("New or Existing Database? ")
		if re.match('^new$', choice, re.IGNORECASE):
			db_info = new_db("test")
			break
		elif re.match('^old$', choice, re.IGNORECASE):
			db_info = open_db()
			break
		else:
			print "Bad Input"

	image_details = ipc_shell(fdisk)

	insert_file_list(db_info)

	query_row_db(db_info, "name")

	query_db(db_info, "NIKON")
	
	#final_digest = hashfile()
	#if original_digest != final_digest:
	#	print "\n\n\n Warning File Altered \n\n\n"
	#else:
	#	print "File Unaltered"
	return;

if __name__ == "__main__":
	main()