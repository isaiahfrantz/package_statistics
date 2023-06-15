# package_statistics
Calculate the number of files each package in the main Debian repo for a given architecture

# Usage
The script is comprise of two parts:
 - A wrapper script to handle/parse/validate the cli args
 - A module that contains the logic for downloading the zipped repo catalog, parsing it, and calculating the output

## Options
- -h/--help: displays help and exits
- -d/--debug: outputs additional debug info (mostly used during dev time)
- -l/--list: gets and lists the available architectures from the repo sire
- -a/--arch: specify the desired architecture
- -c/--count: specify the number of packages to be printed in the report, default is 10

---
# Note
(Glenn) Isaiah Frantz
isaiah.frantz@gmail.com

package_statistics:

Time spent on project: 4h

In a past life I wrote a lot of large perl scripts.
These days I write a ton of ruby+puppet.
While these languages share ancestors with python, they are very different when it comes to regex functionality and how data structure methods work.
I spent a lot of time translating how I would do things in ruby to python using the following sites:
 - <https://curlconverter.com/python/>: convert curl to python, I chose the requests class rather than the http.client class
 - <https://www.w3schools.com/python/>: quick lookup of methods
 - <https://www.tutorialspoint.com/python>: a second method site
 - <https://www.geeksforgeeks.org/>: found how to deal with binary data and gzip

I learned a lot about python with this project. In the past I have modified existing scripts but haven't written anything from scratch.
I'm definitely interested in learning more

