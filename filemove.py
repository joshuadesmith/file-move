# FileMove.py ALPHA

import shutil, os, argparse, time, glob


# Flags for debugging  
# - Set LIST_FILES to true to list all files in source directory
LIST_FILES = True

# Base directory (location of Settlements and Client Files folders) - CHANGE BEFORE FINAL VERSION
#base = 'C:\\Users\\joshua\\Desktop\\Mock Y Drive'
#unixbase = 'C:/Users/joshua/Desktop/Mock Y Drive'
base = 'Y:'
unixbase = 'Y:'

# Source directory - 'Documents to Move to Client Files (Executed)' folder
src = base + '\\Settlements\\Administrative\\Affidavits\\Scanned Affidavits.Releases to Separate\\'
unixsrc = unixbase + '/Settlements/Administrative/Affidavits/Scanned Affidavits.Releases to Separate/'

# Destination directory - 'Positives' folder
posdir = base + '\\Client Files\\Positives'
unixposdir = unixbase + '/Client Files/Positives' # Not sure if I need this...

# sets the src variable - which is the folder to be checked for files to move
def set_src(drafts=False):
	global src, unixsrc
	if not drafts:
		src += 'Documents to Move to Client Files (Executed)'
		unixsrc += 'Documents to Move to Client Files (Executed)'
	else:
		src += 'Drafted affs' # TODO: put proper folder name here

# Checks whether the client already has a copy of a doc to be moved
def is_dupe(dest, file):
	full_path = dest + '\\' + file
	return os.path.isfile(full_path)

# generates a .txt file with a detailed log of this script's results
def generate_log(moved, not_moved, run_time):
	timestr = time.strftime("%Y%m%d-%H%M%S")
	filename = src + '\\movelog_' + timestr + '.txt'
	f = open(filename, "w")
	f.write("FileMove.py\n")
	f.write("Ran: " + timestr + "\n")
	f.write("Total run time: %s seconds\n\n" % run_time)

	f.write(str(len(moved)) + " Files moved to positives:\n")
	for i in range(len(moved)):
		f.write("\t- " + moved[i] + "\n")
	f.write("\n")

	f.write(str(len(not_moved)) + " Files not moved:\n")
	for i in range(len(not_moved)):
		f.write("\t- " + not_moved[i] + "\n")
	f.write("\n")


