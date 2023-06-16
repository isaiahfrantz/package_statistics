#!/usr/bin/env python
'''
Package_statistics fetches the Contents file from a Debian repo for a specified architecture
    Parameters:
        help (bool) : Flag to print help info
        debug (bool): Flag to print extra debug output
        list (bool) : Calculate and print a list of the available architectures based on
            files available in Debian repo
        arch (str)  : The name of the desired architecture, must match an entry from -list output
        count (int) : Optional, Number of packages to print, starting from highest count, descending order
            Default number is 10

    Dependencies:
        Module: package_statistics_lib.py
'''
import sys
import getopt
import package_statistics_lib as psl

# remove first arg/program name
argslist = sys.argv[1:]

# Options
OPTIONS = "hdla:c:"
# Long options
long_options = ["help", "debug", "list", "arch=", "count="]

try:
    # Parse args
    args, values = getopt.getopt(argslist, OPTIONS, long_options)
except getopt.error as err:
        # we hit an error, print details
        psl.pm(f"ERROR: arg parsing error=>{str(err)}<")

# globals and default values
ARCH = 'ARCH_NOT_SET'
NUM  = 10

def main(args) -> int:
    global ARCH, NUM
    # check args
    for arg, val in args:
        if arg in ("-h", "--help"):
            psl.pm("Display help")
            psl.show_help()

        elif arg in ("-d", "--debug"):
            psl.pm("Enable debug output")
            psl.DEBUG = True

        elif arg in ("-l", "--list"):
            psl.pm("Show list architecture tags there are files for")
            count = 1
            for i in psl.get_arch_list():
                psl.pm(f"{count}. {i}")
                count += 1
            sys.exit()

        elif arg in ("-a", "--arch"):
            psl.pm(f"Checking for arch=>{val}<")
            if val in psl.get_arch_list():
                ARCH = val
                psl.pm(f"Processing package statistics for arch=>{ARCH}<")
            else:
                psl.pm(f"No Contents-{val}.gz file found! Please check arch and rerun.")
                sys.exit(1)
        elif arg in ("-c", "--count"):
            psl.pm(f"Requested {val} entries")
            if val.isnumeric():
                NUM = int(val)
            else:
                psl.pm(f"ERROR: arg for count is not numerical=>{str(val)}<")
                sys.exit(1)



    # required args
    if ARCH == 'ARCH_NOT_SET':
        psl.pm("ERROR: arch arg is required!")
        psl.show_help(1)

    # we know the file exists, lets get it
    psl.pm(f"Package statistics for arch=>{ARCH}<:")
    psl.top_count(ARCH,NUM)

    return 0

# start main script
if __name__ == '__main__':
    raise SystemExit(main(args))
