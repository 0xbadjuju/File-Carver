#!/usr/bin/python

import subprocess
import sys
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

def new_db(db_name):
	db_info[db_connect] = sqlite3.connect(db_name+".db")
	db_info[db_pointer] = db_info[db_connect].cursor()
	db_info[db_pointer].execute("""CREATE TABLE files(name text, inode text, file_number text)""")
	return db_info;

def open_db(db_name):
	db_info[db_connect] = sqlite3.connect(db_name+".db")
	db_info[db_pointer] = db_connect.cursor()
	return db_info;

def query_row_db(db_info, db_row):
	for row in db_info[db_pointer].execute("SELECT rowid, * FROM files ORDER BY"+db_row+"):
		print row
	return;

def query_db(db_info, string):
	db_query = "SELECT * FROM files WHERE name LIKE %"+string+"%"
	db_info[db_pointer].execute(db_query)
	print db_info[db_pointer].fetchall()
	return;

#def file_list(db_info)
def insert_file_list():
	fls = "fls -prlo 32 "+sys.argv[1]
	file_dictionary = {}
	file_list = ipc_shell(fls)
	iteration = 0
	for single_file in file_list:
		iteration++
		single_file = single_file.split()
		if single_file[0] == 'r/r':
			if single_file[1] == "*":
				file_dictionary[single_file[3]] = single_file[2]
				#file_info = [(single_file[3], single_file[3], iteration)]
				#db_info[db_pointer].executemany("INSERT INTO files VALUES (?,?,?)", file_info)
				#db_info[db_connect].commit()
			else:
				file_dictionary[single_file[2]] = single_file[1]
	return file_dictionary;

def main():

	original_digest = hashfile()

	fdisk 	= "fdisk -l "+sys.argv[1]
	icat	= "icat -o 32 "+sys.argv[1]
	dd	= "if="+sys.argv[1]+" of="

	image_details = ipc_shell(fdisk)
	print image_details[9]

	files = insert_file_list()
	for single_file in files:
		print single_file, files[single_file]

	#icat = icat + file offset + " < " + output file
	#carve = ipc_shell(icat)
	
	#dd = dd+output_name+" skip="+file_location
	#duplicate = ipc_shell(dd)
	
	final_digest = hashfile()
	if original_digest != final_digest:
		print "\n\n\n Warning File Altered \n\n\n"
	else:
		print "File Unaltered"
	return;

if __name__ == "__main__":
	main()