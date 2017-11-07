# moveback.py
# Author: Josh Smith

import os, glob, shutil

# Base directory (location of Settlements and Client Files folders) - CHANGE BEFORE FINAL VERSION
base = 'C:\\Users\\joshua\\Desktop\\Mock Y Drive'

# destination directory - 'Documents to Move to Client Files (Executed)' folder
dest = base + '\\Settlements\\Administrative\\Affidavits\\Scanned Affidavits.Releases to Separate\\Documents to Move to Client Files (Executed)'

# source directory - 'Positives' folder
posdir = base + '\\Client Files\\Positives'

def main():
	# Get all the file paths and file names to be moved
	filepaths = []	# Full file paths
	files = []		# File names (e.g. Smith, Joshua D. - Quigley Release.pdf)
	print("Moving files back to DtMtCF(E) folder...")
	for dirpath, dirnames, filenames in os.walk(posdir):
		for filename in [f for f in filenames if f.endswith(".pdf")]:
			shutil.move(os.path.join(dirpath, filename), dest)
			print("\tMoved \"" + filename + "\"")


if __name__ == '__main__':
	main()
