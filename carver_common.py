import subprocess
import sqlite3
import hashlib
import os

def get_partition_offset(image):
	ipc_shell("fdisk -l "+image)

def ipc_shell(shell_command):
	try:
		sub_process = subprocess.Popen( shell_command, shell=True, stdout=subprocess.PIPE )
		(std_out, std_err) = sub_process.communicate()
	except OSError as error:
		print "Command Failed:", error
	std_out = std_out.splitlines()
	return std_out;

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

def new_db(db_name):
	if os.path.exists(db_name):
		print "File Exists"
	else:
		db_info = {"db_connect":"","db_cursor":""}
		db_info["db_connect"] = sqlite3.connect(db_name+".db")
 		db_info["db_cursor"] = db_info["db_connect"].cursor()
		db_info["db_cursor"].execute("""CREATE TABLE files(name text, inode int, file_number int)""")
		db_info["db_cursor"].execute("""CREATE TABLE partitions(name text, boot text, start int, end int, blocks int, id int, system text)""")
	return db_info;

def open_db(db_name):
	db_info = {"db_connect":"","db_cursor":""}
	if os.path.exists(db_name): 
		db_info["db_connect"] = sqlite3.connect(db_name+".db")
		db_info["db_cursor"] = db_info["db_connect"].cursor()
	else:
		print "No Such File"
	return db_info;