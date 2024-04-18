import numpy as np
import argparse
import re
import sys

############# Utility function to read fit file #######################
def ReadAndParseFitInfo(fname):

    infile = open(fname,'r')
    lines = infile.readlines()
    infile.close()

    p = re.compile('(^gamma)(?:(?!WTZt|WTHt|ZTZt|ZTHt).)*$')
    bkg_gamma_lines = list(filter(lambda x : not(p.search(x) is None), lines))

    print("Number of bkg gamma lines :",len(bkg_gamma_lines))

    split_bkg_lines = [ [e.strip() for e in line.split()] for line in bkg_gamma_lines ]

    fitinfo = {}
    fitinfo['systs'] = np.array(split_bkg_lines)[:,0].tolist()
    fitinfo['values'] = np.array([ [float(e.strip()) for e in line[1:]] \
                                   for line in split_bkg_lines ])

    return fitinfo
        
##### Utility function to read systematics table file #####
def ReadAndParseSysInfo(fname):

    infile = open(fname,'r')
    lines = infile.readlines()
    infile.close()

    sysinfo={}
    split_lines = [ [e.strip() for e in ln.split('|')[1:len(ln.split('|'))-1]] for ln in lines ] 

    sysinfo['samples'] = split_lines[0][1:]
    sysinfo['systs'] = np.array(split_lines)[1:,0].tolist()
    sysinfo['zeroinds'] = np.array(np.where(np.array(split_lines)=='0 / 0'))

    sysinfo['upvals'] = np.array([ [float(e.split('/')[0].strip()) for e in line[1:]] \
                                   for line in split_lines[1:] ])
    sysinfo['downvals'] = np.array([ [float(e.split('/')[0].strip()) for e in line[1:]] \
                                   for line in split_lines[1:] ])

    return sysinfo

#################### Compare two tables and mark the cells with large differences #########
def CompareTables(tab1, tab2, threshold=0.1, dimensions=True):

    diffinfo = {}
    reldiff = np.fabs(np.divide(np.subtract(tab1,tab2),
                               tab1,where=(tab1 != 0.)))

    ### The max in each of three columns need to be checked separately
    diffinfo['maxdiff'] = reldiff.max()
    diffinfo['maxind'] = np.unravel_index(reldiff.argmax(),reldiff.shape)

    if dimensions:
        diffinfo['maxdiff_row'] = reldiff.max(axis=0)
        diffinfo['maxind_row'] = reldiff.argmax(axis=0)

        diffinfo['maxdiff_col'] = reldiff.max(axis=1)
        diffinfo['maxind_col'] = reldiff.argmax(axis=1)

    diffinfo['large_inds'] = None
    diffinfo['large_diffs'] = None
    if np.any(reldiff > threshold):
        diffinfo['large_inds'] = np.array(np.where(reldiff > threshold))
        diffinfo['large_diffs'] = reldiff[np.where(reldiff > threshold)]
        

    return diffinfo

######################################################################################################

def CompareTRExFFitFile(fname1, fname2):

    fitinfo1 = ReadAndParseFitInfo(fname1)
    fitinfo2 = ReadAndParseFitInfo(fname2)

    if(fitinfo1['systs'] != fitinfo2['systs']):
        print("<ERROR>:: Mismatched syst lists. Please check.")
        print("Sys list 1 :",fitinfo1['systs'])
        print("Sys list 2 :",fitinfo2['systs'])
        sys.exit()

    #### Check if differences above threshold for any values ####
    diffinfo_systs = CompareTables(fitinfo1['values'], fitinfo2['values'], threshold=0.1, dimensions=True)

    print("Maximum relative difference values: ", diffinfo_systs['maxdiff_row'])
    print("Max. diff. central syst: ",fitinfo1['systs'][diffinfo_systs['maxind_row'][0]])
    print("Max. diff. up syst: ",fitinfo1['systs'][diffinfo_systs['maxind_row'][1]])
    print("Max. diff. down syst: ",fitinfo1['systs'][diffinfo_systs['maxind_row'][2]])

    if not(diffinfo_systs['large_inds'] is None):
        print( "Large differences observed: " )
        large_inds = diffinfo_systs['large_inds']

        #Divide the large indices into groups by column
        #Find the row (systematics) indices corresponding to the 
        #0th (central), 1st (positive) and 2nd (negative) columns
        systinds_central = large_inds[0][np.where(large_inds[1] == 0)]
        systinds_pos = large_inds[0][np.where(large_inds[1] == 1)]
        systinds_neg = large_inds[0][np.where(large_inds[1] == 2)]

        print("------")
        print( "Systematics with large diff. in central:" )
        for i in systinds_central:
            print( fitinfo1['systs'][i] )

        print("------")
        print( "Systematics with large diff. in pos:" )
        for i in systinds_pos:
            print( fitinfo1['systs'][i] )

        print("------")
        print( "Systematics with large diff. in neg:" )
        for i in systinds_neg:
            print( fitinfo1['systs'][i] )

    return

