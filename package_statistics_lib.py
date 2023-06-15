'''
Package_statistics_lib contains a bunch of functions to get and process Contents files from debian
    repo sites.
'''
import sys
import re
import gzip
import requests

DEBUG = False

def show_help(exit_code=0):
    '''
    Display help and exit
        Parameters:
            exit_code (int): default is zero, if set will exit with provided exit_code
        Returns:
            None
    '''
    print ("""Args:
    -h,--help       display this help
    -d,--debug      print debug output
    -l,--list       list supported architectures and exit
    -a,--arch       architecture whose packages list you want to analyze
    -c,--count      the number of packages you would like to list""")
    sys.exit(exit_code)

def pm(message):
    '''
    Handles printing messages
        Parameters:
            message (string):
                If it contains the string DEBUG, print it to stderr only if the global DEBUG is True
                If it doesn't contain DEBUG, print message to stdout as it is
        Returns:
            None
    '''
    if re.search(r"DEBUG",message):
        if DEBUG:
            print(message, file=sys.stderr)
    else:
        print(message)

def http_get_item(arch=None):
    '''
    Drives http calls using the requests module
        Parameters:
            arch (string): optional, default is None
                If not set, get the index and filter for Context files
                If set, must have a remote file matching Contents-{arch}.gz

        Returns:
            Text of index if arch=None
            Binary file object of gziped Contents file for arch
    '''
    base_url = "http://ftp.uk.debian.org/debian/dists/stable/main"
    if arch is not None and arch.isprintable():
        # we received a value, assume it is an arch
        get_it = f"{base_url}/Contents-{arch}.gz"
    else:
        # no arg, we want the list
        get_it = base_url

    try:
        x = requests.get(get_it, timeout=20)
        if arch is not None:
            return x.content

        return x.text

    except requests.HTTPError as err:
        pm(f"Error in http request=>{str(err)}<")
        sys.exit(1)

def get_arch_list():
    '''
    Retrieves index from page to calculate the available list of architectures there are files for
        Parameters:
            None
        Returns:
            arch_list (list): A list of the available architectures
    '''
    # call http_get_item() to get list of archs that have files
    arch_list = []
    for l in http_get_item().splitlines():
        pm(f"DEBUG: get_arch_list() line=>{l}<")
        m = re.search(r"Contents-[^u].*\.gz",l)
        if m:
            f = m.group().split('"')[0]
            f = re.split(r"-|\.",f)[1]
            arch_list.append(f)
            pm(f"DEBUG: get_arch_list() entry=>{f}< raw=>{m}<")

    pm(f"DEBUG: get_arch_list() list=>{arch_list}<")
    return arch_list


def get_arch_file(arch):
    '''
    Wrapper to retrieve the binary gzipped file containing the package and file list for the requested arch
        Parameter:
            arch (str): String must match arch specific files on server
        Return:
            (bytes): Binary file object containing bytes
    '''
    return http_get_item(arch)

def gunzip_file(data):
    '''
    Decompress gzipped file
        Parameters:
            data (bytes): This is the gzipped file containing package and file info for a specific arch
        Return:
            (str): The text of the Contents file for a specific arch, newline separated lines
    '''
    return gzip.decompress(data).decode()

def process_arch_file(arch):
    '''
    Parses the decompressed text of the Contents file for a specific arch and builds a dictionary containing
        a list of packages and its file reference count.
        Uses the specification listed here: https://wiki.debian.org/DebianRepository/Format?action=show&redirect=RepositoryFormat#A.22Contents.22_indices
        Parameters:
            arch (str): Architecture Contents file to ask get_arch_file() to retrieve
        Returns:
            package_by_fcount (dict); key == (int) file count, value == (list) of packages with that number of files
    '''
    # get file stream
    file = get_arch_file(arch)
    pm(f"DEBUG: got file=>{type(file)}<")
    # extract data from gzip
    file_data = gunzip_file(file)
    pm("DEBUG: extracted data")
    # iterate
    file_count = {}
    for l in file_data.splitlines():
        if re.search(r"FILE.*LOCATION",l):
            # skip header line if present
            pm(f"DEBUG: skip header line=>{l}<")
            continue
        pm(f"DEBUG: line=>{l}<")
        t = l.strip().split()
        pl = t.pop()
        for p in pl.split(","):
            pm(f"DEBUG: package=>{p}<")
            r = p.split("/")
            package = p
            if len(r) > 2:
                # remove the deprecated AREA component of the package if present
                pm(f"DEBUG: p=>{p}< r=>{r}<")
                r.pop(0)
                package = "/".join(r)
            if package in file_count.keys():
                file_count[package] += 1
            else:
                file_count[package] = 1
    pm("DEBUG: done parsing file")
    package_by_fcount = {}
    for package,fcount in file_count.items():
        # now we order the packages by the number of files found
        if fcount not in package_by_fcount.keys():
            package_by_fcount[fcount] = []
        package_by_fcount[fcount].append(package)

    return package_by_fcount

def top_count(arch, num=10):
    '''
    Drives the entire fetch and parse process
        Parameters:
            arch (str): Architecture Contents file to process
            num (int): Number of packages to display, starting from highest number of files to lowest.
                Defaults to 10 packages
        Returns:
            None: Prints out the number of packages requested, numbered list in descending order
                If there are more than one package with the same number of files, we print them in alphabetic order
    '''
    file_count = process_arch_file(arch)
    pm(f"DEBUG: entries in file_count dict=>{len(file_count.keys())}<")
    file_count_keys = list(file_count.keys())
    file_count_keys.sort(reverse=True)
    order_by_count = {}
    for i in file_count_keys:
        if num < 1:
            break
        file_count[i].sort()
        for package in file_count[i]:
            if i not in order_by_count.keys():
                order_by_count[i] = []
            order_by_count[i].append(package)
            num -= 1
            if num < 1:
                break
    print_report(order_by_count)

def print_report(packages):
    '''
    Print the report
        Parameters:
            packages (dict): packages to print; key == (int) number of files, value == (list) names of packages
        Return:
            None
    '''
    count = 1
    for i in packages:
        # print(f"i=>{i}< size=>{len(packages[i])}<")
        for p in packages[i]:
            # print(f"p=>{p}<")
            pm(f"{count}. {p} {i}")
            count += 1
            # 1. <package name 1> <number of files>
            # 2. <package name 2> <number of files>
            # ......
            # 10. <package name 10> <number of files>
