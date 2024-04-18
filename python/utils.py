import os

##___________________________________________________________________
##
def printError(text):
    #prints text in red
    os.system("echo -e '\\033[41;1;37m "+text+" \\033[0m'")
##___________________________________________________________________
##
def printWarning(text):
    #prints text in orange
    os.system("echo -e '\\033[43;1;37m "+text+" \\033[0m'")
##___________________________________________________________________
##
def printGoodNews(text):
    #prints text in green
    os.system("echo -e '\\033[42;1;37m "+text+" \\033[0m'")

