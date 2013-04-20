#!/usr/bin/python

import subprocess
import sys
import hashlib

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

def file_list():
	fls = "fls -prlo 32 "+sys.argv[1]
	file_dictionary = {}
	file_list = ipc_shell(fls)
	for single_file in file_list:
		single_file = single_file.split()
		if single_file[0] == 'r/r':
			if single_file[1] == "*":
				file_dictionary[single_file[3]] = single_file[2]
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

	files = file_list()
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