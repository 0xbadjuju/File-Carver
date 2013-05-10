#!/usr/bin/python

################################################################################
# Alexander Leary, Scott Fenwick, Melissa Parker
# April 2013
#
# Main file for carving program
# Requires carver_files and carver_partitions carving actions
# All three files require carver_common for database related tasks
################################################################################

import sys
import re
import argparse

import carver_files
import carver_partitions
import carver_common

################################################################################
# Function:	 main_menu(image)
# Variables: image, choice, type, string, slice, start, stop  
# Launches all program functions by looping through and getting user input
################################################################################
def main_menu(image):
	while True:
		choice = raw_input("\
		\n\
		1. Open Database \n\
		2. Print Database Contents \n\
		3. Search Files Database \n\
		4. Carve File \n\
		5. Carve Partition \n\
		6. Exit \nSelection: ")

		if re.match('^Populate|1$', choice, re.IGNORECASE):
			while True:
				choice = raw_input("\t\t1. New Database \n\t\t2. Existing Database \nSelection: ")
				if re.match('^new|1$', choice, re.IGNORECASE):
					db_info = carver_common.new_db(raw_input("Database Name? "))
					carver_common.insert_list_db(db_info,image)
					break
				elif re.match('^old|existing|2$', choice, re.IGNORECASE):
					db_info = carver_common.open_db(raw_input("Database Name? "))
					break
				else:
					print "Bad Input"
		elif re.match('^Print|2$', choice, re.IGNORECASE):
			carver_files.query_files_table_db(db_info)
			carver_partitions.query_partitions_table_db(db_info)
		elif re.match('^Search|3$', choice, re.IGNORECASE):
			while True:
				type = raw_input("\tType of Search? \n\t\t1. By Name \n\t\t2. By Disk Location \nSelection: ")
				if re.match('^Name|1$', type, re.IGNORECASE):
					carver_files.query_name_db(db_info, raw_input("\nString to search for? "))
					break
				elif re.match('^Inode|2$', type, re.IGNORECASE):
					carver_files.query_inode_db(db_info, raw_input("\nString to search for? "))
					break
				else:
					print "Bad Input"
		elif re.match('^File|4$', choice, re.IGNORECASE):
			while True:
				type = raw_input("\tCarve By: \n\t\t1. By Name \n\t\t2. By Location \n\t\t3. File Number \n\t\t4. Back \nSelection: ")
				if re.match('^Name|1$', type, re.IGNORECASE):
					string = raw_input("\nName to search for? ")
					carver_files.query_name_db(db_info, string)
					if re.match('^Yes|Y$', raw_input("\nContinue? "), re.IGNORECASE):
						carver_files.carve_file(db_info, image, string)
						break
				elif re.match('^Inode|2$', type, re.IGNORECASE):
					string = raw_input("\nDisk Location to search for? ")
					carver_files.query_inode_db(db_info, string)
					if re.match('^Yes|Y$', raw_input("\nContinue? "), re.IGNORECASE):
						carver_files.carve_file(db_info, image, string)
						break
				elif re.match('^Number|3$', type, re.IGNORECASE):
					string = raw_input("\nDB File Number to search for? ")
					carver_files.query_file_number_db(db_info, string)
					if re.match('^Yes|Y$', raw_input("\nContinue? "), re.IGNORECASE):
						carver_files.carve_file(db_info, image, string)
						break
				elif re.match('^Back|4$', type, re.IGNORECASE):
					break
				else:
					print "Bad Input"
		elif re.match('^Partition|5$', choice, re.IGNORECASE):
			carver_partitions.query_partitions_table_db(db_info)
			while True:
				slice = raw_input("\tCarve By: \n\t\t1. By Name \n\t\t2. By Sector \n\t\t3. Back \nSelection: ")
				if re.match('^Name|1$', slice, re.IGNORECASE):
					string = raw_input("\nPartition name? ")
					carver_partitions.query_partition_name_db(db_info, string)
					if re.match('^Yes|Y$', raw_input("\nContinue? "), re.IGNORECASE):
						carver_partitions.carve_partition(db_info, image, string)
					break
				elif re.match('^Sector|2$', slice, re.IGNORECASE):
					start = raw_input("\nStart Sector? ")
					stop = raw_input("\nStop Sector? ")
					carver_partitions.carve_partition(db_info, start, stop)
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
			
################################################################################
# Function:	 main()
# Variables: image, original_digest, final_digest
# Hashes original file, opens the main menu, the checks the file hasn't been
# altered in any way.
################################################################################
def main():
	
	arguments = argparse.ArgumentParser()
	arguments.add_argument('-n','--nohash', help='Disable Image Hashing', action='store_true', required=False)
	arguments.add_argument('-i','--image', help='Pass Image Name', action="store", required=False)
	arguments.set_defaults(n=False, nohash=False, i="", image="")
	passed_arguments = arguments.parse_args()
	
	if passed_arguments.image != "":
		image = passed_arguments.image
	else:
		image = raw_input("\nImage Name? ")

	if not passed_arguments.nohash:
		original_digest = carver_common.hashfile(image)

	main_menu(image)
	if not passed_arguments.nohash:
		final_digest = carver_common.hashfile(image)
		if original_digest != final_digest:
			print "\n\n\n Warning File Altered \n\n\n"
		else:
			print "File Unaltered"
	return;

if __name__ == "__main__":
	main()