def move_main(drafts, silent, log):
	start_time = time.time()
	set_src(drafts)

	# Get all the file paths and file names to be moved
	#filepaths = []	# Full file paths
	#files = []		# File names (e.g. Smith, Joshua D. - Quigley Release.pdf)
	#for dirpath, dirnames, filenames in os.walk(src):
	#	for filename in [f for f in filenames if f.endswith(".pdf")]:
	#		filepaths.append(os.path.join(dirpath, filename))
	#		files.append(filename)

	# glob version...
	filepaths = glob.glob('%s/*.pdf' % unixsrc)
	files = [os.path.basename(fp) for fp in filepaths]

	# For sanity check
	if not silent:
		if len(files) > 0:
			print("Found "+ str(len(files)) + " files to be moved to Positives")
		else:
			print("No files found in source directory... Exiting")
			return

	# Print file paths (for debugging)
	if LIST_FILES:
		print(str(len(files)) + ' Files to be Moved:')
		for file in files:
			print('\t' + file)
		print("") 
		print("Corresponding file paths: ")
		for filepath in filepaths:
			print('\t' + filepath)
		print("TEST RUN TO DETERMINE ACCURACY OF FILE PATH FETCHING - EXITING\n...")
		

	moved = []
	not_moved = []

	# Time to move dem files
	for i in range(len(files)):
		# Find appropriate folder for file
		# 1. Get client name from file name (testing with just one file)
		cli_name = files[i].split(" - ")[0].replace('.', '')

		# 2. Search for dir that matches this name
		# If the client has a standard directory name (no flags), then proceed, otherwise, pull up possible folders
		dest = ''
		if not os.path.isdir(posdir + '\\' + cli_name):
			# if the exact folder isn't there, get all possible matches
			#dests = []
			#for dir in os.listdir(posdir):
			#	if cli_name in dir.split('.'):
			#		dests.append(dir)
			fp = unixposdir + '/' + cli_name
			dests = glob.glob('%s**' % fp)

			if LIST_FILES:
				print("Possible destinations:")
				for d in dests:
					print("\t" + d)
				continue;

			if len(dests) == 1:
				dest = posdir + '\\' + dests[0]	# if only one is found, then use it
			elif len(dests) > 1:
				if not silent:
					print("\"" + files[i] + "\" not moved - Multiple possible destination folders found.")
				not_moved.append(files[i])
				continue
		else:
			dest = posdir + '\\' + cli_name # exact folder name match

		if not dest:
			if not silent:
				print("\"" + files[i] + "\" not moved - No valid destination folder found.")
			not_moved.append(files[i])
			continue

		if not drafts:	
			# 3. Now time to determine whether the file is an aff or a release
			# TODO: HANDLE OTHER DOCUMENT TYPES (skip for now)
			doc_info = files[i].split(" - ")[1].replace(".pdf", "").split(" ")
			if "Affidavit" in doc_info:
				dest += '\\Affidavits\\Executed Affidavits'
			elif "Release" in doc_info:
				dest += '\\Releases'
			else:
				if not silent:
					print("\"" + files[i] + "\" not moved - Unsupported document type.")
				not_moved.append(files[i])
				continue
		else:	# when moving drafted affs shoop 
			dest += '\\Affidavits'

		# Final check on destination...
		if not dest:
			if not silent:
				print("\"" + files[i] + "\" not moved - Unknown error :(")
			not_moved.append(files[i])
		else:
			# CHECK if DUPE DOC
			if not is_dupe(dest, files[i]):
				if LIST_FILES:
					print("Moving \"" + files[i] + "\" to " + dest)
				shutil.move(filepaths[i], dest)
				moved.append(files[i])
			else:
				if not silent:
					print("\"" + files[i] + "\" not moved - Dupe doc")
				not_moved.append(files[i])

	total_time = round(time.time() - start_time, 5);

	# Final console reporting
	if not silent:
		print("...")
		if len(not_moved) == 0:
			print("All files moved successfully.")
		else:
			print(str(len(not_moved)) + " files were not moved:")
			for file in not_moved:
				print("\t - " + file)

	if log:
		generate_log(moved, not_moved, total_time)
		
# ONLY PRINTS - DOES NOT MOVE FILES
def move_main_2(debug):
	# Get time for speed logging
	start_time = time.time()

	# Set source directory depending on drafts or executed
	set_src()

	# full file paths of pdfs to be moved
	filepaths = glob.glob('%s/*.pdf' % unixsrc)

	# standalone file names of pdfs
	filenames = [os.path.basename(fp) for fp in filepaths]

	# Print file paths (for debugging)
	if debug:
		print(str(len(filenames)) + ' filenames = [')
		for file in filenames:
			print('\t' + file + ",")
		print("]\n") 
		print("filepaths = [")
		for filepath in filepaths:
			print('\t' + filepath + ",")
		print("]\n")

	# Lists for moved and unmoved file names
	moved = []
	unmoved = []

	# Main loop for moving
	if debug:
		print("ENTER MAIN LOOP:")
	for i in range(10):
		# Get client name from file name (testing with just one file)
		cli_name = filenames[i].split(" - ")[0].replace('.', '')
		dest = ''

		# Get possible destinations with glob and cli_name
		fp = unixposdir + '/' + cli_name
		possible_dests = glob.glob('%s**' % fp)

		if debug:
			print("Possible destinations for \"" + filenames[i] + "\":")
			for pd in possible_dests:
				print("\t" + pd)
			print("")


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Move files from \'Files to be moved\' to \'Positives\'')
	parser.add_argument('--drafts', help="Use this to move files from drafted affs to be moved folder (currently only moves PDFs)", action="store_true", default=False)
	parser.add_argument('--silent', help="Use this to limit feedback messages (not recommended)", action="store_true", default=False)
	parser.add_argument('--log', help="Use this to create a text file containing detailed results of the move", action="store_true", default=False)
	args = parser.parse_args()
	# print("Cmd Line Args:\n\tdrafts: " + str(args.drafts) + "\n\tsilent: " + str(args.silent) + "\n\tlog: " + str(args.log))
	#move_main(args.drafts, args.silent, args.log)
	move_main_2(True)
