# filemove.py
# Author: Josh Smith

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

    f.write(str(len(moved)) + " Files moved successfully:\n")
    for i in range(len(moved)):
        f.write("\t- " + moved[i] + "\n")
    f.write("\n")

    f.write(str(len(not_moved)) + " Files not moved:\n")
    for i in range(len(not_moved)):
        f.write("\t- " + not_moved[i][0] + " - " + not_moved[i][1] + "\n")
    f.write("\n")

        
# ONLY PRINTS - DOES NOT MOVE FILES
def move_main(debug, log):
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
    dotcount = 0;
    for i in range(len(filenames)):
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

        if len(possible_dests) == 1:
            dest = possible_dests[0]
        elif len(possible_dests) < 1:
            if debug:
                print("No possible dests for " + filenames[i])
            unmoved.append([filenames[i], "No possible destinations found"])
            continue
        elif len(possible_dests) > 1:
            if debug:
                print("Multiple possible destinations found for " + filenames[i])
            unmoved.append([filenames[i], "Multiple possible destinations found"])
            continue

        # 3. Now time to determine whether the file is an aff or a release
        # TODO: HANDLE OTHER DOCUMENT TYPES (skip for now)
        doc_info = filenames[i].split(" - ")[1].replace(".pdf", "").split(" ")
        if "Affidavit" in doc_info:
            dest += '/Affidavits/Executed Affidavits'
        elif "Release" in doc_info:
            dest += '/Releases'
        else:
            if debug:
                print("\"" + filenames[i] + "\" not moved - Unsupported document type.")
            unmoved.append([filenames[i], "Unsupported document type"])
            continue

        # Final check on destination...
        if not dest:
            if debug:
                print("\"" + filenames[i] + "\" not moved - Unknown error :(")
            unmoved.append([filenames[i], "Unknown error (uh oh...)"])
        else:
            # CHECK if DUPE DOC
            if not is_dupe(dest, filenames[i]):
                shutil.move(filepaths[i], dest)
                moved.append(filenames[i])
            else:
                if debug:
                    print("\"" + filenames[i] + "\" not moved - Dupe doc")
                unmoved.append([filenames[i], "Duplicate document"])

        print(". ", end="")
        dotcount += 1;
        if dotcount % 10 == 0:
            print("\n", end="")

    total_time = round(time.time() - start_time, 5);
    print("")
    if log:
        generate_log(moved, unmoved, total_time)
    print("Total execution time: " + str(total_time))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Move files from \'Files to be moved\' to \'Positives\'')
    parser.add_argument('--drafts', help="Use this to move files from drafted affs to be moved folder (NOT TESTED)", action="store_true", default=False)
    parser.add_argument('--verbose', help="Use this to show feedback messages (might be messy)", action="store_true", default=False)
    parser.add_argument('--log', help="Use this to create a text file containing detailed results of the move", action="store_true", default=False)
    args = parser.parse_args()
    move_main(args.verbose, args.log)
