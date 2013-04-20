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

def main():

	original_digest = hashfile()

	fdisk 	= "fdisk -l "+sys.argv[1]
	fls 	= "fls -prlo 32 "+sys.argv[1]
	icat	= "icat -o 32 "+sys.argv[1]
	dd	= "if="+sys.argv[1]+" of="

	image_details = ipc_shell(fdisk)
	print image_details[9]
	
	file_list = ipc_shell(fls)
	file_list_line = file_list[1].split()
	print file_list_line[2]

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