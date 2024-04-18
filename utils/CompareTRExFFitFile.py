import numpy as np
import sys

############# Utility function to read fit file #######################
def ReadAndParseFitInfo(fname):

    infile = open(fname,'r')
    lines = infile.readlines()
    infile.close()

    p = re.compile('(^gamma)(?:(?!WTZt|WTHt|ZTZt|ZTHt).)*$')
    bkg_gamma_lines = list(filter(lambda x : not(p.search(x) is None), lines))

    print("Number of bkg gamma lines :",len(bkg_gamma_lines))

    split_bkg_lines = [ [e.strip for e in line.split()] for line in bkg_gamma_lines ]

    sysinfo = {}
    sysinfo['systs'] = np.array(split_bkg_lines)[:,0].tolist()
    sysinfo['values'] = np.array([ [float(e.strip()) for e in line[1:]] \
                                   for line in split_bkg_lines ])

    return sysinfo
        
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

def CompareTables(tab1, tab2, threshold=0.1):

    diffinfo = {}
    reldiff = np.fabs(np.divide(np.subtract(tab1,tab2),
                               tab1,where=(tab1 != 0.)))

    diffinfo['maxdiff'] = np.max(reldiff)
    diffinfo['large_ind'] = None
    if np.any(reldiff > threshold):
        diffinfo['large_ind'] = np.array(np.where(reldiff_up > threshold))

    return diffinfo

def CompareTRExFFitFile(fname1, fname2):


def CompareSysInfo(fname1, fname2):
###### Read the two files to compare and check consistency of format ##### 
#fname1 = 'SPT_MONOTOP_TCR_MONOTOP_scaled_M16K050BRW50_data_BONLY_syst_postFit.txt'
#fname2 = 'SPT_MONOTOP_TCR__BONLY_syst_postFit.txt'

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


    #### Now check if differences above threshold for any values ####
    diffinfo_up = CompareTables(sysinfo1['upvals'], sysinfo2['upvals'], threshold=0.1)
    diffinfo_down = CompareTables(sysinfo1['downvals'], sysinfo2['downvals'], threshold=0.1)

    print("Maximum relative difference in up values: ", diffinfo_up['maxdiff'])
    print("Maximum relative difference in down values: ", diffinfo_down['maxdiff'])

    if not(diffinfo_up['large_ind'] is None):
        print( "Large differences in up variation observed: " )
        large_up = diffinfo_up['large_ind']

        for i in range(0, large_up.shape[1]):
            print( sysinfo2['systs'][large_up[0][i]], '  |   ', 
                   sysinfo2['samples'][large_up[1][i]], ' >> ', 
                   reldiff_up[large_up[0][i]][large_up[1][i]] )

    if not(diffinfo_down['large_ind'] is None):
        print( "Large differences in up variation observed: " )
        large_down = diffinfo_down['large_ind']

        for i in range(0, large_down.shape[1]):
            print( sysinfo2['systs'][large_down[0][i]], '  |   ', 
                   sysinfo2['samples'][large_down[1][i]], ' >> ', 
                   reldiff_down[large_down[0][i]][large_down[1][i]] )
            

######################################################################################################