######################################################################################################

def CompareTRExFSystFile(fname1, fname2):

    sysinfo1 = ReadAndParseSysInfo(fname1)
    sysinfo2 = ReadAndParseSysInfo(fname2)

    if(sysinfo1['samples'] != sysinfo2['samples']):
        print("<ERROR>:: Mismatched sample lists")
        print("Sample list 1 :",sysinfo1['samples'])
        print("Sample list 2 :",sysinfo2['samples'])
        sys.exit()
        
    if(sysinfo1['systs'] != sysinfo2['systs']):
        print("<ERROR>:: Mismatched syst lists. Please check.")
        print("Sys list 1 :",sysinfo1['systs'])
        print("Sys list 2 :",sysinfo2['systs'])
        sys.exit()

    ### Check if identically zero elements are in the same positions in
    ### the two lists
    if not np.array_equal(sysinfo1['zeroinds'],sysinfo2['zeroinds']):
        print("<WARNING>:: Location of zero uncertainties differ")
        
        print("Systematics 1:")
        print(" Sys     |    Sample")
        for i in range(0, sysinfo1['zeroinds'].shape[1]):
            print( sysinfo1['systs'][sysinfo1['zeroinds'][0][i]], '  |   ',
                   sysinfo1['samples'][sysinfo1['zeroinds'][1][i]] )

        print("Systematics 2:")
        print(" Sys     |    Sample")
        for i in range(0, sysinfo2['zeroinds'].shape[1]):
            print( sysinfo2['systs'][sysinfo2['zeroinds'][0][i]], '  |   ',
                   sysinfo2['samples'][sysinfo2['zeroinds'][1][i]] )

    #### Check if differences above threshold for any values ####
    diffinfo_upvals = CompareTables(sysinfo1['upvals'], sysinfo2['upvals'], 
                                    threshold=0.1, dimensions=False)
    diffinfo_downvals = CompareTables(sysinfo1['downvals'], sysinfo2['downvals'], 
                                      threshold=0.1, dimensions=False)

    print("Maximum relative difference in up values: ", diffinfo_upvals['maxdiff'])
    print("Maximum relative difference in down values: ", diffinfo_downvals['maxdiff'])

    if not(diffinfo_upvals['large_inds'] is None):
        print( "Large differences in up variation observed: " )
        large_up = diffinfo_upvals['large_inds']
        for i in range(0, large_up.shape[1]):
            print( sysinfo2['systs'][large_up[0][i]], '  |   ',
                   sysinfo2['samples'][large_up[1][i]], ' >> ',
                   diffinfo_upvals["large_diffs"][i] )

    if not(diffinfo_downvals['large_inds'] is None):
        print( "Large differences in down variation observed: " )
        large_up = diffinfo_downvals['large_inds']
        for i in range(0, large_up.shape[1]):
            print( sysinfo2['systs'][large_up[0][i]], '  |   ',
                   sysinfo2['samples'][large_up[1][i]], ' >> ',
                   diffinfo_downvals["large_diffs"][i] )

    return

######################################################################################################

def main(args):

    parser = argparse.ArgumentParser()
    parser.add_argument("--baseDir",
                        help="If provided, taken as the base directory relative to \
                        which file paths will be found",
                        action="store", default="")
    parser.add_argument("--files",
                        help="Names of the two files to compare",
                        action="store", nargs=2, required=True)
    parser.add_argument("--fileType",
                        help="SYST for systematics tables, FIT for a TRExFitter fit file",
                        choices=["SYST","FIT"], required=True)

    arguments = parser.parse_args(args)

    #File names
    file1 = arguments.files[0]
    file2 = arguments.files[1]
    if(file1[0] != '/'):
        file1 = arguments.baseDir + file1
    if(file2[0] != '/'):
        file2 = arguments.baseDir + file2

    #Run comparison
    if(arguments.fileType == "SYST"):
        CompareTRExFSystFile(file1, file2)

    if(arguments.fileType == "FIT"):
        CompareTRExFFitFile(file1, file2)

    return 


######################################################################################################
if __name__ == '__main__':
   main(sys.argv[1:])

######################################################################################################
