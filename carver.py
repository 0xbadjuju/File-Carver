#!/usr/bin/python

import sys
import re

import carver_files
import carver_partitions
import carver_common

def main_menu(image):
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
					db_info = carver_common.new_db(raw_input("Database Name? "))
					carver_files.insert_file_list_db(db_info,image)
					carver_partitions.insert_partition_list_db(db_info,image)
					break
				elif re.match('^old|existing|2$', choice, re.IGNORECASE):
					db_info = carver_common.open_db(raw_input("Database Name? "))
					break
				else:
					print "Bad Input"
			print "Database Populated"
		elif re.match('^Print|2$', choice, re.IGNORECASE):
			carver_files.query_files_table_db(db_info)
			carver_partitions.query_partitions_table_db(db_info)
		elif re.match('^Search|3$', choice, re.IGNORECASE):
			while True:
				type = raw_input("Type of Search? \n\t\t1. By Name \n\t\t2. By Inode \nSelection: ")
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
				type = raw_input("Carve By: \n\t\t1. By Name \n\t\t2. By Inode \n\t\t3. File Number \n\t\t4. Back \nSelection: ")
				if re.match('^Name|1$', type, re.IGNORECASE):
					string = raw_input("\nName to search for? ")
					carver_files.query_name_db(db_info, string)
					if re.match('^Yes|Y$', raw_input("\nContinue? "), re.IGNORECASE):
						carver_files.carve_file(db_info, image, string)
						break
				elif re.match('^Inode|2$', type, re.IGNORECASE):
					string = raw_input("\nInode to search for? ")
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
				slice = raw_input("Carve By: \n\t\t1. By Name \n\t\t2. By Sector \n\t\t3. Back \nSelection: ")
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

def main():
	image = sys.argv[1]

	carver_common.get_partition_offset(image)

	original_digest = carver_common.hashfile(image)

	main_menu(image)

	final_digest = carver_common.hashfile(image)
	if original_digest != final_digest:
		print "\n\n\n Warning File Altered \n\n\n"
	else:
		print "File Unaltered"
	return;

if __name__ == "__main__":
	main()
